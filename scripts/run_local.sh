#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── Locate and activate virtual environment ───────────────────────────────────
VENV_NAME="${VENV:-}"
CANDIDATES=("env311" "venv" ".venv" "env")
[ -n "$VENV_NAME" ] && CANDIDATES=("$VENV_NAME" "${CANDIDATES[@]}")

ACTIVATED=0
for name in "${CANDIDATES[@]}"; do
    activate="$ROOT/$name/bin/activate"
    if [ -f "$activate" ]; then
        echo "Activating virtual environment: $name"
        # shellcheck disable=SC1090
        source "$activate"
        ACTIVATED=1
        break
    fi
done

if [ $ACTIVATED -eq 0 ]; then
    echo "Warning: no virtual environment found. Searched: ${CANDIDATES[*]}"
    echo "  Create one: python3 -m venv env311"
    echo "  Install:    env311/bin/pip install -r requirements.txt"
fi

# ── Load .env ─────────────────────────────────────────────────────────────────
if [ -f "$ROOT/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$ROOT/.env"
    set +a
fi

# ── Resolve host / port ───────────────────────────────────────────────────────
HOST="${APP_HOST:-0.0.0.0}"
PORT="${APP_PORT:-8000}"
RELOAD="${RELOAD:-1}"

RELOAD_FLAG=""
[ "$RELOAD" = "1" ] && RELOAD_FLAG="--reload"

echo ""
echo "Starting Lapo - AI Code Review Assistant"
echo "  URL  : http://localhost:$PORT"
echo "  Docs : http://localhost:$PORT/docs"
echo "  Env  : ${APP_ENV:-development}"
echo ""

# shellcheck disable=SC2086
uvicorn app.main:app --host "$HOST" --port "$PORT" $RELOAD_FLAG
