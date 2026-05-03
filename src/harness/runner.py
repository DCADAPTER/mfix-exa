from dataclasses import dataclass

from src.common.config import Settings


@dataclass
class SimulationHarness:
    settings: Settings

    def run_once(self, plan: str) -> dict[str, str]:
        # TODO: subprocess 실행 + 결과 파싱 + 실패 복구 로직 연결
        return {
            "status": "stubbed",
            "plan": plan,
            "simulator_cmd": self.settings.harness.simulator_cmd,
        }
