#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
minimum=${AGENT_USAGE_MINIMUM:-20}
agent=${1:-self}
python3 "$ROOT/scripts/test_check_agent_usage.py"
python3 "$ROOT/scripts/check_agent_usage.py" --agent "$agent" --minimum-remaining "$minimum" --json
