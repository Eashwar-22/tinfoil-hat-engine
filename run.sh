#!/bin/bash



echo "=========================================="
echo "   TINFOIL HAT SEARCH ENGINE - LAUNCHER   "
echo "=========================================="

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null
then
    echo "[!] WARNING: Ollama does not seem to be running."
    echo "[*] Starting Ollama in the background..."
    ollama serve &
    sleep 5
fi

# Check for the model (Llama3.2)
if ! ollama list | grep -q "llama3.2"; then
    echo "[!] Model 'llama3.2' not found. Pulling it now..."
    echo "    (This might take a few minutes depending on your internet)"
    ollama pull llama3.2
fi

# Check for Vision Model (Llava)
if ! ollama list | grep -q "llava"; then
    echo "[!] Vision Model 'llava' not found. Downloading in BACKGROUND..."
    ollama pull llava &
fi

# 1. Start Backend
echo "[*] Booting Backend (FastAPI)..."
cd backend
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 2. Start Frontend
echo "[*] Loading Frontend (Vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo " "
echo "=========================================="
echo "   SYSTEM ONLINE"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   Press Ctrl+C to shutdown"
echo "=========================================="

# Wait for process exit
wait $BACKEND_PID $FRONTEND_PID
