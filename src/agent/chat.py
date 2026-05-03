from __future__ import annotations

from pathlib import Path

import typer

from src.common.config import load_settings

cli = typer.Typer()


def build_prompt(user_text: str, system_text: str | None = None) -> str:
    system = system_text or "You are an MFIX-Exa simulation assistant."
    return f"<|system|>\n{system}\n<|user|>\n{user_text}\n<|assistant|>\n"


@cli.command()
def run(
    config: str = typer.Option(..., "--config", help="Path to settings YAML/JSON"),
    adapter_path: str | None = typer.Option(None, "--adapter-path"),
    max_new_tokens: int = typer.Option(512, "--max-new-tokens"),
    temperature: float = typer.Option(0.2, "--temperature"),
    top_p: float = typer.Option(0.95, "--top-p"),
) -> None:
    """Load base model + LoRA adapter and start an interactive chat loop."""
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    settings = load_settings(config)
    base_model_name = settings.training.base_model
    lora_path = adapter_path or settings.training.output_dir

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

    print("[chat] model loaded. type '/exit' to quit.")
    while True:
        user_text = input("user> ").strip()
        if user_text in {"/exit", "exit", "quit"}:
            print("[chat] bye")
            break
        if not user_text:
            continue

        prompt = build_prompt(user_text)
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

        # Print only assistant continuation when possible
        assistant_prefix = prompt.replace("<|system|>\n", "").replace("<|user|>\n", "")
        if generated.startswith(assistant_prefix):
            reply = generated[len(assistant_prefix) :].strip()
        else:
            reply = generated.strip()
        print(f"assistant> {reply}")


@cli.command("version")
def version() -> None:
    """Show chat CLI version info."""
    print("mfix-exa chat cli")


if __name__ == "__main__":
    cli()
