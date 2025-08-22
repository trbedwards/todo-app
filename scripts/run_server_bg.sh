#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$REPO_ROOT/.uvicorn.log"
PID_FILE="$REPO_ROOT/.uvicorn.pid"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
	echo "Uvicorn already running (PID $(cat "$PID_FILE"))."
	echo "Logs: $LOG_FILE"
	exit 0
fi

# Conda activation if available
if [[ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]]; then
	source "$HOME/miniforge3/etc/profile.d/conda.sh"
fi

conda activate todo-app 2>/dev/null || true
cd "$REPO_ROOT"

nohup python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Uvicorn started (PID $PID). Logs: $LOG_FILE"