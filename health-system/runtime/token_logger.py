from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "runtime" / "data" / "logs" / "token_usage.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_token_usage(component: str, tokens_in: int, tokens_out: int, layers_used: List[str]) -> Dict[str, Any]:
    row = {
        "component": component,
        "tokens_in": int(tokens_in or 0),
        "tokens_out": int(tokens_out or 0),
        "layers_used": list(layers_used or []),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
