<div align="center">

# safe-mini

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#status)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**A safe-by-construction local-execution substrate for mini-swe-agent–style bash-action coding agents.**

Sandboxed boundary, generous capability inside. Designed to be auditable in one focused sitting.

</div>

---

## What this is

safe-mini is the load-bearing runtime substrate for [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)–style coding agents that decide one bash command at a time within a budget.

Multiple peer consumers depend on it:

| Consumer | Role |
|---|---|
| [JustAi](https://github.com/JustinJLeopard/justai-demo) | Project orchestrator — goal decomposition, chunk sizing, dashboards. |
| local-resident | Researcher harness — benchmark corpus + 54-trial calibration matrix. |

safe-mini is intentionally generic: it does not know about its consumers' domain models. Future projects can ship on top of the same substrate.

## What lives here

- **Runner loop** — prompt → one bash action → observation → repeat
- **Action protocol parsers** — fenced bash block, JSON action object
- **Executor policies** — `open` / `safe` / `allowlist` (and future variants)
- **Observation policies** — `full` / `tail` / `headtail` / `structured` / `structured+raw-tail`
- **Worktree provisioner** — fresh copy of repo per run, scoped HOME, sanitized PATH
- **Command/path guard** — configurable denylist + sensitive-path patterns
- **Incident artifact emission** — full transcript saved per run
- **Failure classifier** — 7-class taxonomy
- **Trajectory recording** — per-step timeline with phase markers
- **Ledger** — per-run cost/token/latency capture
- **Canonical types** — `Chunk`, `Budget`, `RunResult`, `FailureClass`, `ObservationPolicy`, `ExecutorPolicy`
- **AgentRunner Protocol** — the contract consumers depend on

## Failure taxonomy

| Class | Meaning |
|---|---|
| `safety-violation` | Agent attempted an action the executor policy denied. |
| `action-protocol-violation` | Output didn't parse as a valid action. |
| `exhausted-ideas` | Budget remained but the loop converged without progress. |
| `budget-exhausted` | Move or observation budget hit the cap. |
| `context-starvation` | Observations truncated below decision-relevant detail. |
| `reward-hacking` | Test passed by means unrelated to the requested change. |
| `embodiment-failure` | Action ran but didn't produce the expected world-state change. |

## Two-axis budget

Every run is bounded on TWO axes:

- **Move budget** — how many bash actions the agent can execute.
- **Observation budget** — how many characters of output the agent can read.

Both are enforced inside the runner. Either axis can independently fire `BUDGET_EXHAUSTED`.

## Installation

> **Note**: safe-mini is in alpha. Not yet on PyPI. Pinning options below.

### From git (Phase A — current)

```bash
pip install 'safe-mini @ git+https://github.com/JustinJLeopard/safe-mini.git@17c8514c1bf42d3064748400745099ca1723e782'
```

### From source (development)

```bash
git clone https://github.com/JustinJLeopard/safe-mini.git
cd safe-mini
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

pytest -q
ruff check safe_mini tests
mypy safe_mini
```

### From PyPI (Phase B — pending stabilization)

```bash
pip install safe-mini  # not yet published
```

## Status

**Current source state:** alpha (package metadata `0.1.0`). The reference
implementation from the pre-public 54-trial calibration study is preserved
under `reference/` for transparency. The production package under `safe_mini/`
now includes the concrete `SafeMiniRunner`, action parser, executor policies,
observation handling, worktree provisioning, and integration tests. The
injectable executor boundary supports explicit consumers such as JustAi.

This records source integration only. It is not package-install, live-model,
productive-runtime, or release evidence.

**Empirical baseline** (from the lab study, 6 task families × 9 configs × 54 trials):

- "Open" executor leaked a fake credential **6 / 6** probe runs while still solving the task.
- "Safe" executor blocked **6 / 6** probes and still solved **6 / 6** tasks.
- `reproduce_first` workflow: 2 steps avg vs 3 for `inspect_first`.
- `headtail` and structured observations beat pure `tail` on noisy output (tail dropped early failure clues).
- JSON and fenced-bash action protocols equivalent in deterministic tests; live-model malformed-action rate is the open question.

The lab study artifacts:

- `reference/lab_safe_mini_agent.py` — the original 270-line single-file agent loop
- `reference/lab_benchmark_tasks.py` — the 6-task corpus
- `reference/lab_benchmark_safe_mini.py` — the matrix-runner

The production runner components have been factored into this package. The
benchmark harness remains separate work for `local-resident`.

## Three-repo architecture

safe-mini is one of three repos:

```
        ┌─────────────────────────┐         ┌────────────────────────────┐
        │      JustAi             │         │      local-resident        │
        │  (orchestrator)         │         │  (researcher harness)      │
        └────────────┬────────────┘         └──────────────┬─────────────┘
                     │                                     │
                     └──────────────┬──────────────────────┘
                                    ▼
                            ┌──────────────┐
                            │  safe-mini   │
                            │ (this repo)  │
                            └──────────────┘
```

## Contributing

This is currently a personal-research-stage project. Issue reports and design discussions welcome via GitHub Issues. PRs accepted after issue-first design review for non-trivial changes.

## License

MIT — see [LICENSE](./LICENSE).
