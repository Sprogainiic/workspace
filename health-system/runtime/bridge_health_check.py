from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
INGEST_DIR = ROOT / "runtime" / "data" / "ingest"
HEARTBEAT_LOG = INGEST_DIR / "reactive_bridge_heartbeat.jsonl"
STATUS_FILE = INGEST_DIR / "reactive_bridge_status.json"

DEFAULT_MAX_HEARTBEAT_AGE_SECONDS = 15
DEFAULT_MAX_STATUS_AGE_SECONDS = 15


def _parse_ts(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _last_jsonl_row(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except Exception:
        return None


def bridge_health(now: Optional[datetime] = None, max_heartbeat_age_seconds: int = DEFAULT_MAX_HEARTBEAT_AGE_SECONDS, max_status_age_seconds: int = DEFAULT_MAX_STATUS_AGE_SECONDS) -> Dict[str, Any]:
    now = now or datetime.now(timezone.utc).astimezone()
    hb = _last_jsonl_row(HEARTBEAT_LOG)
    status = json.loads(STATUS_FILE.read_text(encoding="utf-8")) if STATUS_FILE.exists() else None

    hb_ts = _parse_ts(hb.get("timestamp", "")) if hb else None
    status_ts = _parse_ts(status.get("timestamp", "")) if isinstance(status, dict) else None
    hb_age = (now - hb_ts).total_seconds() if hb_ts else None
    status_age = (now - status_ts).total_seconds() if status_ts else None

    healthy = (
        hb_age is not None and hb_age <= max_heartbeat_age_seconds and
        status_age is not None and status_age <= max_status_age_seconds
    )
    return {
        "healthy": healthy,
        "last_heartbeat_age_seconds": hb_age,
        "last_status_age_seconds": status_age,
        "max_heartbeat_age_seconds": max_heartbeat_age_seconds,
        "max_status_age_seconds": max_status_age_seconds,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-heartbeat-age-seconds", type=int, default=DEFAULT_MAX_HEARTBEAT_AGE_SECONDS)
    parser.add_argument("--max-status-age-seconds", type=int, default=DEFAULT_MAX_STATUS_AGE_SECONDS)
    args = parser.parse_args(argv)
    result = bridge_health(max_heartbeat_age_seconds=args.max_heartbeat_age_seconds, max_status_age_seconds=args.max_status_age_seconds)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
