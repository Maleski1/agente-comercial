"""
Script de setup: cria instancia na Evolution API e configura webhook.

Uso: python scripts/setup_evolution.py
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
API_KEY = os.getenv("EVOLUTION_API_KEY", "minha-chave-secreta-123")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "agente-comercial")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://host.docker.internal:8000/webhook/messages")

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json",
}


def verificar_api_online() -> bool:
    """Verifica se a Evolution API esta respondendo."""
    try:
        resp = httpx.get(f"{API_URL}", headers=HEADERS, timeout=5)
        print(f"[OK] Evolution API respondendo (status {resp.status_code})")
        return True
    except httpx.ConnectError:
        print("[ERRO] Evolution API nao esta rodando!")
        print("       Execute: docker compose up -d")
        return False


def criar_instancia() -> dict:
    """Cria uma nova instancia do WhatsApp na Evolution API."""
    payload = {
        "instanceName": INSTANCE_NAME,
        "integration": "WHATSAPP-BAILEYS",
        "qrcode": True,
    }

    resp = httpx.post(
        f"{API_URL}/instance/create",
        json=payload,
        headers=HEADERS,
        timeout=10,
    )

    if resp.status_code == 201:
        data = resp.json()
        print(f"[OK] Instancia '{INSTANCE_NAME}' criada com sucesso!")
        return data
    elif resp.status_code == 403:
        print(f"[ERRO] Chave de API invalida. Verifique EVOLUTION_API_KEY no .env")
        sys.exit(1)
    elif resp.status_code == 409:
        print(f"[INFO] Instancia '{INSTANCE_NAME}' ja existe. Continuando...")
        return {}
    else:
        print(f"[ERRO] Falha ao criar instancia: {resp.status_code} - {resp.text}")
        sys.exit(1)


def configurar_webhook() -> None:
    """Configura o webhook na Evolution API para encaminhar mensagens ao FastAPI."""
    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_URL,
            "webhookByEvents": False,
            "webhookBase64": False,
            "events": [
                "MESSAGES_UPSERT",
                "CONNECTION_UPDATE",
            ],
        }
    }

    resp = httpx.post(
        f"{API_URL}/webhook/set/{INSTANCE_NAME}",
        json=payload,
        headers=HEADERS,
        timeout=10,
    )

    if resp.status_code in (200, 201):
        print(f"[OK] Webhook configurado -> {WEBHOOK_URL}")
        print(f"     Eventos: MESSAGES_UPSERT, CONNECTION_UPDATE")
    else:
        print(f"[ERRO] Falha ao configurar webhook: {resp.status_code} - {resp.text}")
        print("       Voce pode configurar manualmente depois.")


def buscar_qrcode() -> str | None:
    """Busca o QR code para conectar o WhatsApp."""
    resp = httpx.get(
        f"{API_URL}/instance/connect/{INSTANCE_NAME}",
        headers=HEADERS,
        timeout=10,
    )

    if resp.status_code == 200:
        data = resp.json()
        # O QR code pode vir como base64 ou como texto
        qr_base64 = data.get("base64")
        qr_code = data.get("code")

        if qr_base64:
            print("\n[QR CODE] Abra o link abaixo no navegador para escanear:")
            print(f"  {API_URL}/instance/connect/{INSTANCE_NAME}")
        elif qr_code:
            print(f"\n[QR CODE] Codigo: {qr_code}")
        else:
            state = data.get("instance", {}).get("state", "")
            if state == "open":
                print("[OK] WhatsApp ja esta conectado!")
            else:
                print(f"[INFO] Estado da instancia: {state}")

        return qr_code
    else:
        print(f"[AVISO] Nao foi possivel obter QR code: {resp.status_code}")
        return None


def verificar_status() -> str:
    """Verifica o status da conexao do WhatsApp."""
    resp = httpx.get(
        f"{API_URL}/instance/connectionState/{INSTANCE_NAME}",
        headers=HEADERS,
        timeout=10,
    )

    if resp.status_code == 200:
        state = resp.json().get("instance", {}).get("state", "desconhecido")
        print(f"[STATUS] Conexao: {state}")
        return state

    return "erro"


def main():
    print("=" * 50)
    print("  SETUP - EVOLUTION API")
    print("=" * 50)
    print(f"\n  API URL:    {API_URL}")
    print(f"  Instancia:  {INSTANCE_NAME}")
    print(f"  Webhook:    {WEBHOOK_URL}")
    print()

    # 1. Verificar API
    if not verificar_api_online():
        sys.exit(1)

    # 2. Criar instancia
    criar_instancia()

    # 3. Configurar webhook
    configurar_webhook()

    # 4. Buscar QR code
    print("\n--- Conexao WhatsApp ---")
    buscar_qrcode()

    print("\n" + "=" * 50)
    print("  PROXIMO PASSO:")
    print("  1. Escaneie o QR code com seu WhatsApp")
    print(f"  2. Acesse {API_URL}/instance/connect/{INSTANCE_NAME}")
    print("  3. Inicie o FastAPI: uvicorn src.main:app --reload")
    print("  4. Envie uma mensagem de teste!")
    print("=" * 50)


if __name__ == "__main__":
    main()
