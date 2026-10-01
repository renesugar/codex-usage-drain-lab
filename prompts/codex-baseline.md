Run the Codex baseline usage-drain experiment in this repository exactly as specified in `AGENTS.md`.

Use Astra with low reasoning effort and the default service tier. Use ChatGPT subscriber auth only; do not use API-key billing or API pricing.

Validate `scripts/check_agent_usage.py` first, take the before snapshot with `scripts/start_run.py`, launch exactly one 61m30s `wait_target.py`, and wait on that same terminal session until it completes. Do not spawn a monitoring subagent in the baseline. Do not do unrelated work during the wait. If a runtime timeout wakes you while the target is still running, continue waiting on the same session; do not duplicate the command.

After completion, take the after snapshot, provide the relevant Codex rollout JSONL to `scripts/finish_run.py`, and inspect the generated Markdown report for correctness.
