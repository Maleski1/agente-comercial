"""Envio de mensagens via Evolution API — multi-tenant."""

import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config_manager import get_config
from src.database.connection import SessionLocal
from src.database.queries import listar_instancias_empresa

logger = logging.getLogger(__name__)

SEND_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


async def enviar_mensagem(
    telefone: str, texto: str, empresa_id: int | None = None
) -> dict:
    """
    Envia uma mensagem de texto via Evolution API.

    Args:
        telefone: Número com código do país (ex: 5511999999999)
        texto: Texto da mensagem
        empresa_id: se informado, busca instância ativa da empresa
    """
    # Determinar qual instância usar
    instance_name = None
    if empresa_id is not None:
        db = SessionLocal()
        try:
            instancias = listar_instancias_empresa(db, empresa_id)
            ativas = [i for i in instancias if i.ativa]
            if ativas:
                instance_name = ativas[0].nome_instancia
        finally:
            db.close()

    if instance_name is None:
        instance_name = get_config("evolution_instance_name", empresa_id=empresa_id)

    url = (
        f"{get_config('evolution_api_url')}/message/sendText/"
        f"{instance_name}"
    )

    payload = {
        "number": telefone,
        "text": texto,
    }

    headers = {
        "apikey": get_config("evolution_api_key"),
        "Content-Type": "application/json",
    }

    return await _enviar_com_retry(url, payload, headers, telefone, instance_name)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True,
)
async def _enviar_com_retry(
    url: str, payload: dict, headers: dict, telefone: str, instance_name: str,
) -> dict:
    """Envia mensagem com retry automático (3 tentativas, backoff exponencial)."""
    async with httpx.AsyncClient(timeout=SEND_TIMEOUT) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Mensagem enviada para {telefone} via {instance_name}")
            return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Timeout ao enviar mensagem para {telefone}: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao enviar para {telefone} (tentará retry): {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Erro de conexão ao enviar para {telefone}: {e}")
            raise
