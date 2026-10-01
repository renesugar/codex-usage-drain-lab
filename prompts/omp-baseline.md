Run the OMP baseline usage-drain experiment in this repository exactly as specified in `AGENTS.md`.

The parent model must be `openai-codex/gpt-6-astra:low`. This is a ChatGPT/Codex subscription test. Do not switch to the API-key based `openai` provider and do not use API pricing.

Validate `scripts/check_agent_usage.py --agent omp` against `omp usage --provider openai-codex` before starting. Take the before snapshot, launch exactly one 61m30s target, and use OMP's normal waiting behavior. Do not dispatch the `wait-monitor` agent in the baseline. If OMP itself yields and returns you to the model while the target is unchanged, continue waiting on the same process without unrelated work.

After completion, take the after snapshot and pass the correct OMP session JSONL to `scripts/finish_run.py`.
