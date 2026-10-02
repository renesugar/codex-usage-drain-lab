# Usage-drain test report: 20261001T225924Z-codex-mitigation

- Date/time started: `2026-10-01T22:59:26.366378Z`
- Date/time finished: `2026-10-02T00:01:30.852611Z`
- Mode: **mitigation**
- Model: **gpt-6-astra**
- Reasoning effort: **low**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Active Codex host version: **0.160.0** (`CODEX_VERSION` and host executable path); the separately installed quota-probe CLI is **0.159.3**.
- Pre-completion model-round estimate: **1** (confidence: high)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| codex | host 0.160.0; probe CLI 0.159.3 | 71.00% | 89.00% | 68.00% | 88.00% | 3.00 pp | 1.00 pp |

## Protocol and wait strategy

- Usable subscription measurement with a documented hourly communication qualification. Astra/low was verified in the active rollout; the installed mitigation profile specifies default service tier. No model worker was spawned.
- Host process inspection found no pre-existing target. Exactly one target ran from `2026-10-01T22:59:36.888002Z` to `2026-10-02T00:01:06.893798Z`, exiting successfully after 3690 seconds with no fail-safe, restart, or unrelated work.
- One Code Mode execution launched the target and deterministically re-armed empty terminal waits on that same session. It made 13 terminal wait calls, each requesting up to 300 seconds, without model reasoning between those calls. This measures deterministic tool orchestration, not a Luna-monitor strategy or proof that the installed 65-minute terminal setting hot-reloaded.
- The outer execution yielded after 3500 seconds. One parent round sent a brief status message and waited for the same execution cell to complete, satisfying the host's requirement for communication within an hour. The estimated split is **1 parent / 0 worker** pre-completion rounds. The estimate remains best effort despite the counter's `high` confidence label.
- Both snapshots contain active subscription telemetry. The five-hour reset remained `2026-10-02T01:23:42Z`; the weekly reset remained `2026-10-08T15:20:23Z`. No subscription reset crossed the interval. The separate reserve-model bucket was excluded from the reported named windows.
- The before snapshot finished about 10.5 seconds before target start; report finalization finished about 24 seconds after target completion. Quota deltas include these boundary intervals and completion handling, not only the sleep.
- Six parser tests passed before launch. The host and CLI version distinction limits comparison with the earlier baseline, whose report captured only the CLI version. This single trial does not establish causation.

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
  "window_end_utc": "2026-10-02T00:01:06.893798Z",
  "window_start_utc": "2026-10-01T22:59:36.888002Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Raw evidence

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261001T225924Z-codex-mitigation/`. Raw session transcripts are **not copied into this repository**.
