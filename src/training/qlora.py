from dataclasses import dataclass

from src.common.config import Settings


@dataclass
class QLoRATrainer:
    settings: Settings

    def train(self) -> None:
        # TODO: peft/bitsandbytes/transformers 학습 파이프라인 연결
        print(
            "[training] starting qlora with",
            self.settings.training.base_model,
            "->",
            self.settings.training.output_dir,
        )
