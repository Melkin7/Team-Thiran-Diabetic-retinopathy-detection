#!/bin/bash

# Team Thiran - Web Interface Launcher
# FastAPI + Uvicorn

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   TEAM THIRAN - Diabetic Retinopathy Detection Web App      ║"
echo "║                 Professional Medical Interface               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Activate virtual environment ──────────────────────────────────
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✅ Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# ── Check .env file ───────────────────────────────────────────────
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi

# ── Load .env variables ───────────────────────────────────────────
export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

# ── Check & Download model file ───────────────────────────────────
echo "🔍 Checking ML model..."
if [ ! -f "$PROJECT_DIR/models/classifier.pt" ]; then
    echo "⚠️  Model not found! Downloading from Google Drive (~677MB)..."
    pip install gdown -q
    gdown "https://drive.google.com/uc?id=17tor-RkVSy2zcDkWsgfUdOtEhmQbZE_S" \
          -O "$PROJECT_DIR/models/classifier.pt"
    if [ ! -f "$PROJECT_DIR/models/classifier.pt" ]; then
        echo "❌ Model download failed!"
        exit 1
    fi
    echo "✅ Model downloaded successfully!"
fi
echo "✅ Model file found ($(du -h "$PROJECT_DIR/models/classifier.pt" | cut -f1))"

# ── Check database connection (warn only, don't block) ────────────
echo ""
echo "🔍 Checking database connection..."
python3 -c "
import os
import mysql.connector
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'dr_user'),
        password=os.getenv('DB_PASSWORD', 'dr_password_2024'),
        database=os.getenv('DB_NAME', 'BLINDNESS'),
    )
    print('✅ Database connection successful!')
    conn.close()
except mysql.connector.Error as e:
    print(f'⚠️  Database not available: {e}')
    print('⚠️  App will start without database')
"

# ── Check Twilio credentials ──────────────────────────────────────
echo ""
echo "🔍 Checking Twilio configuration..."
python3 -c "
import os
sid   = os.getenv('TWILIO_ACCOUNT_SID', '')
token = os.getenv('TWILIO_AUTH_TOKEN', '')
phone = os.getenv('TWILIO_PHONE', '')
wa    = os.getenv('TWILIO_WHATSAPP', '')
recip = os.getenv('RECIPIENT_PHONE', '')

if sid and token and sid != 'your_account_sid_here':
    print('✅ Twilio credentials found')
    print(f'   SID:            {sid[:10]}...')
    print(f'   Phone:          {phone}')
    print(f'   WhatsApp:       {wa}')
    print(f'   Recipient:      {recip}')
else:
    print('⚠️  Twilio not configured — notifications disabled')
"

# ── Start FastAPI server ──────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  STARTING WEB APPLICATION                    ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  🌐 Open your browser: http://localhost:8000                ║"
echo "║  📖 API Docs at:       http://localhost:8000/docs           ║"
echo "║  Press Ctrl+C to stop the server                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd "$PROJECT_DIR"
python main.py
