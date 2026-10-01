# Plan

## Goal

Produce comparable, versioned measurements of ChatGPT subscriber quota drain caused by coding-agent waiting behavior, then compare baseline behavior with long-wait / low-cost-monitor mitigations.

## Phase 1 — Harness construction — complete

- [x] Port the Notrios model-free Codex quota probe.
- [x] Add OMP `openai-codex` usage probing.
- [x] Preserve a local-cache Claude probe.
- [x] Add informational OpenCode2 support without falsely treating its local stats as ChatGPT quota.
- [x] Add parser tests.
- [x] Add deterministic 61m30s target with a 65m hard fail-safe.
- [x] Add baseline and mitigation project profiles for Codex and OMP.
- [x] Add report generation and best-effort pre-completion model-round counting.
- [x] Add issue inventory and categories to README.

## Phase 2 — Environment verification — pending on test machine

- [ ] Run `python3 scripts/test_check_agent_usage.py`.
- [ ] Confirm `check_agent_usage.py --agent codex` reports real 5-hour/weekly windows without a model call.
- [ ] Confirm `check_agent_usage.py --agent omp` reports the same subscription via `openai-codex`.
- [ ] Confirm project Codex configuration loads without errors.
- [ ] Confirm project OMP configuration loads and selects `openai-codex/gpt-6-astra:low`.
- [ ] Confirm `wait-monitor` resolves to Luna/low in OMP.
- [ ] Record installed versions.

## Phase 3 — Baselines — pending

Run at least two valid trials for each condition when practical:

1. Codex baseline, Astra/low.
2. OMP baseline, Astra/low.

Do not overlap trials because both spend the same subscription quota.

## Phase 4 — Mitigations — pending

1. Codex mitigation: Astra/low parent, 65-minute empty-terminal wait allowance, one Luna/low monitoring worker if necessary.
2. OMP mitigation: Astra/low parent, blocking `wait-monitor` routed to Luna/low.

The purpose of these runs is empirical: measure whether moving waiting away from repeated parent reasoning reduces the actual subscriber-window delta.

## Phase 5 — Compare — pending

Create a summary table across valid runs:

- agent and version;
- mode;
- initial 5-hour / weekly headroom;
- percentage-point drain;
- target duration;
- observed pre-completion model rounds;
- parent vs monitor round split when available.

Do not claim causation from a single run. Prefer repeated A/B trials on the same client version and similar quota headroom.

## Non-goals

- API dollar-cost benchmarking.
- Benchmarking model answer quality.
- Stressing the account until quota exhaustion.
- Testing arbitrary long-running workloads before the deterministic sleeper is understood.
- Treating a cheap remote monitor as the final architecture. The desired product behavior remains event-driven deterministic notification with zero reasoning inference while state is unchanged.
