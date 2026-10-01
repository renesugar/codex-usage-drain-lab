# AGENTS.md

This repository is an experiment harness, not a normal implementation project. The primary rule is **do not contaminate the measurement**.

## Prime directive

Measure ChatGPT subscriber usage while a deterministic 61m30s process runs. Do not substitute API-key billing, API-price estimates, a different model, or an unrelated workload.

The parent model for both Codex and OMP tests is Astra at low reasoning effort:

- Codex: `gpt-6-astra`, `model_reasoning_effort = "low"`
- OMP: `openai-codex/gpt-6-astra:low`

The OMP provider must be `openai-codex`, not the API-key based `openai` provider.

## Before a measured run

1. Read `README.md` and `PLAN.md`.
2. Run:

   ```bash
   python3 scripts/test_check_agent_usage.py
   python3 scripts/check_agent_usage.py --agent self --json
   ```

3. If running OMP, also run:

   ```bash
   omp usage --json --provider openai-codex
   ```

   Confirm it returns ChatGPT/Codex subscription windows. If not, stop and repair the probe/authentication. Do not fall back to API-key billing.

4. Record the installed agent version. `scripts/start_run.py` does this automatically.
5. Confirm the active project profile is the intended one:

   ```bash
   python3 scripts/select_profile.py codex baseline
   # or: python3 scripts/select_profile.py codex mitigation
   # or: python3 scripts/select_profile.py omp baseline
   # or: python3 scripts/select_profile.py omp mitigation
   ```

6. Do not begin a measured run close to an expected 5-hour or weekly reset. A reset makes the before/after delta uninterpretable.

## Codex baseline procedure

From the repository root:

```bash
python3 scripts/select_profile.py codex baseline
RUN_ID=$(python3 scripts/start_run.py --agent codex --mode baseline)
python3 scripts/wait_target.py --log "reports/raw/$RUN_ID/target.jsonl"
```

The last command is deliberately long-running. Let the terminal tool yield/background it if that is the normal Codex behavior, but **never start a replacement sleeper**.

While it runs:

- Use the normal Codex waiting mechanism. This is the baseline; do not invoke the mitigation monitor.
- Do not run unrelated searches, tests, web calls, status checks, or commentary-generating work.
- If Codex wakes because a timeout expired while the target is still running, continue waiting on the same session. That wake is part of the measured failure mode.
- Do not send periodic updates merely because a minute elapsed.
- The target itself exits after 3690 seconds and has a fail-safe at 3900 seconds. The fail-safe should never fire in a correct run.

After completion, locate the current rollout file:

```bash
python3 scripts/find_recent_session.py --agent codex
```

Then finish:

```bash
python3 scripts/finish_run.py \
  --run-id "$RUN_ID" \
  --session-log ~/.codex/sessions/.../rollout-....jsonl
```

Commit the generated `reports/<run-id>.md` if the run is valid. Do not commit the raw private rollout.

## OMP baseline procedure

From the repository root:

```bash
python3 scripts/select_profile.py omp baseline
RUN_ID=$(python3 scripts/start_run.py --agent omp --mode baseline)
python3 scripts/wait_target.py --log "reports/raw/$RUN_ID/target.jsonl"
```

Use OMP's normal wait behavior. Do not dispatch `wait-monitor` in the baseline.

After completion:

```bash
python3 scripts/find_recent_session.py --agent omp
python3 scripts/finish_run.py \
  --run-id "$RUN_ID" \
  --session-log ~/.omp/agent/sessions/...jsonl
```

If the OMP session was imported from Codex with `--from-codex`, that is allowed, but the `before` snapshot must be taken immediately before the OMP target launch. Do not reuse the Codex before snapshot.

## Codex mitigation procedure

Install the mitigation profile:

```bash
python3 scripts/select_profile.py codex mitigation
RUN_ID=$(python3 scripts/start_run.py --agent codex --mode mitigation)
```

The parent remains Astra/low. Prefer the longest supported blocking/event-driven wait. If a worker is used, the configured default worker is Luna/low and there must be only one monitoring worker.

The monitor's contract is:

- watch exactly one target/session;
- no periodic status messages;
- no duplicate/restarted command;
- return on completion, failure, actionable anomaly, or hard fail-safe only;
- if the runtime forces an intermediate timeout, immediately re-arm the wait without unrelated reasoning.

Then launch the same target:

```bash
python3 scripts/wait_target.py --log "reports/raw/$RUN_ID/target.jsonl"
```

When finishing, pass both parent and monitor session logs if they are separately persisted:

```bash
python3 scripts/finish_run.py --run-id "$RUN_ID" \
  --session-log <parent-rollout.jsonl> \
  --session-log <monitor-rollout.jsonl>
```

## OMP mitigation procedure

Install the mitigation profile:

```bash
python3 scripts/select_profile.py omp mitigation
RUN_ID=$(python3 scripts/start_run.py --agent omp --mode mitigation)
```

Dispatch the project agent named `wait-monitor`. Its model is routed by project configuration to `openai-codex/gpt-5.6-luna:low`. The parent remains `openai-codex/gpt-6-astra:low`.

Give `wait-monitor` responsibility for the same deterministic target and remain idle until the worker returns. Do not poll the worker from Astra. Include parent and worker session JSONL files in `finish_run.py` when available.

## Resume and interruption rule

After a usage-limit interruption, application restart, or session resume, previous liveness state is stale. Before waiting on an old process or subagent:

1. verify the target/worker still exists;
2. do not assume “running” from old conversation history;
3. never launch a duplicate sleeper to replace a target that is actually still alive;
4. if the old target is gone without a `completed` marker, mark the run invalid rather than manufacturing a result.

## What counts as an unnecessary wake

`wait_target.py` writes its own `started` and `completed` UTC timestamps. `count_model_rounds.py` only counts model activity strictly between those timestamps.

Any reasoning-model round in that interval is unnecessary for discovering target completion because the target has not yet completed. The normal model turn triggered by real completion falls after the target's `completed` marker and is excluded.

The round counter is best effort. The authoritative measurement is subscriber quota before/after.

## Report validity checklist

A run is valid only when:

- target recorded `started` and `completed`;
- target did not record `failsafe_timeout`;
- model was Astra/low for the parent;
- OMP used `openai-codex` subscription auth;
- no API-price conversion was used;
- no 5-hour/weekly reset occurred between before and after snapshots;
- no duplicate sleeper was launched;
- no unrelated model work occurred during the target interval;
- coding-agent version is recorded.

If any condition fails, keep the raw evidence if useful but mark the run invalid and do not compare its quota delta with valid runs.
