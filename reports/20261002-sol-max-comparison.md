# Sol/Max baseline compared with prior subscriber-quota trials

The requested GPT-6.1 Sol/Max baseline completed one 3690-second target on
Codex host and CLI 0.160.0. Subscription remaining fell from 100% to 97% in
the five-hour window and from 82% to 81% in the weekly window. The best-effort
counter recorded 26 model sampling records strictly before target completion.

| Condition | Parent / effort | Recorded client version | Initial 5h / weekly remaining | Five-hour drain | Weekly drain | Pre-completion parent / worker rounds |
|---|---|---|---|---:|---:|---:|
| [Codex baseline, original](20261001T181408Z-codex-baseline.md) | Astra / low | CLI 0.159.3; host not separately recorded | 69% / 95% | 10 pp | 1 pp | 26 / 0 |
| [Codex mitigation, original](20261001T225924Z-codex-mitigation.md) | Astra / low | Host 0.160.0; CLI 0.159.3 | 71% / 89% | 3 pp | 1 pp | 1 / 0 |
| [Codex baseline, repeated](20261002T000931Z-codex-baseline.md) | Astra / low | Host and CLI 0.160.0 | 60% / 87% | 15 pp | 2 pp | 26 / 0 |
| [Codex mitigation, repeated](20261002T012430Z-codex-mitigation.md) | Astra / low | Host and CLI 0.160.0 | 98% / 84% | 3 pp | 1 pp | 1 / 0 |
| [Codex Sol baseline](20261002T065619Z-codex-baseline.md) | Sol / max | Host and CLI 0.160.0 | 100% / 82% | 3 pp | 1 pp | 26 / 0 |
| [OMP baseline](20261001T202930Z-omp-baseline.md) | Astra / low | OMP 18.4.9 | 90% / 92% | 2 pp | 1 pp | 3 / 0 |
| [OMP mitigation](20261001T215330Z-omp-mitigation.md) | Astra / low | OMP 18.4.9 | 79% / 90% | 0 pp | 0 pp | 0 / 3 |

All included targets completed 3690 seconds, ran sequentially, and had no
subscription reset inside their before/after intervals. The first Codex
attempt with missing quota snapshots is excluded. Zero reported quota movement
does not mean zero inference or zero token use.

## What this says about waiting and model activity

The Codex baselines each recorded 26 pre-completion sampling records even
though the target was still sleeping. The Sol/Max baseline showed 3 pp of
five-hour movement versus 15 pp for Astra/low at matching recorded versions.
The observed lower movement is consistent with the prediction that changing
the model condition can reduce subscriber drain while timeout-driven model
returns continue. The same round count also shows that choosing Sol did not
remove those model returns.

Moving repeated terminal waits inside deterministic orchestration reduced
Astra's estimated parent rounds from 26 to 1 in the mitigation trials, with
observed five-hour movement of 3 pp. Sol baseline's matching 3 pp movement
does not imply the same per-request cost or mechanism. This experiment records
subscriber-window movement, not API billing or a model pricing ratio.

## Limits of the comparison

- Sol/Max versus Astra/low changes both model and effort. A Sol/low trial or other matched-effort experiment would be needed to separate those effects; none was run here.
- Starting headroom, reset windows, and accumulated conversation context differed. Sampling records support model activity during waiting, but percentage deltas do not directly attribute every quota charge to those records.
- Each Codex trial included one host-required hourly status message. Round counts remain best effort. OMP counts use assistant-message records, unlike Codex sampling records.
- OMP baseline finalization was delayed about 15m22s. Other included finalizations finished roughly 12–40 seconds after completion; each also has a short pre-launch gap. Those unequal boundary intervals are included in quota deltas.
- Earlier host/CLI differences did not establish an upgrade between the original Astra trials. Both repeat Astra trials and Sol explicitly recorded host and CLI 0.160.0.

The evidence supports further matched trials; it does not establish causation
or a general client/model ranking. No additional trial was launched after the
requested Sol/Max baseline.
