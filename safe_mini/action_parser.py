"""Action protocol parsing for safe-mini runner loops."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ActionFormat(StrEnum):
    """Supported one-action response protocols."""

    FENCED_BASH = "fenced-bash"
    JSON = "json"


@dataclass(frozen=True)
class ParsedAction:
    """A parsed shell action plus the protocol format that produced it."""

    command: str
    format: ActionFormat


class ActionParseError(ValueError):
    """Raised when a model response does not contain exactly one valid action."""


def parse_action(text: str) -> ParsedAction:
    """Parse a model response into one shell command.

    Supported forms:
    - A single fenced block labeled ``bash-action``.
    - A JSON object with ``{"action": "bash", "command": "..."}``.
    """

    stripped = text.strip()
    if stripped.startswith("{"):
        return _parse_json_action(stripped)
    return _parse_fenced_bash(stripped)


def _parse_fenced_bash(text: str) -> ParsedAction:
    matches = re.findall(r"```bash-action\s*\n(.*?)\n```", text, re.DOTALL)
    if len(matches) != 1:
        raise ActionParseError(f"expected exactly one bash-action, found {len(matches)}")
    command = matches[0].strip()
    if not command:
        raise ActionParseError("bash-action command cannot be empty")
    return ParsedAction(command=command, format=ActionFormat.FENCED_BASH)


def _parse_json_action(text: str) -> ParsedAction:
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ActionParseError(f"invalid JSON action: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ActionParseError("JSON action must be an object")
    if payload.get("action") != "bash":
        raise ActionParseError("JSON action must set action='bash'")

    command = payload.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ActionParseError("JSON action command must be a non-empty string")
    return ParsedAction(command=command.strip(), format=ActionFormat.JSON)
