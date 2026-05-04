"""Simulation harness for running filtered proposal cases.

Command to run:
    python -m src.agent.initial_ref_loop run \
        --config configs/settings.local.yaml \
        --initial-input "$(cat examples/initial_reference/initial_input.txt)" \
        --initial-error-log "$(cat examples/initial_reference/error_log.txt)"

Execution constraints:
    - `settings.harness.simulator_cmd` is split with `shlex.split`; a leading
      `cd <dir> && <command>` is converted into `subprocess.run(..., cwd=<dir>)`
      so the MFiX-EXA command can run without invoking a shell.
    - `settings.harness.launch_mode=tmux` launches the simulator in a detached
      tmux session. MFiX writes to a real pane for live viewing, while tmux
      captures pane output to a per-session log file.
    - `settings.harness.open_terminal=true` opens a GUI terminal attached to
      that tmux session before the simulator starts, when a terminal emulator is
      available. Python waits for the tmux session to finish before returning a
      final simulation result.
    - Tmux launch mode refuses to start a second session with the configured
      prefix while an earlier MFiX-EXA run is still active, to avoid competing
      for the same GPU memory.
    - For MFiX-EXA, this module infers the active stage input file from
      `simulator_cmd` and rewrites `param = value` entries before launching.
    - Parameter values are treated as text and written directly into the input
      file; caller-side filtering must ensure values are safe and physically
      valid.
    - Runs are bounded by `settings.harness.timeout_sec`; optional retry and
      backoff settings are read defensively when present on the harness config.

More TODO:
    - Add an explicit `stage_input_file` setting instead of relying on command
      inference.
    - Preserve exact whitespace for multi-value MFiX parameters more carefully.
    - Move objective parsing into simulator-specific parsers.
    - Capture run artifacts in per-case working directories.
    - Add unit coverage for input-file rewriting and timeout/retry behavior.
"""

from __future__ import annotations

import re
import shutil
import shlex
import subprocess
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from src.common.config import Settings

Plan: TypeAlias = str | Mapping[str, object]

_PARAM_RE = re.compile(r"([A-Za-z_][\w.\[\]-]*)\s*=\s*([^,;:\s]+)")


