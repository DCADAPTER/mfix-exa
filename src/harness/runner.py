from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from src.common.config import Settings


@dataclass
class SimulationHarness:
    settings: Settings

    def _extract_x(self, plan: str) -> float | None:
        m = re.search(r"x\s*=\s*([-+]?\d*\.?\d+)", plan)
        return float(m.group(1)) if m else None

    def run_once(self, plan: str) -> dict[str, str]:
        x = self._extract_x(plan)
        if x is not None and "examples/simple_optimization/objective.py" in self.settings.harness.simulator_cmd:
            cmd = self.settings.harness.simulator_cmd.split() + ["--x", str(x)]
            cp = subprocess.run(cmd, capture_output=True, text=True, timeout=self.settings.harness.timeout_sec)
            out = cp.stdout.strip()
            m = re.search(r"objective=([-+]?\d*\.?\d+)", out)
            objective = m.group(1) if m else "nan"
            return {
                "status": "ok" if cp.returncode == 0 else "error",
                "plan": plan,
                "x": f"{x}",
                "objective": objective,
                "stdout": out,
            }

        return {
            "status": "stubbed",
            "plan": plan,
            "simulator_cmd": self.settings.harness.simulator_cmd,
        }


# TODO(core):
# - define production-grade implementation tasks for this module.
# - keep this section updated as features are implemented.
