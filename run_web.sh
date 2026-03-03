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
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi

# Load .env variables into shell
export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

# Check database connection
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
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Check model file
echo "🔍 Checking ML model..."
if [ ! -f "$PROJECT_DIR/classifier.pt" ]; then
    echo "❌ Model file (classifier.pt) not found!"
    exit 1
fi
echo "✅ Model file found ($(du -h "$PROJECT_DIR/classifier.pt" | cut -f1))"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  STARTING WEB APPLICATION                    ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  🌐 Open your browser: http://localhost:5000                ║"
echo "║  📝 Username: admin  Password: admin123                     ║"
echo "║  Press Ctrl+C to stop the server                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Start Flask application
cd "$PROJECT_DIR/frontend"
python3 app.py