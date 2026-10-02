# Usage-drain test report: 20261002T000931Z-codex-baseline

- Date/time started: `2026-10-02T00:09:33.235895Z`
- Date/time finished: `2026-10-02T01:11:42.571931Z`
- Mode: **baseline**
- Model: **gpt-6-astra**
- Reasoning effort: **low**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Active host version: **0.160.0**, recorded separately in run metadata; installed CLI also **0.160.0**.
- Pre-completion model-round estimate: **26** (confidence: high)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| codex | codex-cli 0.160.0 | 60.00% | 87.00% | 45.00% | 85.00% | 15.00 pp | 2.00 pp |

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
  "records_in_window": 106,
  "session_logs_read": 1,
  "window_end_utc": "2026-10-02T01:11:31.002099Z",
  "window_start_utc": "2026-10-02T00:10:00.996499Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Protocol qualification

One target completed from `2026-10-02T00:10:00.996499Z` to
`2026-10-02T01:11:31.002099Z`, with no duplicate, restart, or fail-safe.
The session was verified as Astra/low before launch. The baseline project
profile specified default service tier. No worker or unrelated task ran during
the interval. Normal terminal waits returned through Code Mode and the parent
re-armed the same session after timeouts.

One brief hourly wait-status message was required by the host, so this is a
qualified baseline rather than a fully silent control. The 26-round estimate
is best effort. Both subscription snapshots were active: the five-hour reset
remained `2026-10-02T01:23:42Z` and weekly reset remained
`2026-10-08T15:20:23Z`. The before snapshot finished about 27.8 seconds before
target start; finalization finished about 11.6 seconds after target completion.
The quota delta includes those boundary intervals. Six parser tests passed.

## Raw evidence files

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261002T000931Z-codex-baseline/`. Raw session transcripts are **not copied into this repository**.
