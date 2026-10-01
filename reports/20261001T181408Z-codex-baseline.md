# Usage-drain test report: 20261001T181408Z-codex-baseline

**Usable subscription measurement, with a baseline protocol deviation noted below.**
The single target completed its 3690-second interval without a fail-safe or
replacement. No unrelated work occurred during the interval. The rollout records
`gpt-6-astra` / `low`; the project profile specifies the default service tier.
Both snapshots contain subscription telemetry. The five-hour reset stayed at
`2026-10-01T20:20:23Z` and the weekly reset at `2026-10-08T15:20:23Z`.

The host requires communication within each hour, so one brief wait-status
message was sent during the target interval. This deviates from the requested
silent baseline and is included in the observed workload. Treat this as a
qualified baseline, not a perfectly silent control. The round count is best
effort despite the counter's `high` confidence label. A single run does not
establish that waiting alone caused the quota delta.

The saved before snapshot preceded target start by about 14 seconds; the after
snapshot was taken about 40 seconds after completion, including approval delay.
Quota movement therefore also includes those boundary intervals. Snapshot
commands ran outside the sandbox after nested probes failed inside it.

The earlier `20261001T171106Z-codex-baseline` attempt is invalid and excluded
from quota comparisons. Harness changes used for this trial select the Codex
weekly bucket rather than the reserve-model bucket and reject incomplete
pre-run telemetry or a reset within 3900 seconds.

- Date/time started: `2026-10-01T18:14:10.183661Z`
- Date/time finished: `2026-10-01T19:16:34.713266Z`
- Mode: **baseline**
- Model: **gpt-6-astra**
- Reasoning effort: **low**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Pre-completion model-round estimate: **26** (confidence: high)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| codex | codex-cli 0.159.3 | 69.00% | 95.00% | 59.00% | 94.00% | 10.00 pp | 1.00 pp |

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
  "window_end_utc": "2026-10-01T19:15:54.060071Z",
  "window_start_utc": "2026-10-01T18:14:24.054418Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Raw evidence

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261001T181408Z-codex-baseline/`. Raw session transcripts are **not copied into this repository**.
