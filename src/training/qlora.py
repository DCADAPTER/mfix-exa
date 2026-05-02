from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.common.config import Settings


def _validate_record(record: dict[str, Any], idx: int) -> None:
    if "messages" not in record or not isinstance(record["messages"], list):
        raise ValueError(f"Record {idx}: 'messages' list is required")


def _extract_assistant_target(messages: list[dict[str, str]]) -> tuple[str, str]:
    if not messages:
        raise ValueError("messages is empty")

    prompt_msgs = messages[:-1]
    target_msg = messages[-1]
    if target_msg.get("role") != "assistant":
        raise ValueError("last message must be assistant for supervised fine-tuning")

    prompt_lines: list[str] = []
    for msg in prompt_msgs:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        prompt_lines.append(f"[{role}]\n{content}")

    prompt = "\n\n".join(prompt_lines).strip()
    target = target_msg.get("content", "").strip()
    return prompt, target


def load_chatml_jsonl(path: str | Path) -> list[dict[str, str]]:
    """Load ChatML-like JSONL and convert to SFT prompt/response pairs."""
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            _validate_record(record, idx)
            prompt, target = _extract_assistant_target(record["messages"])
            rows.append({"prompt": prompt, "target": target})
    if not rows:
        raise ValueError("No training rows found in dataset")
    return rows


@dataclass
class QLoRATrainer:
    settings: Settings

    def train(
        self,
        train_jsonl: str,
        eval_jsonl: str | None = None,
        batch_size: int = 2,
        grad_accum: int = 8,
        num_epochs: int = 2,
        learning_rate: float = 2e-4,
        max_length: int = 2048,
    ) -> None:
        """Run QLoRA SFT training from ChatML JSONL data.

        Dependencies required at runtime:
        - transformers
        - datasets
        - peft
        - bitsandbytes
        - accelerate
        """
        from datasets import Dataset
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )

        train_rows = load_chatml_jsonl(train_jsonl)
        eval_rows = load_chatml_jsonl(eval_jsonl) if eval_jsonl else None

        tokenizer = AutoTokenizer.from_pretrained(self.settings.training.base_model, use_fast=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype="bfloat16",
        )

        model = AutoModelForCausalLM.from_pretrained(
            self.settings.training.base_model,
            quantization_config=bnb_config,
            device_map="auto",
        )
        model = prepare_model_for_kbit_training(model)

        lora_cfg = LoraConfig(
            r=self.settings.training.lora_r,
            lora_alpha=self.settings.training.lora_alpha,
            lora_dropout=self.settings.training.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "gate_proj"],
        )
        model = get_peft_model(model, lora_cfg)

        def to_text(sample: dict[str, str]) -> dict[str, str]:
            text = (
                "<|system|>\nYou are an MFIX-Exa simulation assistant.\n"
                f"<|user|>\n{sample['prompt']}\n"
                f"<|assistant|>\n{sample['target']}"
            )
            return {"text": text}

        train_ds = Dataset.from_list(train_rows).map(to_text)
        eval_ds = Dataset.from_list(eval_rows).map(to_text) if eval_rows else None

        def tokenize_fn(batch: dict[str, list[str]]) -> dict[str, Any]:
            return tokenizer(batch["text"], truncation=True, max_length=max_length)

        train_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=train_ds.column_names)
        eval_ds = (
            eval_ds.map(tokenize_fn, batched=True, remove_columns=eval_ds.column_names)
            if eval_ds is not None
            else None
        )

        args = TrainingArguments(
            output_dir=self.settings.training.output_dir,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum,
            learning_rate=learning_rate,
            num_train_epochs=num_epochs,
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="epoch" if eval_ds is not None else "no",
            bf16=True,
            report_to="none",
        )

        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=train_ds,
            eval_dataset=eval_ds,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        )
        trainer.train()
        trainer.save_model(self.settings.training.output_dir)
