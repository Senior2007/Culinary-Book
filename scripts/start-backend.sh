#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/Backend"
VENV="$BACKEND/.venv"

if [[ ! -d "$VENV" ]]; then
  echo "Virtual environment not found. Run: ./scripts/setup.sh"
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

export PYTHONPATH="$BACKEND/library/src"
export MONGODB_URL="${MONGODB_URL:-mongodb://localhost:27017}"
export MONGODB_DATABASE="${MONGODB_DATABASE:-culinary_book}"

cd "$BACKEND"
echo "API: http://localhost:8000  |  Docs: http://localhost:8000/docs"
exec uvicorn endpoints:app --reload --host 0.0.0.0 --port 8000
