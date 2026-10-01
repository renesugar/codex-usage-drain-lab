Run the Codex mitigation usage-drain experiment in this repository exactly as specified in `AGENTS.md`.

Use the Codex mitigation profile. The parent must remain Astra/low on the default service tier. Use ChatGPT subscriber auth only; never use API-key billing or API pricing.

The experiment uses the same 61m30s deterministic target as the baseline. Prefer a long blocking/event-driven wait. If a monitoring agent is needed, use exactly one configured Luna/low worker and leave the Astra parent idle. The monitor must not send periodic liveness messages; it should return only on target completion, failure, an actionable anomaly, or the target's 65m hard fail-safe.

Do not poll the monitoring worker from Astra. Do not restart the sleeper after a terminal yield. Finish the report with both parent and monitor session logs if they are separately persisted so that pre-completion model activity can be counted across the whole orchestration.
