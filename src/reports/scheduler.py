"""Agendamento do relatorio diario com APScheduler."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.reports.daily import gerar_e_enviar_relatorio

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _job_relatorio():
    """Wrapper do job para capturar erros sem crashar o scheduler."""
    try:
        resultado = await gerar_e_enviar_relatorio()
        logger.info(f"Job relatorio concluido: {resultado}")
    except Exception as e:
        logger.error(f"Erro no job de relatorio: {e}", exc_info=True)


def iniciar_scheduler():
    """Inicia o scheduler com o job de relatorio diario."""
    hora, minuto = settings.horario_relatorio.split(":")
    trigger = CronTrigger(hour=int(hora), minute=int(minuto))

    scheduler.add_job(_job_relatorio, trigger, id="relatorio_diario", replace_existing=True)
    scheduler.start()
    logger.info(f"Scheduler iniciado - relatorio diario as {settings.horario_relatorio}")


def parar_scheduler():
    """Para o scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler parado.")
