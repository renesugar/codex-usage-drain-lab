#!/usr/bin/env python3
"""Best-effort count of model activity strictly inside the target sleep window.

The target's own started/completed timestamps define the interval. Activity after
`completed` is not counted, so the legitimate completion turn is excluded.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def epoch(s: Any) -> float | None:
    if not isinstance(s, str): return None
    try: return datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
    except ValueError: return None


def find_time(row: dict[str, Any]) -> float | None:
    for key in ('timestamp','timestamp_utc','created_at','time'):
        value = row.get(key)
        if isinstance(value, (int,float)):
            return float(value)/1000 if value > 1e11 else float(value)
        t = epoch(value)
        if t is not None: return t
    payload = row.get('payload')
    if isinstance(payload, dict): return find_time(payload)
    return None


def load_window(target: Path) -> tuple[float,float]:
    start=end=None
    for line in target.read_text(encoding='utf-8').splitlines():
        try: row=json.loads(line)
        except ValueError: continue
        t=epoch(row.get('timestamp_utc'))
        if row.get('event')=='started': start=t
        elif row.get('event')=='completed': end=t
    if start is None or end is None: raise SystemExit('target log has no completed start/end window')
    return start,end


def nested_values(obj: Any):
    if isinstance(obj, dict):
        for k,v in obj.items():
            yield k,v
            yield from nested_values(v)
    elif isinstance(obj,list):
        for v in obj: yield from nested_values(v)


def codex_kind(row: dict[str,Any]) -> str | None:
    strings=[]
    for k,v in nested_values(row):
        if isinstance(v,str): strings.append(v.lower())
        strings.append(str(k).lower())
    joined=' '.join(strings)
    if 'token_usage_record' in joined: return 'sampling'
    if 'response.completed' in joined or 'post sampling token usage' in joined: return 'sampling'
    # Fallback: assistant response items are weaker evidence but better than silence.
    role=None; typ=None
    for k,v in nested_values(row):
        if k=='role' and isinstance(v,str): role=v
        if k=='type' and isinstance(v,str) and typ is None: typ=v
    if role=='assistant' and typ in ('message','response_item'): return 'assistant_message'
    return None


def omp_kind(row: dict[str,Any]) -> str | None:
    if row.get('type')=='model_usage': return 'auxiliary_model_usage'
    if row.get('type')=='message':
        msg=row.get('message')
        if isinstance(msg,dict) and msg.get('role')=='assistant': return 'assistant_message'
    return None


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--agent',choices=('codex','omp'),required=True)
    p.add_argument('--target-log',required=True)
    p.add_argument('--session-log',action='append',default=[])
    p.add_argument('--json',action='store_true',dest='as_json')
    args=p.parse_args()
    start,end=load_window(Path(args.target_log))
    counts={'sampling':0,'assistant_message':0,'auxiliary_model_usage':0}
    files=0; parsed=0
    for name in args.session_log:
        path=Path(name).expanduser()
        if not path.exists(): continue
        files+=1
        for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
            try: row=json.loads(line)
            except ValueError: continue
            t=find_time(row)
            if t is None or not (start < t < end): continue
            parsed+=1
            kind=codex_kind(row) if args.agent=='codex' else omp_kind(row)
            if kind: counts[kind]+=1
    if args.agent=='codex':
        model_rounds = counts['sampling'] or counts['assistant_message']
        confidence = 'high' if counts['sampling'] else ('low' if counts['assistant_message'] else 'unknown')
    else:
        model_rounds = counts['assistant_message'] + counts['auxiliary_model_usage']
        confidence = 'medium' if files else 'unknown'
    out={
        'agent':args.agent,'window_start_utc':datetime.fromtimestamp(start,timezone.utc).isoformat().replace('+00:00','Z'),
        'window_end_utc':datetime.fromtimestamp(end,timezone.utc).isoformat().replace('+00:00','Z'),
        'session_logs_read':files,'records_in_window':parsed,'counts':counts,
        'pre_completion_model_rounds':model_rounds,'confidence':confidence,
        'interpretation':'Rounds strictly after target start and before target completion are unnecessary for learning that this deterministic sleeper is still running. Auxiliary OMP model_usage entries are included when present.'
    }
    print(json.dumps(out,indent=2,sort_keys=True) if args.as_json else f"pre_completion_model_rounds={model_rounds} confidence={confidence} details={counts}")
    return 0

if __name__=='__main__': raise SystemExit(main())
