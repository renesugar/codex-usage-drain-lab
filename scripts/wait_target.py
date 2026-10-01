#!/usr/bin/env python3
"""Deterministic long-running target used by the usage-drain experiment."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
import time


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--sleep-seconds', type=float, default=61*60+30, help='Expected runtime; default 3690 seconds (61m30s).')
    p.add_argument('--failsafe-seconds', type=float, default=65*60, help='Hard fail-safe; default 3900 seconds (65m).')
    p.add_argument('--log', required=True)
    args = p.parse_args()
    if args.sleep_seconds <= 0 or args.failsafe_seconds <= args.sleep_seconds:
        p.error('--failsafe-seconds must be greater than --sleep-seconds, both positive')
    path = Path(args.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    def record(event: str, **extra):
        row = {'event': event, 'timestamp_utc': now_utc(), 'monotonic': time.monotonic(), 'pid': os.getpid(), **extra}
        with lock, path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, sort_keys=True) + '\n')
            f.flush(); os.fsync(f.fileno())
        print(json.dumps(row, sort_keys=True), flush=True)
    def fail():
        record('failsafe_timeout', expected_sleep_seconds=args.sleep_seconds, failsafe_seconds=args.failsafe_seconds)
        os._exit(124)
    timer = threading.Timer(args.failsafe_seconds, fail)
    timer.daemon = True
    timer.start()
    record('started', expected_sleep_seconds=args.sleep_seconds, failsafe_seconds=args.failsafe_seconds)
    time.sleep(args.sleep_seconds)
    record('completed', elapsed_seconds=args.sleep_seconds)
    timer.cancel()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
