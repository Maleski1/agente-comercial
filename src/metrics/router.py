"""Endpoints de metricas diarias — multi-tenant."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.queries import buscar_metricas_dia, buscar_metricas_vendedor
from src.metrics.calculator import calcular_metricas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metricas", tags=["metricas"])


@router.post("/calcular")
def calcular(
    data: str = Query(default=None, description="Data no formato YYYY-MM-DD (padrao: hoje)"),
    vendedor_id: int | None = Query(default=None, description="ID do vendedor (padrao: todos)"),
    empresa_id: int | None = Query(default=None, description="ID da empresa"),
    db: Session = Depends(get_db),
):
    """Calcula metricas diarias para um ou todos os vendedores."""
    if data is None:
        data = date.today().isoformat()

    try:
        resultados = calcular_metricas(db, data, vendedor_id, empresa_id=empresa_id)
    except Exception as e:
        logger.error(f"Erro ao calcular metricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"data": data, "metricas": resultados}


@router.get("/vendedor/{vendedor_id}")
def metricas_vendedor(
    vendedor_id: int,
    limit: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Historico de metricas de um vendedor."""
    metricas = buscar_metricas_vendedor(db, vendedor_id, limit)
    if not metricas:
        raise HTTPException(status_code=404, detail="Nenhuma metrica encontrada.")

    return [
        {
            "data": m.data,
            "total_atendimentos": m.total_atendimentos,
            "tempo_primeira_resp_seg": m.tempo_primeira_resp_seg,
            "tempo_medio_resposta_seg": m.tempo_medio_resposta_seg,
            "total_mql": m.total_mql,
            "total_sql": m.total_sql,
            "total_conversoes": m.total_conversoes,
            "score_medio": m.score_medio,
            "leads_sem_resposta": m.leads_sem_resposta,
        }
        for m in metricas
    ]


@router.get("/dia/{data}")
def metricas_dia(
    data: str,
    empresa_id: int | None = Query(default=None, description="ID da empresa"),
    db: Session = Depends(get_db),
):
    """Metricas de todos os vendedores num dia."""
    metricas = buscar_metricas_dia(db, data, empresa_id=empresa_id)
    if not metricas:
        raise HTTPException(status_code=404, detail="Nenhuma metrica encontrada para este dia.")

    return [
        {
            "vendedor_id": m.vendedor_id,
            "total_atendimentos": m.total_atendimentos,
            "tempo_primeira_resp_seg": m.tempo_primeira_resp_seg,
            "tempo_medio_resposta_seg": m.tempo_medio_resposta_seg,
            "total_mql": m.total_mql,
            "total_sql": m.total_sql,
            "total_conversoes": m.total_conversoes,
            "score_medio": m.score_medio,
            "leads_sem_resposta": m.leads_sem_resposta,
        }
        for m in metricas
    ]


@router.get("/ranking/{data}")
def ranking(
    data: str,
    empresa_id: int | None = Query(default=None, description="ID da empresa"),
    db: Session = Depends(get_db),
):
    """Ranking de vendedores no dia, ordenado por score_medio decrescente."""
    metricas = buscar_metricas_dia(db, data, empresa_id=empresa_id)
    if not metricas:
        raise HTTPException(status_code=404, detail="Nenhuma metrica encontrada para este dia.")

    ranking = sorted(
        metricas,
        key=lambda m: (m.score_medio or 0, m.total_atendimentos),
        reverse=True,
    )

    return [
        {
            "posicao": i + 1,
            "vendedor_id": m.vendedor_id,
            "score_medio": m.score_medio,
            "total_atendimentos": m.total_atendimentos,
            "total_conversoes": m.total_conversoes,
            "leads_sem_resposta": m.leads_sem_resposta,
        }
        for i, m in enumerate(ranking)
    ]
