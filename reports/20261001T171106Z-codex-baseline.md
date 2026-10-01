# Usage-drain test report: 20261001T171106Z-codex-baseline

**INVALID — excluded from quota comparisons.** Both saved subscription snapshots
contain `state: unknown` and `timeout or invalid response`. Nested probes failed
inside the sandbox; the same nested probe succeeded outside it. Earlier preflight
values are not substitutes for the missing before/after measurements.

The single target ran from `2026-10-01T17:11:14.344733Z` to
`2026-10-01T18:12:44.350501Z`, with no fail-safe or replacement sleeper.
The active rollout records `gpt-6-astra` / `low`. One wait-status commentary
occurred during the interval to satisfy the host's hourly communication rule.
The 26-round count is best effort and cannot establish subscriber quota drain.

- Date/time started: `2026-10-01T17:11:07.427557Z`
- Date/time finished: `2026-10-01T18:12:54.207989Z`
- Mode: **baseline**
- Model: **gpt-6-astra**
- Reasoning effort: **low**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Pre-completion model-round estimate: **26** (confidence: high)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| codex | codex-cli 0.159.3 | unknown | unknown | unknown | unknown | unknown | unknown |

## Model activity during deterministic sleep

```json
{
  "agent": "codex",
  "confidence": "high",
  "counts": {
    "assistant_message": 1,
    "auxiliary_model_usage": 0,
    "sampling": 26
  },
  "interpretation": "Rounds strictly after target start and before target completion are unnecessary for learning that this deterministic sleeper is still running. Auxiliary OMP model_usage entries are included when present.",
  "pre_completion_model_rounds": 26,
  "records_in_window": 108,
  "session_logs_read": 1,
  "window_end_utc": "2026-10-01T18:12:44.350501Z",
  "window_start_utc": "2026-10-01T17:11:14.344733Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Raw evidence

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261001T171106Z-codex-baseline/`. Raw session transcripts are **not copied into this repository**.
