# Simple Optimization Loop Example

목표 함수:
- `f(x) = (x - 3)^2`
- 전역 최적해: `x=3`, `f(x)=0`

`AgentRuntime.loop()`는 iteration마다 `x` 후보를 만들고,
`SimulationHarness`는 `python examples/simple_optimization/objective.py --x <value>`를 실행해 objective를 읽습니다.
