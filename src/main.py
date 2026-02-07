"""Ponto de entrada do Agente Comercial."""

import logging

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Conversa, Mensagem, Vendedor
from src.analysis.router import router as analysis_router
from src.metrics.router import router as metrics_router
from src.reports.router import router as reports_router
from src.reports.scheduler import iniciar_scheduler, parar_scheduler
from src.whatsapp.webhook import router as webhook_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(
    title="Agente Comercial",
    description="Sistema de analise de atendimentos comerciais no WhatsApp",
    version="0.1.0",
)

# Registrar rotas
app.include_router(webhook_router)
app.include_router(analysis_router)
app.include_router(metrics_router)
app.include_router(reports_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    logger.info("Iniciando Agente Comercial...")
    criar_tabelas()
    logger.info("Banco de dados pronto.")
    iniciar_scheduler()


@app.on_event("shutdown")
async def shutdown():
    parar_scheduler()
    logger.info("Agente Comercial encerrado.")


@app.get("/")
async def root():
    return {
        "app": "Agente Comercial",
        "versao": "0.1.0",
        "status": "rodando",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


class VendedorCreate(BaseModel):
    nome: str
    telefone: str


@app.get("/vendedores")
async def listar_vendedores(db: Session = Depends(get_db)):
    vendedores = db.query(Vendedor).all()
    return [
        {"id": v.id, "nome": v.nome, "telefone": v.telefone, "ativo": v.ativo}
        for v in vendedores
    ]


@app.post("/vendedores", status_code=201)
async def criar_vendedor(data: VendedorCreate, db: Session = Depends(get_db)):
    existente = db.query(Vendedor).filter(Vendedor.telefone == data.telefone).first()
    if existente:
        return {"id": existente.id, "nome": existente.nome, "telefone": existente.telefone, "ja_existia": True}
    vendedor = Vendedor(nome=data.nome, telefone=data.telefone)
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return {"id": vendedor.id, "nome": vendedor.nome, "telefone": vendedor.telefone}


@app.get("/conversas")
async def listar_conversas(db: Session = Depends(get_db)):
    conversas = db.query(Conversa).order_by(Conversa.atualizada_em.desc()).all()
    return [
        {
            "id": c.id,
            "vendedor_id": c.vendedor_id,
            "lead_telefone": c.lead_telefone,
            "lead_nome": c.lead_nome,
            "status": c.status,
            "iniciada_em": str(c.iniciada_em),
            "atualizada_em": str(c.atualizada_em),
        }
        for c in conversas
    ]


@app.get("/conversas/{conversa_id}/mensagens")
async def listar_mensagens(conversa_id: int, db: Session = Depends(get_db)):
    mensagens = (
        db.query(Mensagem)
        .filter_by(conversa_id=conversa_id)
        .order_by(Mensagem.enviada_em)
        .all()
    )
    return [
        {
            "id": m.id,
            "remetente": m.remetente,
            "conteudo": m.conteudo,
            "tipo": m.tipo,
            "enviada_em": str(m.enviada_em),
        }
        for m in mensagens
    ]
