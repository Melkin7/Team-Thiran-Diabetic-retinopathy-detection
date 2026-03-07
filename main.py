#!/usr/bin/env python3
"""
Team Thiran - Diabetic Retinopathy Detection System
Entry point for the FastAPI web application

To run:
    python main.py
    OR
    ./run_web.sh
"""

import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   TEAM THIRAN - Diabetic Retinopathy Detection Web App      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"🌐 Open your browser: http://{host}:{port}")
    print(f"📖 API Docs at:       http://{host}:{port}/docs")
    print("")
    
    uvicorn.run("server:app", host=host, port=port, reload=True)
