#!/bin/bash

# This script automates the process of starting the development environment
# for the fxbot application. It activates the Python virtual environment,
# starts the Python backend server, and then starts the Node.js frontend server.

# --- Configuration ---
PYTHON_VENV_PATH="engine/.venv" # Relative path to the Python virtual environment directory
PYTHON_LOG_FILE="python_server.log"
FRONTEND_DIR="visualizer"

# --- Cleanup Function ---
# This function is called when the script exits to ensure the background Python process is terminated.
cleanup() {
    echo "" # Newline for cleaner exit message
    echo "Shutting down servers..."
    if [ -n "$PYTHON_PID" ] && ps -p $PYTHON_PID > /dev/null 2>&1; then
        echo "Stopping Python backend server (PID: $PYTHON_PID)..."
        kill $PYTHON_PID
    fi
    echo "Shutdown complete."
    exit 0
}

# Trap the INT signal (sent on Ctrl+C) to run the cleanup function.
trap cleanup SIGINT SIGTERM

# --- Main Execution ---

echo "--- Starting Python Backend Server ---"

# 1. Check for and activate the Python virtual environment.
if [ ! -f "$PYTHON_VENV_PATH/bin/activate" ]; then
    echo "Error: Python virtual environment activation script not found at '$PYTHON_VENV_PATH/bin/activate'."
    echo "Please create the virtual environment first using: python3 -m venv $PYTHON_VENV_PATH"
    exit 1
fi
source "$PYTHON_VENV_PATH/bin/activate"
echo "Python virtual environment activated."

# 2. Start the Python server in the background.
echo "Starting Python server (Uvicorn), logging to '$PYTHON_LOG_FILE'..."
"$PYTHON_VENV_PATH/bin/uvicorn" engine.main:app --reload --host 0.0.0.0 --port 8000 > "$PYTHON_LOG_FILE" 2>&1 &
PYTHON_PID=$!

sleep 2 # Give the server a moment to start.

echo "Python backend server started with PID: $PYTHON_PID"
echo ""
echo "--- Starting Node.js Frontend Server ---"

# 3. Start the Node.js development server in the foreground.
cd "$FRONTEND_DIR" || exit

# Check if node_modules exists, if not install
if [ ! -d "node_modules" ]; then
    echo "node_modules not found. Installing dependencies..."
    npm install
fi

echo "Starting Vite..."
npm run dev -- --host

# The script will block here until `npm run dev` is terminated.
