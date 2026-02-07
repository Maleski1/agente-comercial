"""Endpoint para trigger manual do relatorio."""

from datetime import date

from fastapi import APIRouter, Query

from src.reports.daily import gerar_e_enviar_relatorio

router = APIRouter(tags=["relatorios"])


@router.post("/relatorio/enviar")
async def enviar_relatorio(
    data: str = Query(default=None, description="Data no formato YYYY-MM-DD (padrao: hoje)"),
):
    """Gera e envia o relatorio diario manualmente."""
    data = data or date.today().strftime("%Y-%m-%d")
    resultado = await gerar_e_enviar_relatorio(data)
    return resultado
