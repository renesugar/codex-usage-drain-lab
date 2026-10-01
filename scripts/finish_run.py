#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def pct(data,key):
    v=data.get(key); return 'unknown' if v is None else f'{float(v):.2f}%'
def num(data,key):
    v=data.get(key); return None if v is None else float(v)
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-id',required=True)
    p.add_argument('--session-log',action='append',default=[])
    args=p.parse_args(); run=ROOT/'reports'/'raw'/args.run_id
    meta=json.loads((run/'metadata.json').read_text()); agent=meta['agent']
    probe=subprocess.run([sys.executable,str(ROOT/'scripts'/'check_agent_usage.py'),'--agent',agent,'--json'],capture_output=True,text=True)
    (run/'after.json').write_text(probe.stdout or '{}\n')
    before=json.loads((run/'before.json').read_text()); after=json.loads((run/'after.json').read_text())
    rounds={'pre_completion_model_rounds':'unknown','confidence':'unknown','counts':{}}
    target=run/'target.jsonl'
    if target.exists() and args.session_log:
        cmd=[sys.executable,str(ROOT/'scripts'/'count_model_rounds.py'),'--agent',agent,'--target-log',str(target),'--json']
        for log in args.session_log: cmd += ['--session-log',log]
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode==0:
            rounds=json.loads(r.stdout); (run/'rounds.json').write_text(r.stdout)
    b5=num(before,'five_hour_remaining_percent'); a5=num(after,'five_hour_remaining_percent')
    bw=num(before,'weekly_remaining_percent'); aw=num(after,'weekly_remaining_percent')
    d5='unknown' if b5 is None or a5 is None else f'{b5-a5:.2f} pp'
    dw='unknown' if bw is None or aw is None else f'{bw-aw:.2f} pp'
    target_rows=[]
    if target.exists():
        for line in target.read_text().splitlines():
            try: target_rows.append(json.loads(line))
            except ValueError: pass
    target_status='completed' if any(x.get('event')=='completed' for x in target_rows) else ('failsafe_timeout' if any(x.get('event')=='failsafe_timeout' for x in target_rows) else 'unknown')
    ended=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    report=ROOT/'reports'/f"{args.run_id}.md"
    text=f'''# Usage-drain test report: {args.run_id}\n\n- Date/time started: `{meta.get('started_utc')}`\n- Date/time finished: `{ended}`\n- Mode: **{meta['mode']}**\n- Model: **{meta['model']}**\n- Reasoning effort: **{meta['effort']}**\n- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**\n- Target status: **{target_status}**\n- Pre-completion model-round estimate: **{rounds.get('pre_completion_model_rounds','unknown')}** (confidence: {rounds.get('confidence','unknown')})\n\n| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |\n|---|---|---:|---:|---:|---:|---:|---:|\n| {agent} | {meta.get('agent_version','unknown')} | {pct(before,'five_hour_remaining_percent')} | {pct(before,'weekly_remaining_percent')} | {pct(after,'five_hour_remaining_percent')} | {pct(after,'weekly_remaining_percent')} | {d5} | {dw} |\n\n## Model activity during deterministic sleep\n\n```json\n{json.dumps(rounds,indent=2,sort_keys=True)}\n```\n\nThe interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.\n\n## Raw evidence\n\nRaw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/{args.run_id}/`. Raw session transcripts are **not copied into this repository**.\n'''
    report.write_text(text); print(report)
if __name__=='__main__': main()
