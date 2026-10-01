# Sources consulted

## Notrios (`develop` branch)

- https://github.com/renesugar/notrios/blob/develop/AGENTS.md
- https://github.com/renesugar/notrios/blob/develop/agent/ATTEMPT_LOG.jsonl
- https://github.com/renesugar/notrios/blob/develop/agent/LOOP_DETECTION.md
- https://github.com/renesugar/notrios/blob/develop/agent/MODEL_LOG.jsonl
- https://github.com/renesugar/notrios/blob/develop/scripts/agent_usage_preflight.sh
- https://github.com/renesugar/notrios/blob/develop/scripts/check_agent_usage.py

## Codex

- https://github.com/openai/codex/
- Current source/config schema for `background_terminal_max_timeout`, `[agents]`, `default_subagent_model`, `default_subagent_reasoning_effort`, and `model_reasoning_effort`.
- GitHub issues linked from the inventory in `README.md`.

## OMP / Oh My Pi

- https://github.com/can1357/oh-my-pi/
- `docs/cli-reference.md` for `--from-codex`, `--cwd`, and approval-mode behavior.
- `docs/settings.md` for project `.omp/config.yml`.
- `docs/task-agent-discovery.md` for project agents, role aliases, and `task.agentModelOverrides` precedence.
- `docs/providers.md` / `docs/provider-quirks.md` for the `openai-codex` OAuth provider.
- `packages/ai/src/usage/openai-codex.ts` for 5-hour/7-day usage-window parsing and `/wham/usage` behavior.
