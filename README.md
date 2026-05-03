# MFiX-EXA Agentic Simulation Platform (Skeleton)

이 저장소는 **MFiX-EXA 시뮬레이션 및 피드백 자동화**를 목표로 하는 AI-agent 기반 프로젝트의 스켈레톤입니다.

## 포함 모듈

- MCP 서버 구현 모듈
- LLM agentic 대화/오케스트레이션 모듈
- 하네스 엔지니어링(실험 실행/검증/피드백 루프) 모듈
- QLoRA 기반 학습(파인튜닝) 모듈
- MFiX-EXA 입력/출력 파서 및 데이터셋 모듈

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# 예시 설정 파일 생성
cp configs/settings.example.yaml configs/settings.local.yaml

# MCP 서버 실행
python -m src.mcp_server.main --config configs/settings.local.yaml

# 에이전트 루프 실행
python -m src.agent.runtime --config configs/settings.local.yaml
```

## 디렉터리 구조

```text
.
├── configs/
├── docs/
├── scripts/
├── src/
│   ├── agent/
│   ├── harness/
│   ├── mcp_server/
│   ├── mfiexa/
│   ├── training/
│   └── common/
├── tests/
└── pyproject.toml
```

## 설계 원칙

1. **모듈 경계 명확화**: MCP, Agent, Harness, Training 책임 분리.
2. **재현성**: 설정 파일 + 실행 로그 + 아티팩트 관리.
3. **확장성**: 새 시뮬레이터/LLM/학습 파이프라인 플러그인화.
4. **검증 가능성**: 하네스 레벨 유닛/통합 테스트 우선.

## 향후 구현 TODO

- MFiX-EXA 입출력 정적 스키마 검증기 고도화
- 출력 파일 해석용 MCP tools 구현 확장
- QLoRA 학습용 데이터 큐레이션 파이프라인 구체화
- 자동 하이퍼파라미터 탐색 루프(Agent↔Harness) 연결


## 학습된 모델 채팅 실행

```bash
# 학습 결과(LoRA adapter)가 settings의 training.output_dir에 있다고 가정
python -m src.agent.chat run --config configs/settings.local.yaml

# 또는 어댑터 경로를 명시
python -m src.agent.chat run --config configs/settings.local.yaml --adapter-path ./artifacts/qlora
```


## QLoRA 단계별(순차) 학습

- 처음부터 학습: `resume_adapter_path=None` (기본값)
- 기존 어댑터 이어학습: `resume_adapter_path="./artifacts/qlora_stage1"`

예시:

```python
from src.common.config import load_settings
from src.training.qlora import QLoRATrainer

settings = load_settings("configs/settings.local.yaml")
trainer = QLoRATrainer(settings)

# 1단계: 1.jsonl로 초기 학습
trainer.train(train_jsonl="1.jsonl", eval_jsonl=None)

# 2단계: 1단계 어댑터를 불러와 2.jsonl로 추가 학습
trainer.train(
    train_jsonl="2.jsonl",
    eval_jsonl=None,
    resume_adapter_path="./artifacts/qlora"
)
```


## 반복 루프 실험용 커맨드

```bash
# 1) 정책 주입 + 로컬 채팅 루프
python -m src.agent.chat run   --config configs/settings.local.yaml   --adapter-path ./artifacts/qlora   --instruction-path policies/AGENT_POLICY.md   --memory-turns 8

# 2) 하네스 반복 루프(에이전트 서비스 루프)
python -m src.agent.runtime run --config configs/settings.local.yaml
```


## Agent Loop 실행 파일

```bash
python -m src.agent.Agent_loop_execution run --config configs/settings.local.yaml

# iteration override
python -m src.agent.Agent_loop_execution run --config configs/settings.local.yaml --max-iterations 12
```
