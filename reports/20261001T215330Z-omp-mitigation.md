# Usage-drain test report: 20261001T215330Z-omp-mitigation

- Date/time started: `2026-10-01T21:54:07.872688Z`
- Date/time finished: `2026-10-01T22:55:53.629039Z`
- Mode: **mitigation**
- Model: **gpt-6-astra**
- Reasoning effort: **low**
- Authentication/billing basis: **ChatGPT subscriber quota via Codex/OpenAI Codex OAuth; no API pricing used**
- Target status: **completed**
- Pre-completion model-round estimate: **3** (confidence: medium)

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after | 5-hour drain | Weekly drain |
|---|---|---:|---:|---:|---:|---:|---:|
| omp | omp/18.4.9 | 79.00% | 90.00% | 79.00% | 90.00% | 0.00 pp | 0.00 pp |

## Model activity during deterministic sleep

```json
{
  "agent": "omp",
  "confidence": "medium",
  "counts": {
    "assistant_message": 3,
    "auxiliary_model_usage": 0,
    "sampling": 0
  },
  "interpretation": "Rounds strictly after target start and before target completion are unnecessary for learning that this deterministic sleeper is still running. Auxiliary OMP model_usage entries are included when present.",
  "pre_completion_model_rounds": 3,
  "records_in_window": 9,
  "session_logs_read": 2,
  "window_end_utc": "2026-10-01T22:55:41.361012Z",
  "window_start_utc": "2026-10-01T21:54:11.355589Z"
}
```

The interval above ends at the target's own `completed` timestamp. A model turn caused by actual completion is therefore not counted as an unnecessary wake.

## Validity and timing

- **Valid under the repository checklist.** Before launch, baseline PID `33528` was absent, its completion marker was present, and no harness trial process was running.
- Parent session recorded `openai-codex/gpt-6-astra` with `low` reasoning. Worker session recorded `openai-codex/gpt-5.6-luna` with `low` reasoning and no model fallback.
- Exactly one target was launched (PID `45755`), from `2026-10-01T21:54:11.355589Z` to `2026-10-01T22:55:41.361012Z`: 3690 seconds, no fail-safe event. Its process had exited at final verification.
- `omp usage invalidate --provider openai-codex` immediately preceded both snapshot commands. Both snapshots reported active ChatGPT/Codex OAuth subscription telemetry.
- The 5-hour reset remained `2026-10-02T01:23:42Z`; the weekly reset remained `2026-10-08T15:20:23Z`. Neither reset crossed the measurement interval.
- The parent remained idle inside the blocking monitor dispatch: **0 parent / 3 worker** pre-completion assistant rounds. All three worker rounds only continued the same wait; no unrelated work occurred during the target interval.
- The refresh/finalization command was issued at `2026-10-01T22:55:46.885Z`, approximately **5.524 seconds after completion**. Report finalization finished **12.268 seconds after completion**. The quota interval includes this short post-completion overhead and the pre-launch gap; it is not an exact sleep-only interval.
- Both parent and worker session logs were supplied to the finalizer. Worker log: `~/.omp/agent/sessions/-projects-codex-usage-drain-lab/2026-10-01T20-27-25-175Z_01a0f926-8077-7097-8660-4c009666a686/MitigationMonitor.jsonl`; parent log is the adjacent `2026-10-01T20-27-25-175Z_01a0f926-8077-7097-8660-4c009666a686.jsonl`.
- Zero percentage-point movement is the observed subscription telemetry resolution, not evidence of zero token consumption. This single trial does not establish a causal improvement over baseline.
- Six parser tests passed before measurement. No second mitigation trial was launched.

## Raw evidence

Raw before/after usage JSON, target timestamps, metadata, and the optional round counter are stored under `reports/raw/20261001T215330Z-omp-mitigation/`. Raw session transcripts are **not copied into this repository**.
