#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('agent',choices=('codex','omp'))
    p.add_argument('profile',choices=('baseline','mitigation','sol-max-baseline'))
    args=p.parse_args()
    if args.profile == 'sol-max-baseline' and args.agent != 'codex':
        p.error('sol-max-baseline is a Codex-only experiment profile')
    if args.agent=='codex':
        src=ROOT/'configs'/f'codex-{args.profile}.toml'; dst=ROOT/'.codex'/'config.toml'
    else:
        src=ROOT/'configs'/f'omp-{args.profile}.yml'; dst=ROOT/'.omp'/'config.yml'
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
    print(f'{args.agent}: installed {args.profile} profile -> {dst.relative_to(ROOT)}')
if __name__=='__main__': main()
