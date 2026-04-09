#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

SESSION_DIR = Path.home() / '.openclaw' / 'agents'
DEFAULT_RECENT = 8

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(text) / 4))

def text_from_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and isinstance(block.get('text'), str):
                parts.append(block['text'])
        return '\n'.join(parts)
    return ''

def iter_jsonl(path: Path):
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue

def session_files():
    for p in SESSION_DIR.rglob('*.jsonl'):
        yield p

def score_session(p: Path):
    try:
        return p.stat().st_mtime
    except Exception:
        return 0

def analyze(path: Path, recent=DEFAULT_RECENT):
    entries = list(iter_jsonl(path))
    messages = []
    for e in entries:
        if e.get('type') != 'message':
            continue
        m = e.get('message') or {}
        role = m.get('role', 'unknown')
        txt = text_from_content(m.get('content'))
        messages.append({'role': role, 'text': txt, 'raw': m})

    buckets = defaultdict(int)
    role_counts = defaultdict(int)
    for m in messages:
        t = estimate_tokens(m['text'])
        role = str(m['role']).lower()
        role_counts[role] += 1
        if role == 'system':
            buckets['system'] += t
        elif role == 'user':
            buckets['user'] += t
        elif role in ('assistant', 'model'):
            buckets['assistant'] += t
        elif role == 'toolresult':
            buckets['tools'] += t
        elif role == 'compactionsummary':
            buckets['summary'] += t
        else:
            buckets['other'] += t

    recent_msgs = messages[-recent:] if recent > 0 else []
    recent_tokens = sum(estimate_tokens(m['text']) for m in recent_msgs)
    total = sum(buckets.values())

    return {
        'session_file': str(path),
        'messages': len(messages),
        'role_counts': dict(role_counts),
        'estimated_tokens': dict(sorted(buckets.items())),
        'estimated_total_tokens': total,
        'estimated_recent_window_tokens': recent_tokens,
        'recent_window_messages': len(recent_msgs),
        'largest_messages': [
            {
                'role': m['role'],
                'tokens': estimate_tokens(m['text']),
                'preview': re.sub(r'\s+', ' ', m['text'])[:180]
            }
            for m in sorted(messages, key=lambda x: estimate_tokens(x['text']), reverse=True)[:12]
        ]
    }

if __name__ == '__main__':
    recent = DEFAULT_RECENT
    if len(sys.argv) > 1:
        try:
            recent = int(sys.argv[1])
        except Exception:
            pass
    files = sorted(session_files(), key=score_session, reverse=True)
    if not files:
        print(json.dumps({'error': 'no session files found'}, indent=2))
        sys.exit(1)
    report = analyze(files[0], recent=recent)
    print(json.dumps(report, indent=2))
