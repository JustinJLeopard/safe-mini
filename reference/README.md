# Reference implementation (v0)

These files are the original lab artifacts from `~/projects/mini-swe-agent-study-2026-04-29/lab/` (Justin's pre-public 54-trial calibration study). They are preserved here as the reference implementation against which the production `safe_mini/` package is being adapted.

- `lab_safe_mini_agent.py` — the original 270-line single-file agent loop with `SafeExecutor`, `ScriptedModel`, `Observation`, `RunResult`, `parse_action`, `fresh_repo`, `final_tests_pass`, `run_case`, `main`.
- `lab_benchmark_tasks.py` — the 6-task corpus.
- `lab_benchmark_safe_mini.py` — the matrix-runner that drove 54 trials (6 tasks × 9 configs).

The production package (`safe_mini/`) factors these into:
- `safe_mini/types.py` — Observation, RunResult, Chunk, Budget, FailureClass, ObservationPolicy, ExecutorPolicy
- `safe_mini/protocol.py` — AgentRunner Protocol contract
- `safe_mini/runner.py` — concrete SafeMiniRunner (port of run_case + main loop)
- `safe_mini/policies/` — executor policies (open / safe / allowlist)
- `safe_mini/observation/` — observation policies (full / tail / headtail / structured)
- `safe_mini/classifier.py` — failure classifier (7-class taxonomy)

The benchmark harness moves to the `local-resident` repo (per the 3-repo plan), since safe-mini stays generic-substrate-only.
