"""Motor de calculo de metricas diarias por vendedor."""

import logging
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import Conversa, Mensagem
from src.database.queries import (
    buscar_conversas_do_dia,
    listar_vendedores,
    upsert_metrica_diaria,
)

logger = logging.getLogger(__name__)


@dataclass
class TemposResposta:
    primeira_resposta_seg: int | None
    media_resposta_seg: int | None


def calcular_tempos_resposta(mensagens: list[Mensagem]) -> TemposResposta:
    """Calcula tempo de primeira resposta e tempo medio de resposta.

    Percorre mensagens cronologicamente:
    - Primeira resposta: delta entre 1a msg do lead e 1a resposta do vendedor
    - Media: cada vez que lead manda msg, mede delta ate proxima resposta do vendedor

    Args:
        mensagens: lista de Mensagem ordenada por enviada_em

    Returns:
        TemposResposta com valores em segundos, ou None se nao aplicavel
    """
    primeira_resposta: int | None = None
    deltas: list[int] = []
    timestamp_lead: datetime | None = None

    for msg in mensagens:
        if msg.remetente == "lead":
            if timestamp_lead is None:
                timestamp_lead = msg.enviada_em
        elif msg.remetente == "vendedor" and timestamp_lead is not None:
            delta = int((msg.enviada_em - timestamp_lead).total_seconds())
            if primeira_resposta is None:
                primeira_resposta = delta
            deltas.append(delta)
            timestamp_lead = None

    media = round(sum(deltas) / len(deltas)) if deltas else None
    return TemposResposta(primeira_resposta_seg=primeira_resposta, media_resposta_seg=media)


def _contar_funil(conversas: list[Conversa]) -> dict[str, int]:
    """Conta conversas por classificacao da analise mais recente."""
    contagem = {"mql": 0, "sql": 0, "cliente": 0}
    for conversa in conversas:
        if not conversa.analises:
            continue
        mais_recente = max(conversa.analises, key=lambda a: a.analisada_em)
        if mais_recente.classificacao in contagem:
            contagem[mais_recente.classificacao] += 1
    return contagem


def _calcular_score_medio(conversas: list[Conversa]) -> float | None:
    """Media dos score_qualidade das analises mais recentes."""
    scores = []
    for conversa in conversas:
        if not conversa.analises:
            continue
        mais_recente = max(conversa.analises, key=lambda a: a.analisada_em)
        if mais_recente.score_qualidade is not None:
            scores.append(mais_recente.score_qualidade)
    return round(sum(scores) / len(scores), 1) if scores else None


def _contar_leads_sem_resposta(conversas: list[Conversa]) -> int:
    """Conta conversas onde lead mandou msg mas vendedor nunca respondeu."""
    sem_resposta = 0
    for conversa in conversas:
        tem_lead = any(m.remetente == "lead" for m in conversa.mensagens)
        tem_vendedor = any(m.remetente == "vendedor" for m in conversa.mensagens)
        if tem_lead and not tem_vendedor:
            sem_resposta += 1
    return sem_resposta


def calcular_metricas_vendedor(
    db: Session, vendedor_id: int, data: str, conversas: list[Conversa]
) -> dict:
    """Calcula e persiste metricas de um vendedor para um dia."""
    funil = _contar_funil(conversas)
    score = _calcular_score_medio(conversas)
    sem_resposta = _contar_leads_sem_resposta(conversas)

    # Calcular tempos de resposta agregados
    tempos_primeira = []
    tempos_media = []
    for conversa in conversas:
        if not conversa.mensagens:
            continue
        tempos = calcular_tempos_resposta(conversa.mensagens)
        if tempos.primeira_resposta_seg is not None:
            tempos_primeira.append(tempos.primeira_resposta_seg)
        if tempos.media_resposta_seg is not None:
            tempos_media.append(tempos.media_resposta_seg)

    primeira_resp = (
        round(sum(tempos_primeira) / len(tempos_primeira))
        if tempos_primeira
        else None
    )
    media_resp = (
        round(sum(tempos_media) / len(tempos_media))
        if tempos_media
        else None
    )

    valores = {
        "total_atendimentos": len(conversas),
        "tempo_primeira_resp_seg": primeira_resp,
        "tempo_medio_resposta_seg": media_resp,
        "total_mql": funil["mql"],
        "total_sql": funil["sql"],
        "total_conversoes": funil["cliente"],
        "score_medio": score,
        "leads_sem_resposta": sem_resposta,
    }

    metrica = upsert_metrica_diaria(db, vendedor_id, data, **valores)
    logger.info(f"Metricas calculadas: vendedor={vendedor_id} data={data} atendimentos={len(conversas)}")

    return {
        "metrica_id": metrica.id,
        "vendedor_id": vendedor_id,
        "data": data,
        **valores,
    }


def calcular_metricas(
    db: Session, data: str, vendedor_id: int | None = None
) -> list[dict]:
    """Calcula metricas para um ou todos os vendedores num dia.

    Args:
        data: formato YYYY-MM-DD
        vendedor_id: se informado, calcula so para esse vendedor
    """
    if vendedor_id is not None:
        conversas = buscar_conversas_do_dia(db, data, vendedor_id)
        return [calcular_metricas_vendedor(db, vendedor_id, data, conversas)]

    vendedores = listar_vendedores(db)
    resultados = []
    for vendedor in vendedores:
        conversas = buscar_conversas_do_dia(db, data, vendedor.id)
        resultado = calcular_metricas_vendedor(db, vendedor.id, data, conversas)
        resultados.append(resultado)

    return resultados
