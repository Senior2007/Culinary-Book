#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/Backend"
VENV="$BACKEND/.venv"

echo "==> Creating Python virtual environment..."
python3 -m venv "$VENV"

# shellcheck source=/dev/null
source "$VENV/bin/activate"

echo "==> Installing backend dependencies..."
pip install --upgrade pip
pip install -r "$BACKEND/requirements.txt"

echo ""
echo "Setup complete."
echo "Next steps:"
echo "  1. Start MongoDB:  docker compose up -d"
echo "  2. Backend:        ./scripts/start-backend.sh"
echo "  3. Frontend:       ./scripts/start-frontend.sh   (in another terminal)"
echo "  4. Open browser:   http://localhost:5500"
