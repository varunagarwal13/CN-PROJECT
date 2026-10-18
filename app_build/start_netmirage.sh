#!/usr/bin/env bash
set -e

# =================================================================
# NetMirage - Single Command Platform Launcher
# Zero-Egress Sandboxed Defensive Cyber-Range
# =================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "================================================================="
echo "   NETMIRAGE DEFENSIVE CYBER-RANGE PLATFORM LAUNCHER"
echo "   Workspace Root: ${WORKSPACE_ROOT}"
echo "================================================================="

# 1. Virtual Environment & Dependencies
VENV_DIR="${WORKSPACE_ROOT}/app_build/backend/.venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo "[1/4] Initializing Python virtual environment..."
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install --upgrade pip
    "${VENV_DIR}/bin/pip" install -r "${WORKSPACE_ROOT}/app_build/backend/requirements.txt"
else
    echo "[1/4] Python virtual environment verified: ${VENV_DIR}"
fi

# 2. Database Initialization
echo "[2/4] Initializing SQLite database schema..."
"${VENV_DIR}/bin/python" -c "from app_build.backend.db import init_db; init_db(); print('SQLite schema initialized.')"

# 3. Docker Lab Verification / Fallback
echo "[3/4] Checking zero-egress Docker lab infrastructure..."
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo "      Docker daemon active. Validating ${WORKSPACE_ROOT}/app_build/docker/docker-compose.lab.yml..."
    docker compose -f "${WORKSPACE_ROOT}/app_build/docker/docker-compose.lab.yml" config >/dev/null
    echo "      Starting zero-egress lab containers in background..."
    docker compose -f "${WORKSPACE_ROOT}/app_build/docker/docker-compose.lab.yml" up -d
else
    echo "      Docker daemon not running or unavailable."
    echo "      [ACTIVE] Deterministic zero-egress lab emulator enabled (10.0.10.0/24 - 10.0.50.0/24)."
fi

# 4. Start Services
echo "[4/4] Starting NetMirage Backend and Frontend services..."

# Start Backend Daemon
"${VENV_DIR}/bin/python" -m uvicorn app_build.backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "      FastAPI Control API running (PID: ${BACKEND_PID})"

# Start Frontend Dev Server
cd "${WORKSPACE_ROOT}/app_build/frontend"
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
echo "      Vite React Console running (PID: ${FRONTEND_PID})"

echo "================================================================="
echo "   NETMIRAGE OPERATIONAL READOUT"
echo "   - Web Console:       http://localhost:5173"
echo "   - Control API:       http://localhost:8000"
echo "   - OpenAPI Docs:      http://localhost:8000/docs"
echo "   - Health Check:      http://localhost:8000/api/health"
echo "   - Egress Guard:      ZERO-EGRESS ENFORCED"
echo "================================================================="
echo "   Press Ctrl+C to terminate all services."

cleanup() {
    echo ""
    echo "[NETMIRAGE] Shutting down services..."
    kill ${BACKEND_PID} 2>/dev/null || true
    kill ${FRONTEND_PID} 2>/dev/null || true
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        docker compose -f "${WORKSPACE_ROOT}/app_build/docker/docker-compose.lab.yml" down 2>/dev/null || true
    fi
    echo "[NETMIRAGE] Clean shutdown complete."
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
