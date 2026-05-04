from __future__ import annotations

from pathlib import Path

import typer

from src.agent.memory import SlidingWindowMemory
from src.agent.policy import load_instruction_file, merge_system_instruction
from src.common.config import load_settings

cli = typer.Typer()


def build_prompt(
    user_text: str,
    system_text: str | None = None,
    memory_text: str | None = None,
) -> str:
    system = system_text or "You are an MFIX-Exa simulation assistant."
    history = f"\n<memory>\n{memory_text}\n</memory>\n" if memory_text else ""
    return f"<|system|>\n{system}{history}\n<|user|>\n{user_text}\n<|assistant|>\n"


@cli.command()
def run(
    config: str = typer.Option(..., "--config", help="Path to settings YAML/JSON"),
    adapter_path: str | None = typer.Option(None, "--adapter-path"),
    instruction_path: str | None = typer.Option(None, "--instruction-path"),
    max_new_tokens: int = typer.Option(512, "--max-new-tokens"),
    temperature: float = typer.Option(0.2, "--temperature"),
    top_p: float = typer.Option(0.95, "--top-p"),
    memory_turns: int = typer.Option(8, "--memory-turns"),
) -> None:
    """Load base model + LoRA adapter and start an interactive chat loop."""
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    settings = load_settings(config)
    base_model_name = settings.training.base_model
    lora_path = adapter_path or settings.training.output_dir

    base_system = "You are an MFIX-Exa simulation assistant. Keep outputs practical and concise."
    extra_policy = load_instruction_file(instruction_path)
    merged_system = merge_system_instruction(base_system, extra_policy)

    tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(base_model_name, device_map="auto")

    if not Path(lora_path).exists():
        raise FileNotFoundError(
            f"LoRA adapter path not found: {lora_path}. "
            "Run training first or pass --adapter-path explicitly."
        )
    model = PeftModel.from_pretrained(base_model, lora_path)
    model.eval()

    memory = SlidingWindowMemory(max_turns=memory_turns)
    print("[chat] model loaded. type '/exit' to quit.")
    while True:
        user_text = input("user> ").strip()
        if user_text in {"/exit", "exit", "quit"}:
            print("[chat] bye")
            break
        if not user_text:
            continue

        memory.add("user", user_text)
        prompt = build_prompt(user_text, system_text=merged_system, memory_text=memory.to_text())
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0,
            temperature=temperature,
            top_p=top_p,
            pad_token_id=tokenizer.eos_token_id,
        )
        generated = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        reply = generated.split("<|assistant|>")[-1].strip() if "<|assistant|>" in generated else generated
        memory.add("assistant", reply)
        print(f"assistant> {reply}")


@cli.command("version")
def version() -> None:
    """Show chat CLI version info."""
    print("mfix-exa chat cli")


if __name__ == "__main__":
    cli()
