Run one additional Codex baseline with `gpt-6.1-sol` and `max` reasoning effort,
as explicitly authorized by the user. This is an additional experimental
condition; it overrides AGENTS.md's Astra/low model requirement for this trial
only. Keep the default service tier and ChatGPT subscription authentication.

Read README.md, AGENTS.md, and PLAN.md. Run the parser tests and the model-free
subscription probe. Verify the active rollout actually records Sol/Max and
record both host and CLI versions. Select the dedicated project profile:

```bash
python3 scripts/select_profile.py codex sol-max-baseline
python3 scripts/start_run.py --agent codex --mode baseline \
  --model gpt-6.1-sol --effort max
```

Verify the saved before snapshot, reset headroom, and absence of another target
before launching exactly one normal 3690-second wait_target.py process. Use
the same baseline terminal waiting mechanism as the Astra trials. Do not use
a worker or the deterministic mitigation loop. Immediately continue waiting
on the same terminal session after intermediate timeouts. No unrelated work
may run during the target interval.

After completion, capture the post-run snapshot promptly and finish the report
with the correct parent rollout. Compare subscriber percentage-point movement
and best-effort pre-completion rounds with the earlier runs. Do not infer API
prices, assume subscription weighting from API prices, or claim causation from
one trial. Note that both model and reasoning effort differ from Astra/low,
along with any headroom, context, or timing differences.
