"""Ponto de entrada do Agente Comercial."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from sqlalchemy.orm import Session

from src.config import settings
from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Conversa, Mensagem, Vendedor
from src.analysis.router import router as analysis_router
from src.metrics.router import router as metrics_router
from src.reports.router import router as reports_router
from src.reports.scheduler import iniciar_scheduler, parar_scheduler, recarregar_jobs
from src.whatsapp.webhook import router as webhook_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando Agente Comercial...")
    criar_tabelas()
    logger.info("Banco de dados pronto.")
    iniciar_scheduler()
    yield
    # Shutdown
    parar_scheduler()
    logger.info("Agente Comercial encerrado.")


# Criar app FastAPI
app = FastAPI(
    title="Agente Comercial",
    description="Sistema de análise de atendimentos comerciais no WhatsApp",
    version="1.0.0",
    lifespan=lifespan,
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


def validar_admin_key(x_admin_key: str = Header(...)):
    """Valida admin_key no header para endpoints internos."""
    if x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Admin key inválida")


@app.get("/")
async def root():
    return {
        "app": "Agente Comercial",
        "versao": "1.0.0",
        "status": "rodando",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/vendedores", dependencies=[Depends(validar_admin_key)])
async def api_listar_vendedores(
    empresa_id: int = Query(..., description="ID da empresa"),
    db: Session = Depends(get_db),
):
    """Lista vendedores de uma empresa (requer admin_key)."""
    vendedores = (
        db.query(Vendedor)
        .filter(Vendedor.empresa_id == empresa_id)
        .all()
    )
    return [
        {"id": v.id, "nome": v.nome, "telefone": v.telefone, "ativo": v.ativo}
        for v in vendedores
    ]


@app.get("/conversas", dependencies=[Depends(validar_admin_key)])
async def api_listar_conversas(
    empresa_id: int = Query(..., description="ID da empresa"),
    db: Session = Depends(get_db),
):
    """Lista conversas de uma empresa (requer admin_key)."""
    conversas = (
        db.query(Conversa)
        .filter(Conversa.empresa_id == empresa_id)
        .order_by(Conversa.atualizada_em.desc())
        .all()
    )
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


@app.get("/conversas/{conversa_id}/mensagens", dependencies=[Depends(validar_admin_key)])
async def api_listar_mensagens(conversa_id: int, db: Session = Depends(get_db)):
    """Lista mensagens de uma conversa (requer admin_key)."""
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


@app.post("/admin/scheduler/reload", dependencies=[Depends(validar_admin_key)])
async def api_recarregar_scheduler():
    """Recarrega jobs do scheduler (útil após adicionar nova empresa)."""
    recarregar_jobs()
    return {"status": "ok", "mensagem": "Jobs do scheduler recarregados"}