@dataclass
class SimulationHarness:
    settings: Settings

    def _normalize_plan(self, plan: Plan) -> tuple[str, dict[str, str]]:
        """Input: plan string or mapping. Output: stdin text and parsed parameter map."""
        if isinstance(plan, Mapping):
            params = {str(key): str(value) for key, value in plan.items()}
            return "\n".join(f"{key}={value}" for key, value in params.items()), params

        params = {key: value for key, value in _PARAM_RE.findall(plan)}
        return plan, params

    def _parse_objective(self, output: str) -> str:
        """Input: simulator output text. Output: parsed objective value or nan."""
        m = re.search(r"objective\s*=\s*([-+]?(?:\d*\.?\d+)(?:[eE][-+]?\d+)?)", output)
        return m.group(1) if m else "nan"

    def _clean_output(self, output: str | bytes | None) -> str:
        """Input: optional subprocess output. Output: stripped text."""
        if output is None:
            return ""
        if isinstance(output, bytes):
            return output.decode(errors="replace").strip()
        return output.strip()

    def _read_tail(self, path: Path, max_bytes: int = 20_000) -> str:
        """Input: text file path. Output: trailing text snippet."""
        if not path.exists():
            return ""
        with path.open("rb") as file:
            file.seek(0, 2)
            size = file.tell()
            file.seek(max(0, size - max_bytes))
            return file.read().decode(errors="replace")

    def _build_command(self) -> tuple[list[str], Path | None]:
        """Input: harness settings. Output: simulator argv and optional working directory."""
        tokens = shlex.split(self.settings.harness.simulator_cmd)
        if len(tokens) >= 4 and tokens[0] == "cd" and "&&" in tokens:
            separator = tokens.index("&&")
            if separator == 2:
                return tokens[separator + 1 :], Path(tokens[1])
        return tokens, None

    def _result_base(self, plan_text: str, attempt: int, stage_input_path: str | None) -> dict[str, str]:
        """Input: run metadata. Output: common result fields."""
        result = {
            "plan": plan_text,
            "simulator_cmd": self.settings.harness.simulator_cmd,
            "attempt": str(attempt),
        }
        if stage_input_path is not None:
            result["stage_input_file"] = stage_input_path
        return result

    def _add_plan_parameters(self, result: dict[str, str], params: Mapping[str, str]) -> None:
        """Input: result dict and plan parameters. Output: result augmented in place."""
        for key, value in params.items():
            result[f"param.{key}"] = value
            result.setdefault(key, value)

    def _infer_stage_input_path(self) -> Path | None:
        """Input: harness settings. Output: inferred MFiX-EXA input file path, if any."""
        simulator_cmd = self.settings.harness.simulator_cmd
        if "mfix" not in simulator_cmd.lower():
            return None

        cmd, cwd = self._build_command()
        if not cmd:
            return None

        base_dir = cwd or Path(self.settings.harness.work_dir)

        input_arg: str | None = None
        if "-f" in cmd:
            index = cmd.index("-f")
            if index + 1 < len(cmd):
                input_arg = cmd[index + 1]
        else:
            input_arg = cmd[-1]

        if not input_arg or input_arg.startswith("-") or input_arg in {"&&", ";"}:
            return None

        path = Path(input_arg)
        return path if path.is_absolute() else base_dir / path

    def _update_stage_input(self, params: Mapping[str, str]) -> str | None:
        """Input: plan parameters. Output: updated input path, if an MFiX file was updated."""
        if not params:
            return None

        input_path = self._infer_stage_input_path()
        if input_path is None or not input_path.is_file():
            return None

        replacements = dict(params)
        line_re = re.compile(r"^(\s*([A-Za-z_][\w.\[\]-]*)\s*=\s*)(.*?)(\s*(?:#.*)?)$")
        lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
        updated_keys: set[str] = set()

        for index, line in enumerate(lines):
            newline = "\n" if line.endswith("\n") else ""
            body = line[:-1] if newline else line
            match = line_re.match(body)
            if match is None:
                continue
            key = match.group(2)
            value = replacements.get(key)
            if value is None:
                continue
            lines[index] = f"{match.group(1)}{value}{match.group(4)}{newline}"
            updated_keys.add(key)

        for key, value in replacements.items():
            if key not in updated_keys:
                lines.append(f"{key} = {value}\n")

        input_path.write_text("".join(lines), encoding="utf-8")
        return str(input_path)

    def _active_tmux_sessions(self, session_prefix: str) -> list[str]:
        """Input: tmux session prefix. Output: active matching session names."""
        cp = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if cp.returncode != 0:
            if "no server running" in cp.stderr.lower():
                return []
            raise OSError(cp.stderr.strip() or "tmux list-sessions failed")
        return [
            name
            for name in cp.stdout.splitlines()
            if name == session_prefix or name.startswith(f"{session_prefix}_")
        ]

    def _terminal_argv(self, session_name: str) -> list[str] | None:
        """Input: tmux session name. Output: GUI terminal argv, if available."""
        configured = getattr(self.settings.harness, "terminal_cmd", None)
        if configured:
            base = shlex.split(configured)
            if "{session}" in configured:
                return [part.format(session=session_name) for part in base]
            executable = base[0]
        else:
            executable = next(
                (
                    candidate
                    for candidate in (
                        "x-terminal-emulator",
                        "gnome-terminal",
                        "xfce4-terminal",
                        "konsole",
                        "xterm",
                    )
                    if shutil.which(candidate)
                ),
                "",
            )
            if not executable:
                return None
            base = [executable]

        name = Path(executable).name
        attach = ["tmux", "attach-session", "-t", session_name]
        if name == "gnome-terminal":
            return [*base, "--", *attach]
        return [*base, "-e", *attach]

    def _open_tmux_terminal(self, session_name: str) -> tuple[str | None, str | None]:
        """Input: tmux session name. Output: terminal command text and optional error."""
        if not getattr(self.settings.harness, "open_terminal", False):
            return None, None

        argv = self._terminal_argv(session_name)
        if argv is None:
            return None, "no supported terminal emulator found"

        command_text = " ".join(shlex.quote(part) for part in argv)
        try:
            subprocess.Popen(
                argv,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            return command_text, str(exc)
        return command_text, None

    def _tmux_session_exists(self, session_name: str) -> bool:
        """Input: tmux session name. Output: whether the session still exists."""
        cp = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return cp.returncode == 0

    def _wait_for_tmux_exit(self, session_name: str, timeout_sec: int) -> str:
        """Input: tmux session + timeout. Output: finished or timeout."""
        deadline = time.monotonic() + max(0, timeout_sec)
        while self._tmux_session_exists(session_name):
            if time.monotonic() >= deadline:
                subprocess.run(
                    ["tmux", "kill-session", "-t", session_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return "timeout"
            time.sleep(1.0)
        return "finished"

    def _run_tmux(self, cmd: list[str], cwd: Path | None, plan_text: str, stage_input_path: str | None) -> dict[str, str]:
        """Input: simulator argv/cwd. Output: tmux launch result dict."""
        work_dir = cwd or Path.cwd()
        session_prefix = getattr(self.settings.harness, "tmux_session_prefix", "mfix")
        session_name = re.sub(r"[^A-Za-z0-9_.-]", "_", f"{session_prefix}_{time.time_ns()}")
        log_path = work_dir / f"{session_name}.log"
        start_path = work_dir / f".{session_name}.start"
        status_path = work_dir / f".{session_name}.status"
        log_path.touch()
        command_text = " ".join(shlex.quote(part) for part in cmd)
        start_text = shlex.quote(str(start_path))
        status_text = shlex.quote(str(status_path))
        script = (
            f"while [ ! -f {start_text} ]; do sleep 0.05; done; "
            f"rm -f {start_text}; "
            f"{command_text}; "
            "status=$?; "
            "echo \"[mfix-agent] mpirun exited with status ${status}\"; "
            f"printf '%s' \"${{status}}\" > {status_text}; "
            "exit ${status}"
        )
        tmux_cmd = [
            "tmux",
            "new-session",
            "-d",
            "-s",
            session_name,
            "-c",
            str(work_dir),
            f"bash -lc {shlex.quote(script)}",
        ]
        terminal_cmd_text: str | None = None
        terminal_error: str | None = None

        try:
            cp = subprocess.run(
                tmux_cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if cp.returncode == 0:
                pipe_cp = subprocess.run(
                    [
                        "tmux",
                        "pipe-pane",
                        "-o",
                        "-t",
                        session_name,
                        f"cat >> {shlex.quote(str(log_path))}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if pipe_cp.returncode != 0:
                    subprocess.run(
                        ["tmux", "kill-session", "-t", session_name],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    cp = pipe_cp
                else:
                    terminal_cmd_text, terminal_error = self._open_tmux_terminal(session_name)
                    start_path.touch()
                    wait_status = self._wait_for_tmux_exit(
                        session_name,
                        self.settings.harness.timeout_sec,
                    )
                    if wait_status == "timeout":
                        result = self._result_base(plan_text, 1, stage_input_path)
                        result.update(
                            {
                                "status": "timeout",
                                "returncode": "",
                                "objective": "nan",
                                "stdout": self._read_tail(log_path),
                                "stderr": "tmux session timed out and was killed",
                                "tmux_session": session_name,
                                "tmux_log": str(log_path),
                            }
                        )
                        if terminal_cmd_text is not None:
                            result["terminal_cmd"] = terminal_cmd_text
                        if terminal_error is not None:
                            result["terminal_error"] = terminal_error
                        return result
        except (OSError, subprocess.TimeoutExpired) as exc:
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            start_path.unlink(missing_ok=True)
            result = self._result_base(plan_text, 1, stage_input_path)
            result.update(
                {
                    "status": "error",
                    "returncode": "",
                    "objective": "nan",
                    "stdout": "",
                    "stderr": self._clean_output(getattr(exc, "stderr", None)) or str(exc),
                }
            )
            return result

        stdout = cp.stdout.strip()
        stderr = cp.stderr.strip()
        log_output = self._read_tail(log_path)
        returncode = status_path.read_text(encoding="utf-8", errors="replace").strip() if status_path.exists() else ""
        result = self._result_base(plan_text, 1, stage_input_path)
        result.update(
            {
                "status": "ok" if cp.returncode == 0 and returncode == "0" else "error",
                "returncode": returncode or str(cp.returncode),
                "objective": self._parse_objective(log_output),
                "stdout": stdout,
                "stderr": stderr,
                "tmux_session": session_name,
                "tmux_log": str(log_path),
                "log_tail": log_output,
            }
        )
        status_path.unlink(missing_ok=True)
        if terminal_cmd_text is not None:
            result["terminal_cmd"] = terminal_cmd_text
        if terminal_error is not None:
            result["terminal_error"] = terminal_error
        return result

    def run_once(self, plan: Plan) -> dict[str, str]:
        """Input: plan string or mapping. Output: execution result dict."""
        plan_text, params = self._normalize_plan(plan)
        cmd, cwd = self._build_command()
        launch_mode = getattr(self.settings.harness, "launch_mode", "capture")
        if launch_mode == "tmux":
            session_prefix = getattr(self.settings.harness, "tmux_session_prefix", "mfix")
            try:
                active_sessions = self._active_tmux_sessions(session_prefix)
            except (OSError, subprocess.TimeoutExpired) as exc:
                result = self._result_base(plan_text, 1, None)
                result.update(
                    {
                        "status": "error",
                        "returncode": "",
                        "objective": "nan",
                        "stdout": "",
                        "stderr": str(exc),
                    }
                )
                self._add_plan_parameters(result, params)
                return result
            if active_sessions:
                terminal_cmd_text, terminal_error = self._open_tmux_terminal(active_sessions[0])
                result = self._result_base(plan_text, 1, None)
                result.update(
                    {
                        "status": "busy",
                        "returncode": "",
                        "objective": "nan",
                        "stdout": "",
                        "stderr": "active tmux session already running",
                        "tmux_session": active_sessions[0],
                    }
                )
                if terminal_cmd_text is not None:
                    result["terminal_cmd"] = terminal_cmd_text
                if terminal_error is not None:
                    result["terminal_error"] = terminal_error
                self._add_plan_parameters(result, params)
                return result

            stage_input_path = self._update_stage_input(params)
            result = self._run_tmux(cmd, cwd, plan_text, stage_input_path)
            self._add_plan_parameters(result, params)
            return result

        stage_input_path = self._update_stage_input(params)
        retries = max(0, int(getattr(self.settings.harness, "retries", 0)))
        backoff_sec = max(0.0, float(getattr(self.settings.harness, "backoff_sec", 0.0)))
        attempts = retries + 1
        last_result: dict[str, str] | None = None

        for attempt in range(1, attempts + 1):
            try:
                cp = subprocess.run(
                    cmd,
                    input=plan_text,
                    capture_output=True,
                    text=True,
                    timeout=self.settings.harness.timeout_sec,
                    cwd=str(cwd) if cwd is not None else None,
                )
                stdout = cp.stdout.strip()
                stderr = cp.stderr.strip()
                combined_output = "\n".join(part for part in (stdout, stderr) if part)
                last_result = {
                    "status": "ok" if cp.returncode == 0 else "error",
                    "plan": plan_text,
                    "simulator_cmd": self.settings.harness.simulator_cmd,
                    "returncode": str(cp.returncode),
                    "attempt": str(attempt),
                    "objective": self._parse_objective(combined_output),
                    "stdout": stdout,
                    "stderr": stderr,
                }
                if stage_input_path is not None:
                    last_result["stage_input_file"] = stage_input_path
                self._add_plan_parameters(last_result, params)
                if cp.returncode == 0:
                    return last_result
            except subprocess.TimeoutExpired as exc:
                stdout = self._clean_output(exc.stdout)
                stderr = self._clean_output(exc.stderr)
                combined_output = "\n".join(part for part in (stdout, stderr) if part)
                last_result = {
                    "status": "timeout",
                    "plan": plan_text,
                    "simulator_cmd": self.settings.harness.simulator_cmd,
                    "returncode": "",
                    "attempt": str(attempt),
                    "objective": self._parse_objective(combined_output),
                    "stdout": stdout,
                    "stderr": stderr,
                }
                if stage_input_path is not None:
                    last_result["stage_input_file"] = stage_input_path
                self._add_plan_parameters(last_result, params)
            except (OSError, ValueError) as exc:
                last_result = {
                    "status": "error",
                    "plan": plan_text,
                    "simulator_cmd": self.settings.harness.simulator_cmd,
                    "returncode": "",
                    "attempt": str(attempt),
                    "objective": "nan",
                    "stdout": "",
                    "stderr": str(exc),
                }
                if stage_input_path is not None:
                    last_result["stage_input_file"] = stage_input_path
                self._add_plan_parameters(last_result, params)
                break

            if attempt < attempts and backoff_sec:
                time.sleep(backoff_sec * attempt)

        if last_result is None:
            last_result = {
                "status": "error",
                "plan": plan_text,
                "simulator_cmd": self.settings.harness.simulator_cmd,
                "returncode": "",
                "attempt": "0",
                "objective": "nan",
                "stdout": "",
                "stderr": "",
            }
            self._add_plan_parameters(last_result, params)
        return last_result
