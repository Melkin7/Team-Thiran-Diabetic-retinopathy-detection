#!/bin/bash

# ── Team Thiran — Diabetic Retinopathy Detection ──────────────────────────────
echo "╔══════════════════════════════════════════════════╗"
echo "║   Team Thiran — Diabetic Retinopathy Detection  ║"
echo "║   ResNet152 AI Model | FastAPI + Frontend        ║"
echo "╚══════════════════════════════════════════════════╝"

# ── Navigate to project root ──────────────────────────────────────────────────
cd "$(dirname "$0")"

# ── Activate virtual environment ──────────────────────────────────────────────
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found! Run: python -m venv venv"
    exit 1
fi

# ── Check classifier.pt exists ────────────────────────────────────────────────
if [ ! -f "classifier.pt" ]; then
    echo "❌ classifier.pt not found in project root!"
    exit 1
fi

echo "✅ Model file found: classifier.pt"

# ── Check frontend exists ─────────────────────────────────────────────────────
if [ ! -f "frontend/web/index.html" ]; then
    echo "❌ Frontend not found at frontend/web/index.html"
    exit 1
fi

echo "✅ Frontend found"

# ── Kill any process already using port 8000 ─────────────────────────────────
echo "🔍 Checking port 8000..."
PID=$(lsof -ti:8000)
if [ -n "$PID" ]; then
    echo "⚠️  Port 8000 in use by PID $PID — killing it..."
    kill -9 $PID
    sleep 1
    echo "✅ Port 8000 is now free"
fi

echo ""
echo "🚀 Starting server at http://localhost:8000"
echo "📖 API Docs at  http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

# ── Start FastAPI server ──────────────────────────────────────────────────────
python server.py