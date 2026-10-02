# Usage-drain test report: 20261002T065619Z-codex-baseline

- Date/time started: `2026-10-02T06:56:21.149904Z`
- Date/time finished: `2026-10-02T07:58:19.939148Z`
- Mode: **baseline**
- Model: **gpt-6.1-sol**
- Reasoning effort: **max**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Active host version: **0.160.0**, recorded separately in metadata; installed CLI also **0.160.0**.
- Pre-completion model-round estimate: **26** (confidence: high)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| codex | codex-cli 0.160.0 | 100.00% | 82.00% | 97.00% | 81.00% | 3.00 pp | 1.00 pp |

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
  "records_in_window": 110,
  "session_logs_read": 1,
  "window_end_utc": "2026-10-02T07:58:07.566523Z",
  "window_start_utc": "2026-10-02T06:56:37.560809Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Protocol checks and qualification

- This is the additional Sol/Max baseline explicitly requested by the user, overriding the standard Astra/low requirement for this trial. Active rollout contexts throughout the target interval recorded `gpt-6.1-sol` / `max`. The dedicated profile specified default service tier.
- Exactly one target ran from `2026-10-02T06:56:37.560809Z` to `2026-10-02T07:58:07.566523Z`, completing 3690 seconds without a duplicate, restart, or fail-safe. No worker, mitigation loop, or unrelated task ran during the interval.
- The baseline used the same terminal waiting mechanism as the Astra trials: after terminal timeouts, the parent continued waiting on the original session through Code Mode. The counter found 26 sampling records before completion. This is best-effort evidence of model activity while the target was still sleeping, not a direct measurement of per-request quota charges.
- One brief hourly status message was required by the host, as in the Codex comparison trials. This makes the run a qualified baseline rather than a fully silent control. An environment-date update also arrived during the interval; it introduced no task or unrelated work.
- Both saved snapshots contain active subscription telemetry. The five-hour reset remained `2026-10-02T11:24:51Z` and the weekly reset remained `2026-10-08T15:20:23Z`; neither reset crossed the trial. The separate reserve-model quota was excluded from the named windows.
- The before snapshot finished about 16.4 seconds before target start; report finalization finished about 12.4 seconds after completion. The quota interval includes these boundary intervals and completion handling. Six parser tests passed.

## Comparison with Astra baselines

| Codex baseline | Model / effort | Host / CLI | Five-hour drain | Weekly drain | Pre-completion rounds |
|---|---|---|---:|---:|---:|
| [Original Astra](20261001T181408Z-codex-baseline.md) | Astra / low | Host not separately recorded / 0.159.3 | 10 pp | 1 pp | 26 |
| [Repeated Astra](20261002T000931Z-codex-baseline.md) | Astra / low | 0.160.0 / 0.160.0 | 15 pp | 2 pp | 26 |
| This trial | Sol / max | 0.160.0 / 0.160.0 | 3 pp | 1 pp | 26 |

At matching host/CLI versions, Sol/Max showed 12 percentage points less
five-hour movement than the repeated Astra/low baseline, despite the same
estimated number of pre-completion rounds. That is consistent with the user's
prediction of lower subscriber drain for this model condition while repeated
inference occurs during waiting. It does not establish the subscription's
model weighting or isolate inference as the sole cause of quota movement.

Both model and reasoning effort changed. Starting five-hour/weekly headroom
was 100%/82% for Sol versus 60%/87% for repeated Astra; the runs occurred in
different five-hour windows and later portions of the same accumulating
conversation. Cached context, backend accounting, and percentage resolution
can affect the observations. This is one Sol trial, not a controlled causal
estimate, and no API price or dollar conversion was used.

See the [comparison across all completed conditions](20261002-sol-max-comparison.md).

## Raw evidence

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261002T065619Z-codex-baseline/`. Raw session transcripts are **not copied into this repository**.
