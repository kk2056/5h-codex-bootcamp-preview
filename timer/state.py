"""Local-only state helpers shared by the timer page server and CLI."""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = PRODUCT_ROOT / "progress" / "progress.json"
INSTANCE_ID = sha256(str(STATE_PATH.resolve()).encode("utf-8")).hexdigest()[:16]
ALLOWANCE_SECONDS = 5 * 60 * 60
LEVEL_IDS = ("01", "02", "03", "04", "05")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _default_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "course_id": "5h-codex-bootcamp",
        "course_title": "5H CODEX BOOTCAMP",
        "allowance_seconds": ALLOWANCE_SECONDS,
        "used_seconds": 0.0,
        "running": False,
        "running_since": None,
        "course_status": "not_started",
        "current_level_id": "01",
        "completed_level_ids": [],
        "weak_points": [],
        "updated_at": _now_iso(),
    }


def _write(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix="progress-", suffix=".json", dir=STATE_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(tmp_name, STATE_PATH)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _read_raw() -> dict[str, Any]:
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if not isinstance(state, dict) or state.get("schema_version") != 1:
            raise ValueError("Unsupported progress file format")
        return {**_default_state(), **state}
    except FileNotFoundError:
        state = _default_state()
        _write(state)
        return state
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Could not read course progress: {exc}") from exc


def _checkpoint(state: dict[str, Any], now: float | None = None) -> dict[str, Any]:
    now = now if now is not None else time.time()
    result = dict(state)
    used = max(0.0, float(result.get("used_seconds", 0)))
    allowance = max(0, int(result.get("allowance_seconds", ALLOWANCE_SECONDS)))
    if result.get("running") and result.get("running_since") is not None:
        try:
            used += max(0.0, now - float(result["running_since"]))
        except (TypeError, ValueError):
            pass
    used = min(used, allowance)
    result["used_seconds"] = used
    result["allowance_seconds"] = allowance
    if used >= allowance:
        result["running"] = False
        result["running_since"] = None
        result["course_status"] = "time_used"
    return result


def get_state() -> dict[str, Any]:
    now = time.time()
    state = _checkpoint(_read_raw(), now)
    if state.get("running"):
        # Keep a durable checkpoint while the page polls. A restarted server
        # can pause at this value instead of charging for time it was offline.
        state["running_since"] = now
        state["updated_at"] = _now_iso()
        _write(state)
    elif state.get("course_status") == "time_used":
        _write(state)
    allowance = int(state["allowance_seconds"])
    used = int(state["used_seconds"])
    state["elapsed_seconds"] = used
    state["remaining_seconds"] = max(0, allowance - used)
    state["server_now"] = time.time()
    state["instance_id"] = INSTANCE_ID
    return state


def pause_after_server_restart() -> None:
    """Freeze an interrupted session at its last durable checkpoint."""
    state = _read_raw()
    if not state.get("running"):
        return
    state["running"] = False
    state["running_since"] = None
    state["course_status"] = "paused"
    state["updated_at"] = _now_iso()
    _write(state)


def apply_action(action: str) -> dict[str, Any]:
    now = time.time()
    state = _checkpoint(_read_raw(), now)
    if action in {"start", "resume"} and state.get("running"):
        return get_state()
    if action == "start":
        if state["course_status"] in {"time_used", "complete"}:
            raise ValueError("This course is already finished.")
        if not state["running"]:
            state["running"] = True
            state["running_since"] = now
            state["course_status"] = "running"
    elif action == "pause":
        if state["running"]:
            state["running"] = False
            state["running_since"] = None
            state["course_status"] = "paused"
    elif action == "resume":
        if state["course_status"] in {"time_used", "complete"}:
            raise ValueError("This course is already finished.")
        if not state["running"]:
            state["running"] = True
            state["running_since"] = now
            state["course_status"] = "running"
    elif action == "reset":
        state = _default_state()
    else:
        raise ValueError("Action must be start, pause, resume, or reset.")

    state["updated_at"] = _now_iso()
    _write(state)
    return get_state()


def mark_level_complete(level_id: str) -> dict[str, Any]:
    """Record a level only after the coach has checked evidence and teach-back."""
    if level_id not in LEVEL_IDS:
        raise ValueError(f"Unknown level {level_id!r}; expected one of {', '.join(LEVEL_IDS)}.")

    now = time.time()
    state = _checkpoint(_read_raw(), now)
    if state.get("running"):
        state["running_since"] = now
    if state["course_status"] == "not_started":
        raise ValueError("Start the course before completing a level.")
    if state["course_status"] in {"time_used", "complete"}:
        raise ValueError("This course is already finished.")

    completed = list(state.get("completed_level_ids", []))
    if level_id in completed:
        return get_state()
    if level_id != state.get("current_level_id"):
        raise ValueError(f"Level {state.get('current_level_id')} must be completed before {level_id}.")

    completed.append(level_id)
    state["completed_level_ids"] = completed
    following = [item for item in LEVEL_IDS if item not in completed]
    if following:
        state["current_level_id"] = following[0]
    else:
        state["current_level_id"] = "done"
        state["running"] = False
        state["running_since"] = None
        state["course_status"] = "complete"

    state["updated_at"] = _now_iso()
    _write(state)
    return get_state()
