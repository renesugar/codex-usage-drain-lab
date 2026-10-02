# Codex / OMP subscriber usage-drain harness

This repository is a reproducible harness for measuring **ChatGPT subscriber quota drain** while a coding agent waits for a deterministic long-running command. It is designed around the specific failure mode where a reasoning model wakes repeatedly just to learn that a process is still running.

The primary baseline target sleeps for **61 minutes 30 seconds (3690 s)**. Its own hard fail-safe fires at **65 minutes (3900 s)**. In the expected success case the fail-safe never fires: the process completes at a known time and the coding agent should be idle until completion is observable.

The primary agents under test are:

- **Codex**, using `gpt-6-astra` with **low** reasoning effort.
- **OMP (Oh My Pi)**, using `openai-codex/gpt-6-astra:low`.

Both tests are explicitly subscription tests. They use the user's **ChatGPT/Codex subscription authentication**. Do **not** substitute OpenAI API-key billing and do **not** estimate cost from API prices. The measured quantities are the 5-hour and weekly subscription windows exposed by the installed clients.

## What is measured

Each run records:

- coding-agent name and exact installed version;
- model and reasoning effort;
- 5-hour remaining percentage before and after;
- weekly remaining percentage before and after;
- percentage-point drain during the test;
- deterministic target start/completion timestamps;
- when session logs are supplied, a best-effort count of model rounds strictly **after target start and before target completion**.

That last interval is useful because any reasoning-model round inside it cannot have been required to discover completion: the target has not completed yet. The normal completion turn occurs after the target's own `completed` timestamp and is excluded.

## Source lineage

