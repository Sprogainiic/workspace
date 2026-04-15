from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .bridge_health_check import bridge_health, DEFAULT_MAX_HEARTBEAT_AGE_SECONDS, DEFAULT_MAX_STATUS_AGE_SECONDS

ROOT = Path(__file__).resolve().parents[1]
AUDIT_LOG = ROOT / "runtime" / "data" / "ingest" / "reactive_bridge_restart_audit.jsonl"
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
SERVICE = "health-reactive-bridge.service"
RECOVERY_GRACE_SECONDS = 10


def _append(row: Dict[str, Any]) -> Dict[str, Any]:
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def log_restart(action: str, reason: str, **extra) -> Dict[str, Any]:
    row = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "action": action,
        "service": SERVICE,
        "reason": reason,
        **extra,
    }
    return _append(row)


def _service_active() -> bool:
    proc = subprocess.run(["systemctl", "is-active", SERVICE], capture_output=True, text=True)
    return proc.returncode == 0 and proc.stdout.strip() == "active"


def watchdog_once(max_heartbeat_age_seconds: int = DEFAULT_MAX_HEARTBEAT_AGE_SECONDS, max_status_age_seconds: int = DEFAULT_MAX_STATUS_AGE_SECONDS, recovery_grace_seconds: int = RECOVERY_GRACE_SECONDS) -> Dict[str, Any]:
    result = bridge_health(max_heartbeat_age_seconds=max_heartbeat_age_seconds, max_status_age_seconds=max_status_age_seconds)
    if result["healthy"]:
        return {"healthy": True, "restart_attempted": False, "reason": None}

    hb_age = result.get("last_heartbeat_age_seconds")
    status_age = result.get("last_status_age_seconds")
    if hb_age is None or hb_age > max_heartbeat_age_seconds:
        reason = "stale_heartbeat"
    else:
        reason = "stale_status"

    active_before = _service_active()
    command = "restart" if active_before else "start"
    proc = subprocess.run(["systemctl", command, SERVICE], capture_output=True, text=True, timeout=20)

    time.sleep(recovery_grace_seconds)
    active_after = _service_active()
    post = bridge_health(max_heartbeat_age_seconds=max_heartbeat_age_seconds, max_status_age_seconds=max_status_age_seconds)
    heartbeat_fresh_after = bool(post["healthy"])

    audit = log_restart(
        "restart_service",
        reason,
        command=command,
        command_success=(proc.returncode == 0),
        service_active_after=active_after,
        heartbeat_fresh_after=heartbeat_fresh_after,
    )

    if not active_after:
        log_restart("restart_service_failed", "inactive_after_restart", command=command)
    elif not heartbeat_fresh_after:
        log_restart("restart_service_failed", "stale_after_restart", command=command)

    return {
        "healthy": False,
        "restart_attempted": True,
        "reason": reason,
        "command": command,
        "restart_returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "service_active_after": active_after,
        "heartbeat_fresh_after": heartbeat_fresh_after,
        "audit": audit,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-heartbeat-age-seconds", type=int, default=DEFAULT_MAX_HEARTBEAT_AGE_SECONDS)
    parser.add_argument("--max-status-age-seconds", type=int, default=DEFAULT_MAX_STATUS_AGE_SECONDS)
    parser.add_argument("--recovery-grace-seconds", type=int, default=RECOVERY_GRACE_SECONDS)
    args = parser.parse_args(argv)
    result = watchdog_once(max_heartbeat_age_seconds=args.max_heartbeat_age_seconds, max_status_age_seconds=args.max_status_age_seconds, recovery_grace_seconds=args.recovery_grace_seconds)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if (result.get("healthy") or result.get("heartbeat_fresh_after")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
