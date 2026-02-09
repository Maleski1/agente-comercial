"""Endpoint webhook que recebe mensagens da Evolution API — multi-tenant."""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from src.config import settings
from src.database.connection import SessionLocal
from src.database.models import Conversa, Vendedor
from src.database.queries import (
    buscar_instancia_por_nome,
    buscar_ou_criar_conversa,
    salvar_mensagem,
)
from src.whatsapp.parser import parsear_webhook

logger = logging.getLogger(__name__)
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/webhook/messages")
async def receber_mensagem(
    request: Request,
    db: Session = Depends(get_db),
    apikey: str | None = Header(None),
):
    """
    Recebe webhooks da Evolution API — roteamento multi-tenant.

    Fluxo:
    0. Valida webhook_secret (se configurado)
    1. Parseia o payload
    2. Identifica empresa pela instance_name do payload
    3. Identifica vendedor dentro da empresa
    4. Salva mensagem no banco com empresa_id
    """
    # Validar secret do webhook (se configurado)
    if settings.webhook_secret and apikey != settings.webhook_secret:
        logger.warning("Webhook rejeitado: apikey inválida")
        raise HTTPException(status_code=401, detail="Webhook não autorizado")

    payload = await request.json()

    msg = parsear_webhook(payload)
    if msg is None:
        return {"status": "ignorado", "motivo": "evento nao processavel"}

    # --- Identificar empresa pela instancia ---
    instancia = buscar_instancia_por_nome(db, msg.instance_name)
    if not instancia:
        logger.warning(f"Instancia '{msg.instance_name}' nao registrada. Mensagem ignorada.")
        return {"status": "ignorado", "motivo": "instancia nao registrada"}

    empresa_id = instancia.empresa_id

    # --- Identificar quem eh vendedor e quem eh lead ---
    if msg.enviada_por_mim:
        lead_telefone = msg.telefone_destinatario
        remetente = "vendedor"
        nome_lead = ""
    else:
        lead_telefone = msg.telefone_remetente
        remetente = "lead"
        nome_lead = msg.nome_contato

    # --- Identificar o vendedor DENTRO da empresa ---
    vendedor = None

    # 1. Buscar pelo telefone da instancia (match exato ou parcial)
    instance_phone = msg.instance_phone
    if instance_phone:
        vendedor = (
            db.query(Vendedor)
            .filter(
                Vendedor.empresa_id == empresa_id,
                Vendedor.ativo.is_(True),
                Vendedor.telefone.contains(instance_phone),
            )
            .first()
        )

    # 2. Buscar por conversa existente com esse lead (dentro da empresa)
    if vendedor is None and not msg.enviada_por_mim:
        conversa_existente = (
            db.query(Conversa)
            .join(Vendedor)
            .filter(
                Conversa.empresa_id == empresa_id,
                Conversa.lead_telefone == lead_telefone,
                Vendedor.ativo.is_(True),
            )
            .first()
        )
        if conversa_existente:
            vendedor = db.get(Vendedor, conversa_existente.vendedor_id)

    # 3. Fallback: primeiro vendedor ativo DA EMPRESA
    if vendedor is None:
        vendedor = (
            db.query(Vendedor)
            .filter(Vendedor.empresa_id == empresa_id, Vendedor.ativo.is_(True))
            .first()
        )

    if vendedor is None:
        logger.warning(f"Nenhum vendedor na empresa {empresa_id}. Mensagem ignorada.")
        return {"status": "ignorado", "motivo": "nenhum vendedor na empresa"}

    # --- Buscar ou criar conversa e salvar mensagem ---
    conversa = buscar_ou_criar_conversa(
        db, vendedor.id, lead_telefone, nome_lead, empresa_id=empresa_id
    )

    mensagem = salvar_mensagem(
        db,
        conversa_id=conversa.id,
        remetente=remetente,
        conteudo=msg.conteudo,
        tipo=msg.tipo,
        enviada_em=msg.timestamp,
    )

    logger.info(
        f"Mensagem salva: empresa={empresa_id} conversa={conversa.id} "
        f"remetente={remetente} tipo={msg.tipo}"
    )

    return {
        "status": "salvo",
        "empresa_id": empresa_id,
        "conversa_id": conversa.id,
        "mensagem_id": mensagem.id,
    }
