#!/usr/bin/env python3
"""Control the local five-hour course timer from Codex or a terminal."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT / "timer"))

from ensure_timer import main as ensure_timer_main, probe_server  # noqa: E402
from state import apply_action, get_state, mark_level_complete, pause_after_server_restart  # noqa: E402


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(max(0, seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Control the local 5H Bootcamp timer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "start", "pause", "resume"):
        subparsers.add_parser(name)
    complete = subparsers.add_parser("complete", help="Record a level after evidence has been checked")
    complete.add_argument("level", choices=("01", "02", "03", "04", "05"))
    reset = subparsers.add_parser("reset", help="Reset the local course clock and progress")
    reset.add_argument("--confirm", action="store_true", help="Required to reset saved state")
    args = parser.parse_args()

    try:
        if args.command in {"start", "resume"}:
            if ensure_timer_main() != 0:
                return 1
        elif args.command != "reset" and probe_server() != "ready":
            # A stopped or foreign timer must not add downtime to this course.
            pause_after_server_restart()
            print("本课程计时页未连接，已停在上次保存的进度。", file=sys.stderr)
        if args.command == "status":
            state = get_state()
        elif args.command == "complete":
            state = mark_level_complete(args.level)
        elif args.command == "reset":
            if not args.confirm:
                parser.error("reset requires --confirm")
            state = apply_action("reset")
        else:
            state = apply_action(args.command)
    except ValueError as exc:
        print(f"Timer error: {exc}", file=sys.stderr)
        return 1

    remaining = format_duration(int(state["remaining_seconds"]))
    status = state["course_status"]
    current = "course complete" if state["current_level_id"] == "done" else f"Level {state['current_level_id']}"
    completed = len(state.get("completed_level_ids", []))
    print(f"{remaining} remaining · {status} · {current} · {completed}/5 levels complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
