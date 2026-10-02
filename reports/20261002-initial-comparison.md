# Initial subscriber-quota experiment comparison

Follow-up: [Codex repeats with host and CLI both verified as 0.160.0](20261002-codex-0160-repeat-comparison.md).

All four completed trials used an Astra/low parent and a single 3690-second target. Trials were sequential and used subscription telemetry, with no subscription reset crossing an included trial. Raw private transcripts remain uncommitted.

| Trial | Recorded version | Initial 5h / weekly remaining | 5h drain | Weekly drain | Pre-completion parent / worker rounds |
|---|---|---|---:|---:|---:|
| [Codex baseline](20261001T181408Z-codex-baseline.md) | CLI 0.159.3; host not separately recorded | 69% / 95% | 10 pp | 1 pp | 26 / 0 |
| [Codex mitigation](20261001T225924Z-codex-mitigation.md) | Host 0.160.0; probe CLI 0.159.3 | 71% / 89% | 3 pp | 1 pp | 1 / 0 |
| [OMP baseline](20261001T202930Z-omp-baseline.md) | 18.4.9 | 90% / 92% | 2 pp | 1 pp | 3 / 0 |
| [OMP mitigation](20261001T215330Z-omp-mitigation.md) | 18.4.9 | 79% / 90% | 0 pp | 0 pp | 0 / 3 |

Codex mitigation kept terminal re-arming inside a deterministic Code Mode loop. OMP mitigation assigned waiting to one Luna/low worker. These are different mitigation strategies. All round counts are best effort; Codex used sampling records and OMP used assistant-message records, so cross-client counts are not identical instrumentation.

Both mitigation trials observed fewer parent returns and less five-hour quota movement than their respective baselines. This is descriptive evidence from one trial per condition, not a causal estimate or a client ranking. Zero reported quota movement does not mean zero token consumption.

## Comparison limits

- Codex sent one host-required hourly wait-status message in each included trial. These are qualified measurements rather than fully silent controls.
- OMP baseline finalization was delayed about 15m22s after completion. OMP mitigation finalization finished after 12.268s; Codex baseline after about 40s; Codex mitigation after about 24s. Quota deltas include unequal boundary intervals.
- Initial quota headroom differed, especially between the OMP trials. The Codex host version was not separately recorded for the baseline; matching CLI versions do not establish identical runtime versions.
- Correction: the observed host/CLI version difference in the first mitigation does **not** establish an upgrade between the first baseline and mitigation. The user reports that the actual CLI upgrade occurred after those trials. Repeat trials explicitly record both versions as 0.160.0.
- The [first Codex attempt](20261001T171106Z-codex-baseline.md) is invalid because both saved quota snapshots were unknown. It is excluded from this table.

Repeat baseline/mitigation pairs on verified matching host versions, similar initial headroom, and prompt post-completion snapshots before drawing stronger conclusions. No additional repeated trial was launched as part of this comparison.
