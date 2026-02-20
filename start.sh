#!/bin/bash
echo "Starting CI/CD Healing Agent..."

cd "$(dirname "$0")/backend"
python3 -m venv venv 2>/dev/null
source venv/bin/activate
pip install -r requirements.txt -q
python main.py &
BACKEND_PID=$!

sleep 3

cd "../frontend"
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo "Press Ctrl+C to stop"
wait
