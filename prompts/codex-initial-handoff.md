# Initial handoff: validate quota probes and run Codex/OMP usage-drain experiments

Work only in this repository. Read `README.md`, `AGENTS.md`, and `PLAN.md` first.

This harness measures ChatGPT subscriber quota drain while a deterministic process sleeps for 61 minutes 30 seconds. The goal is to distinguish productive completion handling from reasoning-model wakeups that occur while nothing has changed.

## Non-negotiable settings

- Codex parent: `gpt-6-astra`, reasoning effort `low`, default service tier.
- OMP parent: `openai-codex/gpt-6-astra:low`.
- Authentication: the user's ChatGPT/Codex subscription.
- Never replace OMP's `openai-codex` provider with the API-key based `openai` provider.
- Never use `OPENAI_API_KEY`, API billing, or API-price calculations for this experiment.
- Baseline and mitigation runs must not overlap because they share subscriber quota.

## 1. Validate the local measurement code before any 61m30s run

Run:

```bash
python3 scripts/test_check_agent_usage.py
python3 scripts/check_agent_usage.py --agent codex --json
python3 scripts/check_agent_usage.py --agent omp --json
omp usage --json --provider openai-codex
codex --version
omp --version
```

Verify that both Codex and OMP probes identify the same account's recognizable 5-hour and weekly windows. The exact presentation may differ, but the window durations/resets and percentages should reconcile.

Missing telemetry is `unknown`; never treat it as 100% remaining.

If either parser is incompatible with the installed client version, repair `scripts/check_agent_usage.py` and `scripts/test_check_agent_usage.py` first and rerun the tests. Do not begin a measured run until both quota probes are correct.

## 2. Run the Codex baseline and create its report

Install the baseline project profile:

```bash
python3 scripts/select_profile.py codex baseline
RUN_ID=$(python3 scripts/start_run.py --agent codex --mode baseline)
python3 scripts/wait_target.py --log "reports/raw/$RUN_ID/target.jsonl"
```

The target sleeps 3690 seconds and has a hard fail-safe at 3900 seconds. The fail-safe should never fire.

When the terminal command yields/backgrounds, retain ownership of that same process/session. **Never launch a replacement sleeper.** Use Codex's normal baseline wait behavior. Do not spawn a Luna monitor yet. Do no unrelated work during the sleep interval.

If the runtime returns control because a wait timeout expired while the target is still running, immediately continue waiting on the same target. That timeout-driven re-entry is part of the baseline measurement. Do not send periodic updates merely because time elapsed.

After the target emits `completed`:

```bash
python3 scripts/find_recent_session.py --agent codex
python3 scripts/finish_run.py --run-id "$RUN_ID" --session-log <correct-codex-rollout-jsonl>
```

Inspect and retain the generated Markdown report. Do not copy the private rollout itself into the repository.

## 3. OMP baseline

Only proceed if there is enough 5-hour and weekly headroom for another valid trial and no reset boundary will cross the run.

You may hand the same conversation context to OMP using the Codex session ID:

```bash
omp --from-codex <codex-session-id> --approval-mode always-ask --cwd "$PWD"
```

The import is optional. The measurement is not shared: OMP must take a fresh before snapshot immediately before its own sleeper.

Inside OMP, follow `prompts/omp-baseline.md` and `AGENTS.md`:

```bash
python3 scripts/select_profile.py omp baseline
RUN_ID=$(python3 scripts/start_run.py --agent omp --mode baseline)
python3 scripts/wait_target.py --log "reports/raw/$RUN_ID/target.jsonl"
```

Do not use `wait-monitor` in the OMP baseline. After completion, pass the correct OMP session JSONL to `scripts/finish_run.py`.

If you cannot safely launch OMP from the current Codex process, finish the Codex report and leave an exact OMP resume command in your final handoff instead of faking the second run.

## 4. Mitigation trials

After valid baselines, and only with enough quota headroom, run the matching mitigation prompts:

- `prompts/codex-mitigation.md`
- `prompts/omp-mitigation.md`

Codex mitigation keeps Astra/low as parent, permits a 65-minute empty-terminal wait, and can use one Luna/low monitoring worker.

OMP mitigation keeps `openai-codex/gpt-6-astra:low` as parent and routes the project `wait-monitor` agent to `openai-codex/gpt-5.6-luna:low`.

The Astra parent should remain idle while a monitor owns the wait. Do not poll the monitor from the parent. Include parent and worker session logs in the final report when they are separate.

## 5. Report validity

For every run verify:

- coding-agent version recorded;
- parent actually used Astra/low;
- target has both `started` and `completed` markers and no `failsafe_timeout`;
- no subscription reset occurred between before/after samples;
- no duplicate sleeper was launched;
- no unrelated model work occurred during the sleep;
- 5-hour and weekly before/after fields came from subscription telemetry;
- any pre-completion model-round count is identified as best effort.

If a run is invalid, say why. Do not manufacture or interpolate quota results.
