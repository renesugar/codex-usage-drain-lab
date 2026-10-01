#!/usr/bin/env python3
"""Inspect coding-agent usage without sending a model prompt.

Codex: reads account/rateLimits/read from the local app-server.
OMP: reads `omp usage --json --provider openai-codex`, which uses ChatGPT OAuth.
Claude: reads the optional local status-line cache used by the Notrios pattern.
OpenCode2: reports local `stats --json` only; it is not treated as a ChatGPT
quota source.

This script deliberately never uses OpenAI API pricing and never sends a chat
completion merely to measure quota.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Sequence

WINDOW_NAMES = {"primary", "secondary", "weekly", "fiveHour", "five_hour"}
CLAUDE_USAGE_CACHE = "~/.claude/usage-cache.json"
SELF_ENV = "AGENT_USAGE_AGENT"
LEGACY_SELF_ENV = "NOTRIOS_AGENT_USAGE_AGENT"


def percentage(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if 0 <= number <= 100:
        return round(number, 6)
    return None


def epoch_seconds(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            number = float(text)
        except ValueError:
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.timestamp()
    else:
        return None
    if abs(number) > 1e11:
        number /= 1000.0
    return number


def reset_utc(value: Any) -> str | None:
    seconds = epoch_seconds(value)
    if seconds is None:
        return str(value) if value not in (None, "") else None
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def client_version(command: Sequence[str]) -> str | None:
    try:
        result = subprocess.run(
            [command[0], "--version"], capture_output=True, text=True, timeout=4
        )
    except (OSError, subprocess.SubprocessError):
        return None
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0] if text else None


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None:
        return
    if process.stdin:
        try:
            process.stdin.close()
        except (OSError, ValueError):
            pass
    try:
        if os.name == "posix" and process.pid:
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=1)
    except (OSError, subprocess.TimeoutExpired):
        try:
            if os.name == "posix" and process.pid:
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except OSError:
            pass


def make_bucket(
    name: str,
    *,
    used: Any = None,
    remaining: Any = None,
    duration_minutes: Any = None,
    reset: Any = None,
    limit_id: str | None = None,
) -> dict[str, Any] | None:
    u = percentage(used)
    r = percentage(remaining)
    if u is None and r is not None:
        u = round(100 - r, 6)
    if r is None and u is not None:
        r = round(100 - u, 6)
    if u is None or r is None:
        return None
    try:
        duration = float(duration_minutes) if duration_minutes is not None else None
    except (TypeError, ValueError):
        duration = None
    out: dict[str, Any] = {
        "name": name,
        "used_percent": u,
        "remaining_percent": r,
        "duration_minutes": duration,
        "reset_utc": reset_utc(reset),
        "exhausted": u >= 100,
    }
    if limit_id:
        out["limit_id"] = limit_id
    return out


def annotate_named_windows(result: dict[str, Any]) -> dict[str, Any]:
    """Set five-hour/weekly convenience fields from duration, then names."""
    buckets = result.get("buckets") or []
    five: dict[str, Any] | None = None
    week: dict[str, Any] | None = None
    for bucket in buckets:
        duration = bucket.get("duration_minutes")
        name = str(bucket.get("name", "")).lower()
        if isinstance(duration, (int, float)):
            if 240 <= duration <= 360 and five is None:
                five = bucket
            if 9000 <= duration <= 11000 and week is None:
                week = bucket
        if five is None and ("5h" in name or "five" in name or "5 hour" in name):
            five = bucket
        if week is None and ("week" in name or "7d" in name or "seven" in name):
            week = bucket
    # Only use legacy primary/secondary fallback when durations were unavailable.
    if five is None:
        five = next((b for b in buckets if b.get("name") == "primary" and b.get("duration_minutes") is None), None)
    if week is None:
        week = next((b for b in buckets if b.get("name") == "secondary" and b.get("duration_minutes") is None), None)
    for label, bucket in (("five_hour", five), ("weekly", week)):
        if bucket:
            result[f"{label}_remaining_percent"] = bucket["remaining_percent"]
            result[f"{label}_used_percent"] = bucket["used_percent"]
            result[f"{label}_reset_utc"] = bucket.get("reset_utc")
    return result


def summarize(agent: str, buckets: list[dict[str, Any]], version: str | None, source: str, error: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "agent": agent,
        "state": "active" if buckets else "unknown",
        "client_version": version,
        "source": source,
        "buckets": buckets,
    }
    if error:
        result["error"] = error
    if buckets:
        binding = min(buckets, key=lambda b: b["remaining_percent"])
        result["binding_remaining_percent"] = binding["remaining_percent"]
        if binding.get("exhausted") or binding["remaining_percent"] <= 0:
            result["state"] = "pause"
    return annotate_named_windows(result)


def parse_codex_response(message: Any, version: str | None = None) -> list[dict[str, Any]]:
    if not isinstance(message, dict):
        return []
    data = message.get("result", message)
    if not isinstance(data, dict):
        return []
    limits = data.get("rateLimits", data.get("rate_limits", {}))
    if not isinstance(limits, dict):
        return []
    snapshots = (
        limits.get("rateLimitsByLimitId")
        or limits.get("rate_limits_by_limit_id")
        or data.get("rateLimitsByLimitId")
        or data.get("rate_limits_by_limit_id")
    )
    if not isinstance(snapshots, dict):
        snapshots = {str(limits.get("limitId") or "default"): limits}
    buckets: list[dict[str, Any]] = []
    seen: set[str] = set()
    for limit_id, snapshot in snapshots.items():
        if not isinstance(snapshot, dict):
            continue
        windows = {k: v for k, v in snapshot.items() if k in WINDOW_NAMES and isinstance(v, dict)}
        if not windows and any(k in snapshot for k in ("usedPercent", "remainingPercent")):
            windows = {"primary": snapshot}
        for name, raw in windows.items():
            identity = json.dumps([name, raw], sort_keys=True, default=str)
            if identity in seen:
                continue
            bucket = make_bucket(
                name,
                used=raw.get("usedPercent", raw.get("used_percent", raw.get("used"))),
                remaining=raw.get("remainingPercent", raw.get("remaining_percent", raw.get("remaining"))),
                duration_minutes=raw.get("windowDurationMins", raw.get("window_duration_mins")),
                reset=raw.get("resetsAt", raw.get("resetAt", raw.get("reset_at", raw.get("reset")))),
                limit_id=str(limit_id),
            )
            if bucket:
                buckets.append(bucket)
                seen.add(identity)
    return buckets


def probe_codex(timeout: float = 10) -> dict[str, Any]:
    command = ["codex", "app-server", "--stdio"]
    payloads = [
        {"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "usage-drain-harness", "version": "1"}}},
        {"method": "initialized"},
        {"id": 2, "method": "account/rateLimits/read"},
    ]
    process: subprocess.Popen[str] | None = None
    selector: selectors.BaseSelector | None = None
    version = client_version(command)
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=(os.name == "posix"),
        )
        assert process.stdin and process.stdout
        process.stdin.write("\n".join(json.dumps(p) for p in payloads) + "\n")
        process.stdin.flush()
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout
        response = None
        while time.monotonic() < deadline:
            if not selector.select(max(0, deadline - time.monotonic())):
                break
            line = process.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(msg, dict) and msg.get("id") == 2:
                response = msg
                break
        if response is None:
            return summarize("codex", [], version, "codex app-server account/rateLimits/read", "timeout or invalid response")
        return summarize("codex", parse_codex_response(response, version), version, "codex app-server account/rateLimits/read")
    except (OSError, ValueError) as exc:
        return summarize("codex", [], version, "codex app-server account/rateLimits/read", str(exc))
    finally:
        if selector:
            selector.close()
        stop_process(process)


def walk_dicts(obj: Any) -> Iterable[dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_dicts(value)


def parse_omp_usage(payload: Any) -> list[dict[str, Any]]:
    """Normalize OMP openai-codex usage JSON across recent CLI shapes."""
    limits: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in walk_dicts(payload):
        provider = node.get("provider") or node.get("providerId")
        node_limits = node.get("limits")
        if provider not in (None, "openai-codex") or not isinstance(node_limits, list):
            continue
        for item in node_limits:
            if not isinstance(item, dict):
                continue
            amount = item.get("amount") if isinstance(item.get("amount"), dict) else item
            window = item.get("window") if isinstance(item.get("window"), dict) else item
            used = amount.get("usedPercent", amount.get("used_percent"))
            remaining = amount.get("remainingPercent", amount.get("remaining_percent"))
            used_fraction = amount.get("usedFraction", amount.get("used_fraction"))
            remaining_fraction = amount.get("remainingFraction", amount.get("remaining_fraction"))
            if used is None and used_fraction is not None:
                try:
                    used = float(used_fraction) * 100
                except (TypeError, ValueError):
                    pass
            if remaining is None and remaining_fraction is not None:
                try:
                    remaining = float(remaining_fraction) * 100
                except (TypeError, ValueError):
                    pass
            duration = window.get("durationMinutes", window.get("duration_minutes"))
            if duration is None and window.get("durationMs") is not None:
                try:
                    duration = float(window["durationMs"]) / 60000
                except (TypeError, ValueError):
                    pass
            if duration is None and window.get("durationSeconds") is not None:
                try:
                    duration = float(window["durationSeconds"]) / 60
                except (TypeError, ValueError):
                    pass
            name = str(item.get("name") or item.get("id") or window.get("name") or "rate_limit")
            bucket = make_bucket(
                name,
                used=used,
                remaining=remaining,
                duration_minutes=duration,
                reset=window.get("resetsAt", window.get("resets_at", item.get("resetsAt"))),
                limit_id=str(item.get("id") or "openai-codex"),
            )
            if bucket:
                identity = json.dumps(bucket, sort_keys=True)
                if identity not in seen:
                    limits.append(bucket)
                    seen.add(identity)
    # Handle a direct wham-like JSON shape if a future CLI emits it.
    for name, key in (("primary", "primary_window"), ("secondary", "secondary_window")):
        for node in walk_dicts(payload):
            raw = node.get(key)
            if not isinstance(raw, dict):
                continue
            bucket = make_bucket(
                name,
                used=raw.get("used_percent", raw.get("usedPercent")),
                remaining=raw.get("remaining_percent", raw.get("remainingPercent")),
                duration_minutes=(float(raw["limit_window_seconds"]) / 60 if raw.get("limit_window_seconds") is not None else None),
                reset=raw.get("reset_at", raw.get("resetsAt")),
                limit_id="openai-codex",
            )
            if bucket:
                identity = json.dumps(bucket, sort_keys=True)
                if identity not in seen:
                    limits.append(bucket)
                    seen.add(identity)
    return limits


def probe_omp(timeout: float = 15) -> dict[str, Any]:
    version = client_version(("omp",))
    commands = [
        ["omp", "usage", "--json", "--provider", "openai-codex", "--redact"],
        ["omp", "usage", "--json", "--provider", "openai-codex"],
    ]
    last_error = None
    for command in commands:
        try:
            run = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            last_error = str(exc)
            continue
        if run.returncode != 0:
            last_error = (run.stderr or run.stdout).strip() or f"exit {run.returncode}"
            continue
        try:
            payload = json.loads(run.stdout)
        except json.JSONDecodeError as exc:
            last_error = f"invalid JSON: {exc}"
            continue
        buckets = parse_omp_usage(payload)
        result = summarize("omp", buckets, version, "omp usage --provider openai-codex")
        result["auth_route"] = "openai-codex (ChatGPT/Codex OAuth subscription)"
        if not buckets:
            result["error"] = "OMP returned JSON but no OpenAI Codex quota windows were recognized"
        return result
    result = summarize("omp", [], version, "omp usage --provider openai-codex", last_error or "omp unavailable")
    result["auth_route"] = "openai-codex (ChatGPT/Codex OAuth subscription)"
    return result


def parse_claude_cache(path: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(Path(path).expanduser().read_text())
    except (OSError, ValueError):
        return []
    limits = data.get("rate_limits", {}) if isinstance(data, dict) else {}
    buckets: list[dict[str, Any]] = []
    if isinstance(limits, dict):
        for name, raw in limits.items():
            if not isinstance(raw, dict):
                continue
            used = raw.get("usedPercent", raw.get("used_percent", raw.get("usedPercentage")))
            remaining = raw.get("remainingPercent", raw.get("remaining_percent", raw.get("remainingPercentage")))
            bucket = make_bucket(
                str(name), used=used, remaining=remaining,
                duration_minutes=raw.get("windowDurationMins", raw.get("window_duration_mins")),
                reset=raw.get("resets_at", raw.get("resetsAt")),
            )
            if bucket:
                buckets.append(bucket)
    return buckets


def probe_claude() -> dict[str, Any]:
    path = os.environ.get("CLAUDE_USAGE_CACHE", CLAUDE_USAGE_CACHE)
    return summarize("claude", parse_claude_cache(path), client_version(("claude",)), f"local cache {Path(path).expanduser()}")


def probe_opencode2(timeout: float = 10) -> dict[str, Any]:
    binary = "opencode2" if shutil_which("opencode2") else "opencode"
    version = client_version((binary,)) if binary else None
    if not binary:
        return {"agent": "opencode2", "state": "unknown", "client_version": None, "source": "local stats", "buckets": [], "error": "opencode2/opencode not found"}
    try:
        run = subprocess.run([binary, "stats", "--json"], capture_output=True, text=True, timeout=timeout)
        payload = json.loads(run.stdout) if run.returncode == 0 and run.stdout.strip() else None
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"agent": "opencode2", "state": "unknown", "client_version": version, "source": f"{binary} stats --json", "buckets": [], "error": str(exc)}
    return {
        "agent": "opencode2",
        "state": "informational",
        "client_version": version,
        "source": f"{binary} stats --json",
        "buckets": [],
        "quota_windows_supported": False,
        "note": "OpenCode2 local stats are not treated as ChatGPT 5-hour/weekly subscription quota.",
        "stats": payload,
    }


def shutil_which(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def read_process(pid: int) -> tuple[int, str, list[str]] | None:
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as stream:
            parent = int(stream.read().rsplit(")", 1)[1].split()[1])
        with open(f"/proc/{pid}/cmdline", "rb") as stream:
            argv = [x.decode(errors="replace") for x in stream.read().split(b"\0") if x]
        try:
            exe = os.readlink(f"/proc/{pid}/exe")
        except OSError:
            exe = ""
        return parent, exe, argv
    except (OSError, ValueError, IndexError):
        return None


def classify_agent(executable: str, argv: Sequence[str]) -> str | None:
    names = [os.path.basename(executable).lower() if executable else "", os.path.basename(argv[0]).lower() if argv else ""]
    if any(n in ("claude", "claude-code") for n in names):
        return "claude"
    if any(n == "omp" or n.startswith("omp-") for n in names):
        return "omp"
    if any(n == "codex" or n.startswith("codex-") for n in names):
        return "codex"
    if any(n in ("opencode2", "opencode") for n in names):
        return "opencode2"
    if "node" in names and len(argv) > 1:
        child = os.path.basename(argv[1]).lower()
        if child == "codex": return "codex"
        if child == "omp": return "omp"
        if child in ("opencode", "opencode2"): return "opencode2"
    return None


def identify_self() -> tuple[str | None, str]:
    pid = os.getpid()
    seen: set[int] = set()
    while pid > 0 and pid not in seen and len(seen) < 64:
        seen.add(pid)
        row = read_process(pid)
        if row is None:
            break
        parent, exe, argv = row
        found = classify_agent(exe, argv)
        if found:
            return found, f"process ancestry: pid {pid} is {found}"
        pid = parent
    explicit = (os.environ.get(SELF_ENV) or os.environ.get(LEGACY_SELF_ENV) or "").strip().lower()
    if explicit in {"codex", "omp", "claude", "opencode2", "all"}:
        return explicit, f"environment fallback: {explicit}"
    return None, "no coding agent found in process ancestry or fallback environment"


def probe(name: str, timeout: float) -> dict[str, Any]:
    if name == "codex": return probe_codex(timeout)
    if name == "omp": return probe_omp(timeout)
    if name == "claude": return probe_claude()
    if name == "opencode2": return probe_opencode2(timeout)
    raise ValueError(name)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=("codex", "omp", "claude", "opencode2", "all", "self"), default="all")
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--minimum-remaining", type=float, default=0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if not 0 <= args.minimum_remaining <= 100:
        parser.error("--minimum-remaining must be between 0 and 100")
    selected = args.agent
    selection = None
    if selected == "self":
        detected, selection = identify_self()
        if detected is None:
            selected = "all"
        else:
            selected = detected
    names = ["codex", "omp", "claude", "opencode2"] if selected == "all" else [selected]
    results = [probe(name, args.timeout) for name in names]
    if selection:
        for result in results:
            result["selection"] = selection
    output: Any = results if selected == "all" else results[0]
    encoded = json.dumps(output, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(encoded + "\n")
    if args.as_json or args.output:
        print(encoded)
    else:
        for result in results:
            print(f"{result['agent']}: state={result['state']} version={result.get('client_version') or 'unknown'}")
            print(f"  5h remaining={result.get('five_hour_remaining_percent', 'unknown')} weekly remaining={result.get('weekly_remaining_percent', 'unknown')}")
            for b in result.get("buckets", []):
                print(f"  {b['name']}: remaining={b['remaining_percent']} duration_minutes={b.get('duration_minutes')} reset={b.get('reset_utc')}")
            if result.get("error"): print(f"  error={result['error']}")
    known = [r for r in results if r.get("binding_remaining_percent") is not None]
    if any(float(r["binding_remaining_percent"]) <= args.minimum_remaining for r in known):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
