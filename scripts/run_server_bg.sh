#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "REPO_ROOT: $REPO_ROOT"
LOG_FILE="$REPO_ROOT/.uvicorn.log"
PID_FILE="$REPO_ROOT/.uvicorn.pid"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
	echo "Uvicorn already running (PID $(cat "$PID_FILE"))."
	echo "Logs: $LOG_FILE"
	exit 0
fi

# Check if conda environment is already activated
if [[ "$CONDA_DEFAULT_ENV" == "todo-app" ]]; then
	echo "Conda environment 'todo-app' is already activated."
else
	echo "Sourcing conda environment..."
	# Try multiple conda installation paths
	CONDA_SCRIPT=""
	for conda_path in "$HOME/miniforge3/etc/profile.d/conda.sh" \
	                  "$HOME/anaconda3/etc/profile.d/conda.sh" \
	                  "$HOME/conda/etc/profile.d/conda.sh" \
	                  "/opt/conda/etc/profile.d/conda.sh"; do
		if [[ -f "$conda_path" ]]; then
			CONDA_SCRIPT="$conda_path"
			break
		fi
	done

	if [[ -n "$CONDA_SCRIPT" ]]; then
		source "$CONDA_SCRIPT"
		echo "Activating conda environment..."
		if conda activate todo-app 2>/dev/null; then
			echo "Successfully activated conda environment 'todo-app'"
		else
			echo "Warning: Failed to activate conda environment 'todo-app', continuing anyway..."
		fi
	else
		echo "Warning: Conda not found, continuing without conda activation..."
	fi
fi

cd "$REPO_ROOT"

echo "Starting Uvicorn..."
nohup python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Uvicorn started (PID $PID). Logs: $LOG_FILE"