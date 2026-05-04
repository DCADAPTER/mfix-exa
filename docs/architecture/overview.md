# Architecture Overview

## 1) MCP Server Module
- 역할: 시뮬레이션 입출력 파싱, 스키마 검증, 결과 요약 툴을 MCP tool로 노출.

## 2) LLM Agentic Dialogue Module
- 역할: 사용자 목표를 해석하고, 툴 호출 계획을 세우며 Harness와 상호작용.

## 3) Harness Engineering Module
- 역할: 시뮬레이션 실행 루프, 실패 복구, 메트릭 수집, 피드백 전달.

## 4) QLoRA Training Module
- 역할: 예제 입력/출력 + 도메인 문서 기반 instruction tuning 파이프라인 제공.

## 5) Data + Parser Module
- 역할: MFiX-EXA 입력 구조(JSON화), 출력 로그/필드 파일 해석.