The usage checker is derived from the model-free preflight approach in the `develop` branch of [`renesugar/notrios`](https://github.com/renesugar/notrios/tree/develop), especially `scripts/check_agent_usage.py` and `scripts/agent_usage_preflight.sh`.

The current Notrios `develop` checker probes Codex with local `account/rateLimits/read` and Claude from a local cache. At the time this harness was created, that branch did **not** yet contain `opencode2` support despite earlier workflow notes referring to it. This harness adds:

- `omp`: `omp usage --json --provider openai-codex`, which uses the ChatGPT/Codex OAuth usage endpoint;
- `opencode2`: informational `stats --json` support only. It is **not** treated as a source of ChatGPT 5-hour/weekly quota unless its client later exposes those windows.

OMP's `openai-codex` provider is the subscription/OAuth route. The API-key based `openai` provider is intentionally not used by this harness.

## Repository layout

```text
.codex/config.toml                active Codex project profile
.omp/config.yml                   active OMP project profile
.omp/agents/wait-monitor.md       mitigation worker
configs/                          baseline/mitigation profiles
prompts/                          handoff prompts for measured runs
reports/                          generated Markdown reports
scripts/check_agent_usage.py      non-model usage probe
scripts/test_check_agent_usage.py parser tests
scripts/wait_target.py            61m30s deterministic target
scripts/start_run.py              capture pre-run usage + metadata
scripts/finish_run.py             capture post-run usage + report
scripts/count_model_rounds.py     best-effort pre-completion wake counter
scripts/select_profile.py         switch baseline/mitigation project config
```

Raw probe data is written under `reports/raw/` and ignored by Git. Finished Markdown reports remain under `reports/` and are intended to be committed.

## Before running a real test

Run the parser tests and check both subscription probes without invoking a model:

```bash
python3 scripts/test_check_agent_usage.py
python3 scripts/check_agent_usage.py --agent codex --json
python3 scripts/check_agent_usage.py --agent omp --json
```

For Codex, the probe uses the local app-server's `account/rateLimits/read`; it never runs `codex exec /status` and does not spend a model turn just to measure usage.

For OMP, ensure the **`openai-codex`** provider is authenticated. If `omp usage --provider openai-codex` cannot read the subscription window, fix that before testing. Do not work around it by setting `OPENAI_API_KEY` and switching to the API-billed `openai` provider.

## Baseline run: Codex

Install the baseline project profile:

```bash
python3 scripts/select_profile.py codex baseline
```

Then launch Codex from the repository root. The project config pins Astra/low. Give it [`prompts/codex-baseline.md`](prompts/codex-baseline.md).

The run protocol inside the agent is:

```bash
RUN_ID=$(python3 scripts/start_run.py --agent codex --mode baseline)
python3 scripts/wait_target.py --log "reports/raw/$RUN_ID/target.jsonl"
# agent waits for the same terminal session; do not start a duplicate target
python3 scripts/finish_run.py --run-id "$RUN_ID" --session-log <codex-rollout-jsonl>
```

The important experimental condition is that the **coding agent**, not an external wrapper, owns the wait. It should use its normal/default wait behavior in the baseline. Every timeout-driven re-entry is part of what the baseline is intended to measure.

## Baseline run: OMP

Install the baseline profile:

```bash
python3 scripts/select_profile.py omp baseline
```

Launch from this repository. The project `.omp/config.yml` selects:

```text
openai-codex/gpt-6-astra:low
```

Use [`prompts/omp-baseline.md`](prompts/omp-baseline.md). If desired, import the already-tested Codex conversation context:

```bash
omp --from-codex <codex-session-id> --approval-mode always-ask --cwd "$PWD"
```

Importing a session is optional. Keep the actual measured run separate: take a fresh **before** quota snapshot immediately before the target is launched.

## Additional Sol/Max baseline

An additional user-requested condition uses `gpt-6.1-sol` with `max` reasoning
effort and default service tier. This overrides the standard Astra/low setting
only for that explicitly selected experiment. Use
[`prompts/codex-sol-max-baseline.md`](prompts/codex-sol-max-baseline.md) and
`python3 scripts/select_profile.py codex sol-max-baseline`. Verify the active
session's model; installing a profile alone does not establish a model switch.
Pass `--model gpt-6.1-sol --effort max` to `start_run.py`.

The [Sol/Max comparison](reports/20261002-sol-max-comparison.md) records the
additional baseline alongside the Astra and OMP trials. It compares subscriber
quota movement without API-price conversions.

## Mitigation runs

Mitigation runs deliberately change the wait strategy while keeping the main model Astra/low.

### Codex mitigation

```bash
python3 scripts/select_profile.py codex mitigation
```

The mitigation profile:

- raises `background_terminal_max_timeout` to 65 minutes for an empty terminal wait;
- leaves the parent on Astra/low;
- enables one subagent at a time;
- routes the default subagent to `gpt-5.6-luna` at low effort.

Use [`prompts/codex-mitigation.md`](prompts/codex-mitigation.md). The parent should prefer a long blocking/event-driven wait. When a monitoring worker is needed, that worker should do the waiting and return only on completion/failure/fail-safe. The worker is a mitigation—not the target architecture. Zero-model deterministic notification remains preferable.

### OMP mitigation

```bash
python3 scripts/select_profile.py omp mitigation
```

The project agent `.omp/agents/wait-monitor.md` is routed through `@wait_monitor` to `openai-codex/gpt-5.6-luna:low`. `task.enableEffort: false` prevents a task-level coarse effort hint from replacing the configured low-effort role during this experiment.

Use [`prompts/omp-mitigation.md`](prompts/omp-mitigation.md).

## Session-log discovery and wake counting

The harness never copies complete private transcripts into the repository. Find likely session files with:

```bash
python3 scripts/find_recent_session.py --agent codex
python3 scripts/find_recent_session.py --agent omp
```

Pass the relevant file(s) to `finish_run.py` using repeated `--session-log` arguments. For an OMP mitigation run, include both the parent and monitoring-worker logs when available.

The counter is intentionally labeled **best effort**. Subscription before/after measurements are authoritative for the experiment even when model-round counting is unavailable.

## Report format

Every finished run produces `reports/<run-id>.md` with at least:

| Coding agent | Coding agent version | 5-hour remaining before | Weekly remaining before | 5-hour remaining after | Weekly remaining after |
|---|---|---:|---:|---:|---:|
| codex / omp | captured at runtime | captured | captured | captured | captured |

It also includes calculated percentage-point drain and the pre-completion round estimate when available.

## GitHub issue inventory

The [waiting-inference analysis](reports/20261002-waiting-inference-analysis.md)
collects the subscriber-quota results, source-backed mechanism, prompt-policy
findings, mitigation distinctions, and recommendations for updating existing
Codex issues. Its Codex source links point to the inspected GitHub revision.

Status/assignment snapshot refreshed **2026-10-01**. “Usage-drain severity” is this harness's impact classification, not an OpenAI/GitHub severity label. “Cause confidence” distinguishes concrete code/telemetry evidence from reports that primarily establish a symptom. None of the open issues below had a GitHub assignee when refreshed.

| Issue | Title | Status | Assigned | Usage-drain severity | Category | Cause confidence |
|---|---|---|---|---|---|---|
| [#35259](https://github.com/openai/codex/issues/35259) | Codex Desktop repeatedly re-enters the model during wait/status polling, consuming substantial credits | Open | No | **Critical** | Request-count amplification / waits | Code + telemetry |
| [#35108](https://github.com/openai/codex/issues/35108) | [Codex Desktop] Nested functions.exec wait_agent polling causes repeated parent turns and token usage | Open | No | **High** | Request-count amplification / waits | Code + reproduction |
| [#42981](https://github.com/openai/codex/issues/42981) | Built-in 60-second update/wait instructions override explicit user requests for infrequent monitoring | Open | No | **High** | Prompt policy / waits | Prompt + reproduction |
| [#31935](https://github.com/openai/codex/issues/31935) | Remove the 60-second limit on blocking waits | Open | No | **Medium** | Prompt/runtime wait policy | Architectural |
| [#33542](https://github.com/openai/codex/issues/33542) | Event-driven background task callbacks | Open | No | **Medium** | Event-driven solution | Architectural proposal |
| [#32188](https://github.com/openai/codex/issues/32188) | Event-driven wakeup when background exec sessions complete | Open | No | **High** | Missing completion wake | Code-level gap |
| [#18526](https://github.com/openai/codex/issues/18526) | First message in fresh session consumes ~100k input tokens immediatly, no matter how trivial the input | Closed (completed) | No | **High** | Initial context size | Observed symptom |
| [#14593](https://github.com/openai/codex/issues/14593) | Burning tokens very fast | Closed (completed) | No | **High** | General rapid usage | Observed symptom |
| [#29955](https://github.com/openai/codex/issues/29955) | Quota drained instantly: 100 credits gone after 1 message, 5h limit reset to 0% | Open | No | **Critical** | Quota/accounting | Strong symptom; backend cause unknown |
| [#30918](https://github.com/openai/codex/issues/30918) | Usage limits draining abnormally fast on Plus: 70% to 100% in about 6 minutes on July 2, 2026 | Open | No | **Critical** | Quota/accounting | Strong telemetry |
| [#33685](https://github.com/openai/codex/issues/33685) | Weekly limit is draining like the old 5-hour limit | Open | No | **Critical** | Quota/accounting | Strong symptom; backend cause unknown |
| [#26791](https://github.com/openai/codex/issues/26791) | Token consumption without use | Open | No | **High** | Background/accounting | Observed symptom |
| [#30081](https://github.com/openai/codex/issues/30081) | Pro 5x subscription ended early and quota is draining while idle after renewal | Open | No | **Critical** | Background/accounting | Observed symptom |
| [#41957](https://github.com/openai/codex/issues/41957) | [Bug] ChatGPT Plus quota consumption increased ~9x between comparable Codex App tasks | Open | No | **Critical** | Quota/accounting / weighting | Strong comparative telemetry |
| [#44386](https://github.com/openai/codex/issues/44386) | [Bug] Codex Desktop replays ~150k cached input per tool call and rapidly drains Plus usage | Open | No | **Critical** | Context/schema replay | Strong telemetry |
| [#40897](https://github.com/openai/codex/issues/40897) | [Bug] Code Mode nested exec output truncation causes repeated context growth and extreme cached-token quota consumption | Open | No | **Critical** | Tool-output/context amplification | Strong telemetry |
| [#43287](https://github.com/openai/codex/issues/43287) | Linux Desktop: codex-auto-review continues under approval_policy=on-request and amplifies quota usage | Open | No | **High** | Auxiliary auto-review calls | Strong local evidence |
| [#39408](https://github.com/openai/codex/issues/39408) | Auto-review can cause runaway quota consumption when Windows sandbox bugs repeatedly escalate workspace-local operations | Open | No | **Critical** | Auxiliary auto-review calls | Strong mechanism/report |
| [#39808](https://github.com/openai/codex/issues/39808) | Subagent fan-out can increase usage because each agent pays fixed context/tool/skill overhead | Open | No | **High** | Multi-agent fixed overhead | Architectural mechanism |
| [#46023](https://github.com/openai/codex/issues/46023) | [Bug][Desktop][Subagents] One task processed 242.3M tokens and consumed 11 percentage points of weekly quota in 2h44m | Open | No | **Critical** | Multi-agent/context amplification | Strong telemetry |
| [#43229](https://github.com/openai/codex/issues/43229) | Windows 0.153.4: high usage with V2 workers, Code Mode truncation and effort-change cache misses (local telemetry) | Open | No | **High** | Multi-agent/cache invalidation | Strong telemetry |
| [#35458](https://github.com/openai/codex/issues/35458) | Codex Desktop: screenshots re-persisted in full on every compaction and inherited by subagent forks - ~/.codex/sessions reached ~165 GiB (95% base64 images) | Open | No | **High** | Compaction/media duplication | Strong context/storage evidence |
| [#42702](https://github.com/openai/codex/issues/42702) | Codex Desktop scheduled automation can replay 128K–146K context per call and consume >1.08M tokens in under a minute | Open | No | **Critical** | Background automation/context replay | Strong telemetry |
| [#45383](https://github.com/openai/codex/issues/45383) | [Usage/Resume] Interrupted Codex sessions waste quota rebuilding context instead of finishing work | Open | No | **High** | Resume/reconstruction tax | Strong workflow observation |
| [#27131](https://github.com/openai/codex/issues/27131) | Codex self-ingests local session JSONL logs during token-usage investigation, causing runaway token growth | Open | No | **High** | Tool-selection/context self-ingestion | Strong reproduction |
| [#43136](https://github.com/openai/codex/issues/43136) | Session pinned to wrong rate_limits bucket (codex_bengalfox) while concurrent sessions on the same account receive the correct codex bucket | Open | No | **Critical** | Quota bucket/accounting | Strong telemetry |
| [#38157](https://github.com/openai/codex/issues/38157) | ChatGPT Pro (20x) accounts appear to receive Pro 5x Codex usage capacity | Open | No | **Critical** | Entitlement/provisioning | Strong symptom; backend cause unknown |
| [#39260](https://github.com/openai/codex/issues/39260) | Credit usage ledger frozen since Aug 8, 2026 — 45,252 of 53,000 purchased credits (85.4%) consumed with zero usage records; ongoing | Open | No | **Critical** | Ledger/auxiliary usage attribution | Strong accounting evidence |
| [#37445](https://github.com/openai/codex/issues/37445) | Opening the ChatGPT desktop app silently consumes the Codex weekly limit (fixed 6% per background suggestion run; reproduced under controlled conditions) | Open | No | **Critical** | Background activity | Controlled observation |
| [#42282](https://github.com/openai/codex/issues/42282) | Chronicle background captures consume quota with no attribution in any usage surface (repro script included) | Open | No | **Critical** | Background capture/summarization | Strong local evidence |
| [#44884](https://github.com/openai/codex/issues/44884) | Extreme cached-context amplification in long-running tool-heavy Codex sessions | Open | No | **Critical** | Context replay | Strong telemetry |
| [#44305](https://github.com/openai/codex/issues/44305) | Codex tool loop causes context snowballing and multi-million-token input amplification | Open | No | **High** | Tool-loop/context amplification | Strong telemetry |
| [#41450](https://github.com/openai/codex/issues/41450) | [Code Mode] Reproducible token amplification: one AGENTS.md rule cut cumulative input by 81.6% | Open (reopened) | No | **High** | Outer-cycle scheduling | Controlled A/B evidence |
| [#41220](https://github.com/openai/codex/issues/41220) | [Meta] Abnormal Codex usage/quota depletion and usage-accounting inconsistencies — cross-report tracker | Open | No | **Meta / Critical family** | Meta tracker | Aggregator |
| [#32888](https://github.com/openai/codex/issues/32888) | Auto-compaction uses stale token usage after tool output, causing unrecoverable context overflow | Open | No | **Medium–High** | Compaction timing | Code-level report |

## Issue categories

| Category | Representative issues | Why it matters to usage |
|---|---|---|
| **Too many reasoning-model requests** | #35259, #35108, #42981, #32188, #31935, #33542, #41450 | Timer expiry, serial tool boundaries, or missing runtime callbacks repeatedly return control to a large reasoning context. This harness's sleeper test primarily targets this family. |
| **Each request is too large** | #44386, #40897, #44305, #44884, #35458, #32888, #18526 | Tool/schema/context growth means even a legitimate model turn can replay tens or hundreds of thousands of tokens. |
| **Unexpected auxiliary/background model calls** | #43287, #39408, #37445, #42282, #42702 | Auto-review, Desktop background work, scheduled automation, or capture/summarization can generate authenticated model activity outside the obvious foreground turn. |
| **Multi-agent multiplication and recovery tax** | #39808, #46023, #43229, #45383, #27131 | Child bootstrap/fork cost, repeated large inherited context, cache invalidation, and post-limit reconstruction can magnify usage independently of waits. |
| **Quota/accounting/entitlement anomalies** | #29955, #30918, #33685, #26791, #30081, #41957, #43136, #38157, #39260, #14593 | Reported allowance movement may not be explainable solely from local model-token telemetry. These require server-side attribution/reconciliation as well as client efficiency work. |
| **Cross-report tracker** | #41220 | Correlates the distinct symptom families instead of assuming one root cause. |

## Experimental cautions

1. Do not compare runs that cross a 5-hour or weekly reset boundary.
2. Do not run baseline and mitigation simultaneously; they share the same subscriber quota.
3. Record exact versions. A client update between runs is a confounder, not merely metadata.
4. Keep model/tier fixed: Astra, low reasoning, default service tier. Do not enable Fast/Priority for one run and not another.
5. Do not infer dollars from token counts or API prices. This experiment measures subscription-window movement.
6. Do not treat a missing telemetry field as 100% remaining. Missing/unknown is unknown.
7. Do not launch a replacement sleeper after a terminal-tool yield. The original PID/session must remain the target.
8. For a fair A/B comparison, start runs at similar 5-hour/weekly headroom and repeat each condition more than once.

## Suggested experiment matrix

| Agent | Mode | Parent | Monitor | Expected ideal behavior |
|---|---|---|---|---|
| Codex | baseline | Astra/low | none | Measures current default timeout/re-entry behavior |
| OMP | baseline | Astra/low | none | Measures current default OMP wait behavior |
| Codex | mitigation | Astra/low | Luna/low if needed | Parent idle; long monitor wait; only completion should require parent reasoning |
| OMP | mitigation | Astra/low | `wait-monitor` → Luna/low | Parent idle; blocking monitor; no periodic parent polling |

The architectural target remains stricter than the mitigation: **while the sleeper's externally observable state is unchanged, elapsed wall-clock time alone should not cause a reasoning-model request.**
