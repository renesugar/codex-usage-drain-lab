#!/usr/bin/env python3
"""Print recent candidate session JSONL files; never reads transcript contents."""
from __future__ import annotations
import argparse
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--agent',choices=('codex','omp'),required=True); p.add_argument('--limit',type=int,default=10); args=p.parse_args()
    root=Path('~/.codex/sessions').expanduser() if args.agent=='codex' else Path('~/.omp/agent/sessions').expanduser()
    if not root.exists(): return
    files=sorted(root.rglob('*.jsonl'),key=lambda x:x.stat().st_mtime,reverse=True)
    for f in files[:args.limit]: print(f)
if __name__=='__main__': main()
