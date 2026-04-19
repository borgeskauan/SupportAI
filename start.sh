#!/bin/bash

# SupportAI - Start Backend and Frontend
# This script starts both the FastAPI backend and Angular frontend in one command

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_BIN="$PROJECT_ROOT/venv/bin"

echo "🚀 Starting SupportAI (Backend + Frontend)..."
echo ""

# Setup Backend
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[0;34mSetting up Backend (Python)\033[0m"
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"

cd "$BACKEND_DIR"

# Check if venv exists and is valid
if [ ! -f "$VENV_BIN/python" ]; then
    echo -e "\033[1;33mCreating Python virtual environment...\033[0m"
    rm -rf "$PROJECT_ROOT/venv" 2>/dev/null || true
    python3 -m venv "$PROJECT_ROOT/venv"
fi

# Install dependencies using venv's pip directly
echo "Installing Python dependencies..."
"$VENV_BIN/pip" install --quiet -r requirements.txt 2>/dev/null || "$VENV_BIN/pip" install -r requirements.txt
echo ""

# Setup Frontend
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[0;34mSetting up Frontend (Node.js)\033[0m"
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"

cd "$FRONTEND_DIR"

# Check node and npm
if ! command -v node &> /dev/null; then
    echo -e "\033[0;31m✗ Node.js is not installed. Please install Node.js first.\033[0m"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing Node.js dependencies (this may take a minute)..."
    npm install --silent
else
    echo "Node.js dependencies already installed"
fi

echo -e "\033[0;32m✓ Frontend ready\033[0m"
echo ""

# Start servers
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[0;32m🎉 Starting both servers...\033[0m"
echo -e "\033[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo ""
echo -e "\033[1;33mBackend:\033[0m   http://localhost:8000 (API docs: /docs)"
echo -e "\033[1;33mFrontend:\033[0m  http://localhost:4200"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd "$PROJECT_ROOT"
"$VENV_BIN/python" -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "\033[0;32m✓ Backend started (PID: $BACKEND_PID)\033[0m"

# Give backend a moment to start
sleep 2

# Start frontend in foreground (so Ctrl+C stops the script)
cd "$FRONTEND_DIR"
echo -e "\033[0;32m✓ Frontend starting in Portuguese (this may take a moment)...\033[0m"
npm run ng -- serve --configuration=pt-BR

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null; exit" EXIT INT TERM
