#!/bin/bash

# Team Thiran - Web Interface Launcher
# This script starts the Flask web application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   TEAM THIRAN - Diabetic Retinopathy Detection Web App      ║"
echo "║                 Professional Medical Interface              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✅ Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Creating from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "   ⚠️  Please update .env with your credentials"
fi

# Check database connection
echo ""
echo "🔍 Checking database connection..."
python3 << 'EOF'
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'dr_user'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'BLINDNESS'),
    )
    print("✅ Database connection successful!")
    conn.close()
except mysql.connector.Error as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "Please ensure MySQL is running and credentials are correct in .env"
    exit 1
fi

# Check model file
echo "🔍 Checking ML model..."
if [ ! -f "$PROJECT_DIR/classifier.pt" ]; then
    echo "❌ Model file (classifier.pt) not found!"
    echo "   Please ensure the 677MB trained model is in the project root."
    exit 1
fi
echo "✅ Model file found ($(du -h "$PROJECT_DIR/classifier.pt" | cut -f1))"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  STARTING WEB APPLICATION                    ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  🌐 Open your browser and go to: http://localhost:5000     ║"
echo "║                                                              ║"
echo "║  📝 Demo Login:                                              ║"
echo "║     Username: admin                                          ║"
echo "║     Password: admin123                                       ║"
echo "║                                                              ║"
echo "║  Press Ctrl+C to stop the server                             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Start Flask application
cd "$PROJECT_DIR/frontend"
python3 app.py
