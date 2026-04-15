from __future__ import annotations

import argparse
import json
import time
from typing import Any, Dict, List

from .reactive_session_bridge import process_session_messages


def run_once(session_key: str, history_fetcher) -> List[Dict[str, Any]]:
    data = history_fetcher(sessionKey=session_key, limit=20, includeTools=False)
    messages = data.get("messages", [])
    return process_session_messages(session_key, messages)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-key", required=True)
    parser.add_argument("--mode", choices=["once", "loop"], default="once")
    args = parser.parse_args(argv)
    print(json.dumps({
        "status": "runner_requires_tool_integration",
        "session_key": args.session_key,
        "mode": args.mode,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
