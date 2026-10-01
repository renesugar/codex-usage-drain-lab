Run the OMP mitigation usage-drain experiment in this repository exactly as specified in `AGENTS.md`.

The parent must remain `openai-codex/gpt-6-astra:low`. Dispatch the project `wait-monitor` agent, which is routed by `.omp/config.yml` to `openai-codex/gpt-5.6-luna:low`. Use ChatGPT/Codex subscription authentication only; do not use API-key billing or API pricing.

Take the before snapshot, launch exactly one 61m30s target, and give the monitoring worker ownership of the wait. The Astra parent should remain idle rather than polling the worker. The monitor should use the longest blocking/event-driven wait available and return only on completion, failure, actionable anomaly, or the target's 65m hard fail-safe.

Finish the report with both parent and worker session logs when available. Do not launch a replacement sleeper and do not perform unrelated work during the measured interval.
