# Codex repeat comparison: host and CLI 0.160.0

Both repeated trials explicitly recorded Codex host **0.160.0** and installed
CLI **0.160.0**, using Astra/low and the default-tier project profiles. Each
completed one 3690-second target with no duplicate, restart, fail-safe, or
subscription reset inside the trial. No worker was used.

| Trial | 5-hour before → after | 5-hour drain | Weekly before → after | Weekly drain | Pre-completion parent rounds |
|---|---|---:|---|---:|---:|
| [Baseline](20261002T000931Z-codex-baseline.md) | 60% → 45% | 15 pp | 87% → 85% | 2 pp | 26 |
| [Mitigation](20261002T012430Z-codex-mitigation.md) | 98% → 95% | 3 pp | 84% → 83% | 1 pp | 1 |

The mitigation kept terminal re-arming inside one deterministic Code Mode
execution. Baseline timeouts returned to the model, which continued waiting on
the same terminal session. Round counts are best effort, using sampling records
strictly between target start and completion. Each trial included one hourly
wait-status message required by the host.

The observed five-hour delta was 12 percentage points lower in mitigation.
This is an observation, not a causal effect estimate: a five-hour reset occurred
**between** trials, their starting headroom differed, and they ran sequentially
in an accumulating conversation context. Neither measurement spans that reset.
Baseline finalization finished about 11.6 seconds after target completion;
mitigation finalization finished about 11.7 seconds after completion. Quota
intervals also include the short pre-launch gaps documented in each report.

## Correction to the earlier version interpretation

The first mitigation observed host 0.160.0 alongside CLI 0.159.3. That did not
prove that the host upgraded between the original baseline and mitigation.
The user reports performing the actual CLI upgrade after those trials. The
earlier baseline did not separately record its host version, so the historical
host change remains unestablished. These repeats remove that version ambiguity
by recording both host and CLI in each run's metadata.

The earlier [four-trial comparison](20261002-initial-comparison.md) remains a
separate descriptive result set. Do not interpret differences between earlier
and repeated quota deltas as a release regression or improvement from these
samples alone.
