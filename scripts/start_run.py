#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def now(): return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--agent',choices=('codex','omp'),required=True)
    p.add_argument('--mode',choices=('baseline','mitigation'),required=True)
    p.add_argument('--model',default='gpt-6-astra')
    p.add_argument('--effort',default='low')
    p.add_argument('--run-id')
    args=p.parse_args(); run_id=args.run_id or f"{now()}-{args.agent}-{args.mode}"
    run=ROOT/'reports'/'raw'/run_id; run.mkdir(parents=True,exist_ok=False)
    probe=[sys.executable,str(ROOT/'scripts'/'check_agent_usage.py'),'--agent',args.agent,'--json']
    result=subprocess.run(probe,capture_output=True,text=True)
    (run/'before.json').write_text(result.stdout or '{}\n')
    if result.returncode not in (0,2):
        raise SystemExit(f'usage probe failed: {result.stderr or result.stdout}')
    before=json.loads(result.stdout or '{}')
    required=('five_hour_remaining_percent','weekly_remaining_percent','five_hour_reset_utc','weekly_reset_utc')
    if before.get('state') != 'active' or any(before.get(k) is None for k in required):
        raise SystemExit('usage probe missing required subscription telemetry; do not launch target')
    for key in ('five_hour_reset_utc','weekly_reset_utc'):
        reset=datetime.fromisoformat(before[key].replace('Z','+00:00'))
        if (reset-datetime.now(timezone.utc)).total_seconds() <= 3900:
            raise SystemExit('subscription reset too close; do not launch target')
    version_cmd=[args.agent,'--version'] if args.agent=='omp' else ['codex','--version']
    try: version=subprocess.run(version_cmd,capture_output=True,text=True,timeout=5).stdout.strip().splitlines()[0]
    except Exception: version='unknown'
    try: commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,timeout=5).stdout.strip()
    except Exception: commit='unknown'
    meta={'run_id':run_id,'agent':args.agent,'mode':args.mode,'model':args.model,'effort':args.effort,'agent_version':version,'harness_commit':commit,'started_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}
    (run/'metadata.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    print(run_id)
if __name__=='__main__': main()
