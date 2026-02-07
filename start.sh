#!/bin/bash
# Inicia FastAPI (background) + Streamlit (foreground)

echo "Iniciando Agente Comercial..."

# FastAPI em background
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Streamlit em foreground (mantém o container vivo)
streamlit run src/dashboard/app.py \
  --server.port 8501 \
  --server.headless true \
  --server.address 0.0.0.0
