# Third-party/source notices

The usage-probe design and portions of the normalization/process-detection approach are adapted from the Apache-2.0-licensed Notrios project, `renesugar/notrios`, `develop` branch, especially:

- `AGENTS.md`
- `scripts/check_agent_usage.py`
- `scripts/agent_usage_preflight.sh`
- `agent/ATTEMPT_LOG.jsonl`
- `agent/LOOP_DETECTION.md`
- `agent/MODEL_LOG.jsonl`

Source: https://github.com/renesugar/notrios/tree/develop

OMP behavior/configuration was checked against `can1357/oh-my-pi`, including its CLI, settings, task-agent-discovery, provider, and OpenAI Codex usage documentation/source.

Source: https://github.com/can1357/oh-my-pi

No third-party source file is vendored wholesale in this harness.
