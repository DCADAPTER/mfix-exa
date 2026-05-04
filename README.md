# MFiX-EXA Agentic Loop (Core Only)

핵심 모듈만 남긴 경량 구조입니다.

## Core modules
- `src/common/config.py`: 설정 로더
- `src/harness/runner.py`: 시뮬레이션 실행 하네스
- `src/agentic_loop/analyzer/agent.py`: 에러 로그/입력 기반 insight
- `src/agentic_loop/proposer/agent.py`: 파라미터 케이스 제안
- `src/agentic_loop/filtering/active_learning.py`: 케이스 필터
- `src/agentic_loop/simulation/executor.py`: 선택 케이스 실행
- `src/agentic_loop/orchestrator/loop.py`: 루프 오케스트레이션
- `src/agent/initial_ref_loop.py`: 실행 CLI

## Run
```bash
python -m src.agent.initial_ref_loop run \
  --config examples/simple_optimization/settings.local.yaml \
  --initial-input "$(cat examples/initial_reference/initial_input.txt)" \
  --initial-error-log "$(cat examples/initial_reference/error_log.txt)" \
  --analyzer-model analyzer-mini \
  --proposer-model proposer-mini
```


## TODO

- 상세 구현 TODO: `docs/TODO_CORE.md`
