"""Agendamento do relatório diário com APScheduler — multi-tenant."""

import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config_manager import get_config
from src.database.connection import SessionLocal
from src.database.queries import listar_empresas
from src.reports.daily import gerar_e_enviar_relatorio

logger = logging.getLogger(__name__)

TIMEZONE_BR = ZoneInfo("America/Sao_Paulo")

scheduler = AsyncIOScheduler()


async def _job_relatorio_empresa(empresa_id: int):
    """Job de relatório para uma empresa específica."""
    try:
        resultado = await gerar_e_enviar_relatorio(empresa_id=empresa_id)
        logger.info(f"Job relatório empresa {empresa_id} concluído: {resultado}")
    except Exception as e:
        logger.error(f"Erro no job de relatório empresa {empresa_id}: {e}", exc_info=True)


def _carregar_jobs():
    """Carrega (ou recarrega) jobs de todas as empresas ativas."""
    # Remover jobs existentes
    existing_jobs = scheduler.get_jobs()
    for job in existing_jobs:
        if job.id.startswith("relatorio_"):
            job.remove()

    db = SessionLocal()
    try:
        empresas = listar_empresas(db, apenas_ativas=True)
    finally:
        db.close()

    if not empresas:
        # Fallback: scheduler sem empresa (compatibilidade)
        horario = get_config("horario_relatorio", default="20:00")
        hora, minuto = horario.split(":")
        trigger = CronTrigger(
            hour=int(hora), minute=int(minuto), timezone=TIMEZONE_BR,
        )
        scheduler.add_job(
            _job_relatorio_empresa,
            trigger,
            args=[None],
            id="relatorio_sem_empresa",
            replace_existing=True,
        )
        logger.info(f"Scheduler: sem empresas — relatório às {horario} (Brasília)")
    else:
        for empresa in empresas:
            horario = get_config("horario_relatorio", empresa_id=empresa.id, default="20:00")
            hora, minuto = horario.split(":")
            trigger = CronTrigger(
                hour=int(hora), minute=int(minuto), timezone=TIMEZONE_BR,
            )
            scheduler.add_job(
                _job_relatorio_empresa,
                trigger,
                args=[empresa.id],
                id=f"relatorio_empresa_{empresa.id}",
                replace_existing=True,
            )
            logger.info(
                f"Scheduler: empresa '{empresa.nome}' (id={empresa.id}) — "
                f"relatório às {horario} (Brasília)"
            )

    return len(empresas)


def iniciar_scheduler():
    """Inicia o scheduler com um job de relatório por empresa ativa."""
    total = _carregar_jobs()
    scheduler.start()
    logger.info(f"Scheduler iniciado com {total} empresa(s)")


def recarregar_jobs():
    """Recarrega jobs sem reiniciar o scheduler (ex: nova empresa adicionada)."""
    total = _carregar_jobs()
    logger.info(f"Scheduler recarregado com {total} empresa(s)")


def parar_scheduler():
    """Para o scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler parado.")
