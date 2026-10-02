# Usage-drain test report: 20261002T012430Z-codex-mitigation

- Date/time started: `2026-10-02T01:24:32.401555Z`
- Date/time finished: `2026-10-02T02:26:29.196370Z`
- Mode: **mitigation**
- Model: **gpt-6-astra**
- Reasoning effort: **low**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Active host version: **0.160.0**, recorded separately in metadata and rechecked after completion; installed CLI also **0.160.0**.
- Pre-completion model-round estimate: **1** (confidence: high)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| codex | codex-cli 0.160.0 | 98.00% | 84.00% | 95.00% | 83.00% | 3.00 pp | 1.00 pp |

## Model activity during deterministic sleep

```json
{
  "agent": "codex",
  "confidence": "high",
  "counts": {
    "assistant_message": 1,
    "auxiliary_model_usage": 0,
    "sampling": 1
  },
  "interpretation": "Rounds strictly after target start and before target completion are unnecessary for learning that this deterministic sleeper is still running. Auxiliary OMP model_usage entries are included when present.",
  "pre_completion_model_rounds": 1,
  "records_in_window": 6,
  "session_logs_read": 1,
  "window_end_utc": "2026-10-02T02:26:17.483611Z",
  "window_start_utc": "2026-10-02T01:24:47.477228Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Protocol qualification

One target completed from `2026-10-02T01:24:47.477228Z` to
`2026-10-02T02:26:17.483611Z`, with no duplicate, restart, or fail-safe.
The parent remained Astra/low, with the mitigation profile specifying default
service tier. No model worker or unrelated task ran during the target interval.

One Code Mode execution launched the target and re-armed 13 terminal waits on
that same session, requesting up to 300 seconds each. The outer execution
yielded after 3500 seconds, leading to one brief host-required hourly status
message and a wait on the same execution cell. This is a qualified measurement
with **1 parent / 0 worker** pre-completion rounds, estimated on a best-effort
basis. The mitigation is deterministic tool orchestration, not a Luna-monitor
trial or proof of hot-reloading the configured terminal timeout.

Both subscription snapshots were active. The five-hour reset remained
`2026-10-02T06:24:18Z` and weekly reset remained `2026-10-08T15:20:23Z`.
The five-hour reset occurred between the repeated baseline and this mitigation,
not within either trial. The before snapshot finished about 15.1 seconds before
target start; report finalization finished about 11.7 seconds after completion.
Quota deltas include these boundary intervals. Six parser tests passed.

## Raw evidence files

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261002T012430Z-codex-mitigation/`. Raw session transcripts are **not copied into this repository**.
