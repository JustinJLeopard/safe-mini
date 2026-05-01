"""Executor policy registry."""

from __future__ import annotations

from safe_mini.types import ExecutorPolicy

from .executor import AllowlistExecutor, BaseExecutor, ExecutorBase, OpenExecutor, SafeExecutor

ExecutorPolicies: dict[ExecutorPolicy, type[ExecutorBase]] = {
    ExecutorPolicy.OPEN: OpenExecutor,
    ExecutorPolicy.SAFE: SafeExecutor,
    ExecutorPolicy.ALLOWLIST: AllowlistExecutor,
}

__all__ = [
    "AllowlistExecutor",
    "BaseExecutor",
    "ExecutorBase",
    "ExecutorPolicies",
    "OpenExecutor",
    "SafeExecutor",
]
