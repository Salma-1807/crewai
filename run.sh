#!/bin/bash
# Unix/Linux/Mac startup script for Banking Assistant
# This script sets up the environment and starts the Streamlit app

set -e  # Exit on error

echo ""
echo "========================================"
echo "  Banking Assistant Startup"
echo "  CrewAI + Streamlit"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

echo "✓ Python $(python3 --version) found"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "[3/4] Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "[4/4] Initializing database..."
python database_setup.py || echo "⚠ Database initialization had issues (will retry on first run)"

echo ""
echo "========================================"
echo "  Starting Streamlit Application"
echo "========================================"
echo ""
echo "The app will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
