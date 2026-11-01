#!/bin/bash
set -e

echo "================================================================"
echo "🚀 Arrancando Geko Suite: Signer + Backend + Telegram Bot"
echo "================================================================"

PORT="${PORT:-10000}"
export BACKEND_URL="http://127.0.0.1:${PORT}"
export SIGNER_URL="http://127.0.0.1:8088"
export REMOTE_SIGNER_URL="http://127.0.0.1:8088"
export SIGNER_MODE="remote"

# Cleanup handler for graceful shutdown
cleanup() {
    echo "Recibida señal de terminación (SIGTERM/SIGINT). Deteniendo servicios..."
    kill -TERM "$PID_BOT" 2>/dev/null || true
    kill -TERM "$PID_BACKEND" 2>/dev/null || true
    kill -TERM "$PID_SIGNER" 2>/dev/null || true
    wait
    echo "Todos los servicios han finalizado."
    exit 0
}
trap cleanup SIGTERM SIGINT

# 1. Start Signer Microservice on 127.0.0.1:8088
echo "[1/3] Iniciando ByteDance Remote Signer (:8088)..."
python signer_server.py &
PID_SIGNER=$!

# Wait for Signer healthcheck
for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:8088/health | grep -q "ok"; then
        echo "✔ Signer Microservice listo en http://127.0.0.1:8088"
        break
    fi
    sleep 0.5
done

# 2. Start FastAPI Backend on 0.0.0.0:$PORT
echo "[2/3] Iniciando TikTok Sticker Service FastAPI en :${PORT}..."
uvicorn app.main:app --host 0.0.0.0 --port "$PORT" &
PID_BACKEND=$!

# Wait for Backend healthcheck
for i in $(seq 1 30); do
    if curl -s "http://127.0.0.1:${PORT}/health" | grep -q "healthy"; then
        echo "✔ FastAPI Backend listo en http://0.0.0.0:${PORT}"
        break
    fi
    sleep 0.5
done

# 3. Start Telegram Bot Engine
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠ ADVERTENCIA: La variable TELEGRAM_BOT_TOKEN está vacía. El bot de Telegram no arrancará."
else
    echo "[3/3] Iniciando Geko Telegram Bot Polling Engine..."
    python bot.py &
    PID_BOT=$!
    echo "✔ Telegram Bot Polling Engine iniciado (PID $PID_BOT)."
fi

echo "================================================================"
echo "✔ Suite de producción operativa al 100% en Render"
echo "================================================================"

# Wait for all background processes; exit if any process terminates
wait -n
