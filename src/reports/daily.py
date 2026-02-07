"""Orquestracao do relatorio diario: calcular -> alertas -> formatar -> enviar."""

import logging
from datetime import date

from src.config import settings
from src.database.connection import SessionLocal
from src.database.queries import listar_vendedores
from src.metrics.calculator import calcular_metricas
from src.reports.templates import formatar_tempo, montar_relatorio_completo
from src.whatsapp.sender import enviar_mensagem

logger = logging.getLogger(__name__)


def detectar_alertas(metricas: list[dict], nomes: dict[int, str]) -> list[str]:
    """Analisa metricas e retorna lista de alertas formatados.

    Regras:
    - score_medio < 5.0 -> alerta score baixo
    - leads_sem_resposta > 0 -> alerta leads ignorados
    - tempo_primeira_resp_seg > 600 (10min) -> alerta resposta lenta
    """
    alertas = []
    for m in metricas:
        nome = nomes.get(m["vendedor_id"], f"Vendedor {m['vendedor_id']}")

        # Leads ignorados primeiro — mais urgente para o gestor
        sem_resp = m.get("leads_sem_resposta", 0)
        if sem_resp > 0:
            alertas.append(f"⚠ Leads sem resposta: {nome} ({sem_resp} leads)")

        # Score de qualidade baixo
        score = m.get("score_medio")
        if score is not None and score < 5.0:
            alertas.append(f"⚠ Score baixo: {nome} ({score})")

        # Primeira resposta acima de 10 minutos
        tempo = m.get("tempo_primeira_resp_seg")
        if tempo is not None and tempo > 600:
            alertas.append(f"⚠ Resposta lenta: {nome} ({formatar_tempo(tempo)})")

    return alertas


def dividir_mensagens(texto: str, limite: int = 4000) -> list[str]:
    """Divide texto em blocos respeitando limite de chars do WhatsApp (~4096).

    Quebra nos separadores '\\n\\n' para nao cortar no meio de uma secao.
    """
    if len(texto) <= limite:
        return [texto]

    partes = []
    blocos = texto.split("\n\n")
    parte_atual = ""

    for bloco in blocos:
        candidato = f"{parte_atual}\n\n{bloco}" if parte_atual else bloco
        if len(candidato) <= limite:
            parte_atual = candidato
        else:
            if parte_atual:
                partes.append(parte_atual)
            parte_atual = bloco

    if parte_atual:
        partes.append(parte_atual)

    return partes


async def gerar_e_enviar_relatorio(data: str | None = None) -> dict:
    """Pipeline principal: calcula metricas, gera relatorio, envia ao gestor.

    Usa SessionLocal() direto (nao Depends) porque pode ser chamado
    pelo scheduler fora do contexto HTTP.
    """
    data = data or date.today().strftime("%Y-%m-%d")
    logger.info(f"Gerando relatorio para {data}...")

    db = SessionLocal()
    try:
        # 1. Calcular metricas de todos os vendedores
        metricas = calcular_metricas(db, data)

        # 2. Mapear vendedor_id -> nome
        vendedores = listar_vendedores(db)
        nomes = {v.id: v.nome for v in vendedores}

        # 3. Detectar alertas
        alertas = detectar_alertas(metricas, nomes)

        # 4. Montar texto do relatorio
        texto = montar_relatorio_completo(data, metricas, nomes, alertas)

        # 5. Dividir se necessario e enviar
        partes = dividir_mensagens(texto)
        for parte in partes:
            await enviar_mensagem(settings.gestor_telefone, parte)

        logger.info(
            f"Relatorio enviado: {len(metricas)} vendedores, "
            f"{len(alertas)} alertas, {len(partes)} mensagem(ns)"
        )

        return {
            "data": data,
            "vendedores": len(metricas),
            "alertas": len(alertas),
            "mensagens_enviadas": len(partes),
        }
    finally:
        db.close()
