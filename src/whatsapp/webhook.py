"""Endpoint webhook que recebe mensagens da Evolution API."""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.database.connection import SessionLocal
from src.database.models import Conversa, Vendedor
from src.database.queries import buscar_ou_criar_conversa, salvar_mensagem
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
async def receber_mensagem(request: Request, db: Session = Depends(get_db)):
    """
    Recebe webhooks da Evolution API.

    Fluxo:
    1. Recebe o payload JSON
    2. Parseia para extrair dados uteis
    3. Identifica vendedor e lead
    4. Salva mensagem no banco
    """
    payload = await request.json()

    msg = parsear_webhook(payload)
    if msg is None:
        return {"status": "ignorado", "motivo": "evento nao processavel"}

    # Identificar quem eh vendedor e quem eh lead
    if msg.enviada_por_mim:
        lead_telefone = msg.telefone_destinatario
        remetente = "vendedor"
        nome_lead = ""
    else:
        lead_telefone = msg.telefone_remetente
        remetente = "lead"
        nome_lead = msg.nome_contato

    # Identificar o vendedor
    vendedor = None

    # 1. Buscar pelo telefone da instancia (match exato ou parcial)
    instance_phone = msg.instance_phone
    if instance_phone:
        vendedor = (
            db.query(Vendedor)
            .filter(Vendedor.ativo.is_(True), Vendedor.telefone.contains(instance_phone))
            .first()
        )

    # 2. Buscar por conversa existente com esse lead
    if vendedor is None and not msg.enviada_por_mim:
        conversa_existente = (
            db.query(Conversa)
            .join(Vendedor)
            .filter(Conversa.lead_telefone == lead_telefone, Vendedor.ativo.is_(True))
            .first()
        )
        if conversa_existente:
            vendedor = db.query(Vendedor).get(conversa_existente.vendedor_id)

    # 3. Fallback: primeiro vendedor ativo
    if vendedor is None:
        vendedor = db.query(Vendedor).filter_by(ativo=True).first()

    if vendedor is None:
        logger.warning("Nenhum vendedor cadastrado. Mensagem ignorada.")
        return {"status": "ignorado", "motivo": "nenhum vendedor cadastrado"}

    # Buscar ou criar conversa e salvar mensagem
    conversa = buscar_ou_criar_conversa(db, vendedor.id, lead_telefone, nome_lead)

    mensagem = salvar_mensagem(
        db,
        conversa_id=conversa.id,
        remetente=remetente,
        conteudo=msg.conteudo,
        tipo=msg.tipo,
        enviada_em=msg.timestamp,
    )

    logger.info(
        f"Mensagem salva: conversa={conversa.id} "
        f"remetente={remetente} tipo={msg.tipo}"
    )

    return {
        "status": "salvo",
        "conversa_id": conversa.id,
        "mensagem_id": mensagem.id,
    }
