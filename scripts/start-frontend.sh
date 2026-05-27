#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/Frontend"
PORT="${FRONTEND_PORT:-5500}"

cd "$FRONTEND"
echo "Frontend: http://localhost:${PORT}"
exec python3 -m http.server "$PORT"
