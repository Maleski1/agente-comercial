"""Endpoints de analise de conversas."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.analysis.analyzer import analisar_conversa
from src.database.connection import get_db
from src.database.queries import (
    buscar_analises_por_conversa,
    buscar_conversa_com_mensagens,
    salvar_analise,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analise"])


@router.post("/analisar/{conversa_id}")
async def analisar(conversa_id: int, db: Session = Depends(get_db)):
    """Analisa uma conversa com IA e salva o resultado."""
    conversa = buscar_conversa_com_mensagens(db, conversa_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada.")

    if not conversa.mensagens:
        raise HTTPException(status_code=400, detail="Conversa sem mensagens.")

    mensagens = [
        {
            "remetente": m.remetente,
            "conteudo": m.conteudo,
            "enviada_em": str(m.enviada_em),
        }
        for m in conversa.mensagens
    ]

    try:
        resultado = await analisar_conversa(mensagens)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=500, detail=str(e))

    analise = salvar_analise(
        db=db,
        conversa_id=conversa_id,
        score_qualidade=resultado.score_qualidade,
        classificacao=resultado.classificacao,
        erros=resultado.erros,
        sentimento_lead=resultado.sentimento_lead,
        feedback_ia=resultado.feedback_ia,
    )

    return {
        "analise_id": analise.id,
        "score_qualidade": analise.score_qualidade,
        "classificacao": analise.classificacao,
        "erros": resultado.erros,
        "sentimento_lead": analise.sentimento_lead,
        "feedback_ia": analise.feedback_ia,
    }


@router.get("/analises/{conversa_id}")
async def listar_analises(conversa_id: int, db: Session = Depends(get_db)):
    """Lista todas as analises de uma conversa."""
    analises = buscar_analises_por_conversa(db, conversa_id)
    if not analises:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma analise encontrada para esta conversa.",
        )

    return [
        {
            "analise_id": a.id,
            "score_qualidade": a.score_qualidade,
            "classificacao": a.classificacao,
            "erros": json.loads(a.erros) if a.erros else [],
            "sentimento_lead": a.sentimento_lead,
            "feedback_ia": a.feedback_ia,
            "analisada_em": str(a.analisada_em),
        }
        for a in analises
    ]
