"""Canonical types for the safe-mini substrate.

These types are the contract shared between safe-mini and its consumers
(JustAi, local-resident, future projects). They are intentionally minimal
and intentionally NOT consumer-domain-aware.

TODO(port): full port of dataclasses + enums from
    reference/lab_safe_mini_agent.py
plus extension to the canonical names below per
memory key safe-mini-substrate-architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

# --- Failure taxonomy --------------------------------------------------------


class FailureClass(StrEnum):
    """The 7-class failure taxonomy. Determines how the planner re-decomposes."""

    SAFETY_VIOLATION = "safety-violation"
    ACTION_PROTOCOL_VIOLATION = "action-protocol-violation"
    EXHAUSTED_IDEAS = "exhausted-ideas"
    BUDGET_EXHAUSTED = "budget-exhausted"
    CONTEXT_STARVATION = "context-starvation"
    REWARD_HACKING = "reward-hacking"
    EMBODIMENT_FAILURE = "embodiment-failure"


# --- Policy enums ------------------------------------------------------------


class ExecutorPolicy(StrEnum):
    OPEN = "open"
    SAFE = "safe"
    ALLOWLIST = "allowlist"


class ObservationPolicy(StrEnum):
    FULL = "full"
    TAIL = "tail"
    HEADTAIL = "headtail"
    STRUCTURED = "structured"
    STRUCTURED_RAW_TAIL = "structured+raw-tail"


# --- Move + observation budget ----------------------------------------------


@dataclass
class Budget:
    """Two-axis budget: bash-action moves AND observation char count.

    Both budgets are enforced inside the runner. A run can fail with
    BUDGET_EXHAUSTED on either axis.
    """

    move_budget: int
    observation_budget: int


# --- Work unit + result ------------------------------------------------------


@dataclass
class Chunk:
    """A goal-decomposed work unit fitted to a bash-action loop's budget."""

    id: str
    description: str
    success_criteria: str
    budget: Budget


@dataclass
class Observation:
    """One bash action's result. Mirrors reference/lab_safe_mini_agent.py."""

    command: str
    output: str
    returncode: int
    blocked: bool = False


@dataclass
class RunResult:
    """Per-chunk execution result. Includes trajectory for replay/audit."""

    label: str
    success: bool
    leaked_secret: bool
    blocked_commands: int
    steps: int
    elapsed_sec: float
    final_tests_pass: bool
    transcript: list[dict] = field(default_factory=list)
    failure_class: FailureClass | None = None


# --- TODO during port from reference/ ---------------------------------------
# - extend Chunk / RunResult with the fields the JustAi orchestrator already
#   relies on (action_type, file_touched per step, etc.) — see
#   ~/projects/JustAi-verify-2026-04-30/justai/runner_protocol.py for the
#   stub that this module will eventually replace.
