"""Envio de mensagens via Evolution API."""

import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


async def enviar_mensagem(telefone: str, texto: str) -> dict:
    """
    Envia uma mensagem de texto via Evolution API.

    Args:
        telefone: Numero com codigo do pais (ex: 5511999999999)
        texto: Texto da mensagem
    """
    url = (
        f"{settings.evolution_api_url}/message/sendText/"
        f"{settings.evolution_instance_name}"
    )

    payload = {
        "number": telefone,
        "text": texto,
    }

    headers = {
        "apikey": settings.evolution_api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Mensagem enviada para {telefone}")
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erro ao enviar mensagem para {telefone}: {e}")
            raise
