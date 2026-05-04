# Core Module TODO

## 1) `src/common/config.py`
- [ ] 환경별 config overlay(`base + local + env var`) 지원
- [ ] strict schema versioning (`config_version`) 추가
- [ ] 민감정보(secret) 로딩 정책 분리

## 2) `src/harness/runner.py`
- [ ] subprocess 실행 상태코드/표준에러 상세 수집
- [ ] timeout/retry/backoff 정책 구현
- [ ] 실제 MFiX-EXA 실행 파이프라인과 objective parser 분리

## 3) `src/agentic_loop/analyzer/agent.py`
- [ ] analyzer 전용 LLM provider 연동
- [ ] 에러 유형 taxonomy 기반 원인 분류기 추가
- [ ] RAG retrieval 결과를 evidence로 구조화

## 4) `src/agentic_loop/proposer/agent.py`
- [ ] proposer 전용 LLM provider 연동
- [ ] 다중 후보 생성 시 diversity/novelty 제약 추가
- [ ] proposal schema 검증(JSON schema) 추가

## 5) `src/agentic_loop/filtering/active_learning.py`
- [ ] uncertainty sampling 구현
- [ ] diversity-aware selection (e.g., k-center)
- [ ] safety constraints (range + physical validity)

## 6) `src/agentic_loop/simulation/executor.py`
- [ ] 비동기 실행 큐 / 병렬 case 실행
- [ ] 실행 로그 아티팩트 저장 경로 표준화
- [ ] 실패 케이스 재실행 정책

## 7) `src/agentic_loop/orchestrator/loop.py`
- [ ] 다회 iteration 상태 저장(JSONL)
- [ ] best-case selection + rollback 정책
- [ ] Active Learning feedback metric 연결

## 8) `src/agent/initial_ref_loop.py`
- [ ] initial reference 파일 입력 모드(`--initial-input-file`) 지원
- [ ] 반복 실행 모드(`--iterations`) 지원
- [ ] run summary 리포트 출력(JSON)
