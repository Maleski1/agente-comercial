"""Orquestracao do relatorio diario: calcular -> alertas -> formatar -> enviar — multi-tenant."""

import logging
from datetime import date

from src.config_manager import get_config
from src.database.connection import SessionLocal
from src.database.queries import listar_vendedores
from src.metrics.calculator import calcular_metricas
from src.reports.templates import formatar_tempo, montar_relatorio_completo
from src.whatsapp.sender import enviar_mensagem

logger = logging.getLogger(__name__)


def detectar_alertas(metricas: list[dict], nomes: dict[int, str]) -> list[str]:
    """Analisa metricas e retorna lista de alertas formatados."""
    alertas = []
    for m in metricas:
        nome = nomes.get(m["vendedor_id"], f"Vendedor {m['vendedor_id']}")

        sem_resp = m.get("leads_sem_resposta", 0)
        if sem_resp > 0:
            alertas.append(f"⚠ Leads sem resposta: {nome} ({sem_resp} leads)")

        score = m.get("score_medio")
        if score is not None and score < 5.0:
            alertas.append(f"⚠ Score baixo: {nome} ({score})")

        tempo = m.get("tempo_primeira_resp_seg")
        if tempo is not None and tempo > 600:
            alertas.append(f"⚠ Resposta lenta: {nome} ({formatar_tempo(tempo)})")

    return alertas


def dividir_mensagens(texto: str, limite: int = 4000) -> list[str]:
    """Divide texto em blocos respeitando limite de chars do WhatsApp (~4096)."""
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


async def gerar_e_enviar_relatorio(
    empresa_id: int | None = None, data: str | None = None
) -> dict:
    """Pipeline principal: calcula metricas, gera relatorio, envia ao gestor.

    Args:
        empresa_id: se informado, gera relatorio apenas para essa empresa
        data: formato YYYY-MM-DD (padrao: hoje)
    """
    data = data or date.today().strftime("%Y-%m-%d")
    logger.info(f"Gerando relatorio para {data} empresa={empresa_id}...")

    db = SessionLocal()
    try:
        # 1. Calcular metricas
        metricas = calcular_metricas(db, data, empresa_id=empresa_id)

        # 2. Mapear vendedor_id -> nome
        vendedores = listar_vendedores(db, empresa_id=empresa_id)
        nomes = {v.id: v.nome for v in vendedores}

        # 3. Detectar alertas
        alertas = detectar_alertas(metricas, nomes)

        # 4. Montar texto do relatorio
        texto = montar_relatorio_completo(data, metricas, nomes, alertas)

        # 5. Dividir se necessario e enviar
        gestor_telefone = get_config("gestor_telefone", empresa_id=empresa_id)
        if gestor_telefone:
            partes = dividir_mensagens(texto)
            for parte in partes:
                await enviar_mensagem(gestor_telefone, parte, empresa_id=empresa_id)
        else:
            partes = []
            logger.warning(f"Sem gestor_telefone para empresa {empresa_id}. Relatorio nao enviado.")

        logger.info(
            f"Relatorio gerado: empresa={empresa_id} {len(metricas)} vendedores, "
            f"{len(alertas)} alertas, {len(partes)} mensagem(ns)"
        )

        return {
            "data": data,
            "empresa_id": empresa_id,
            "vendedores": len(metricas),
            "alertas": len(alertas),
            "mensagens_enviadas": len(partes),
        }
    finally:
        db.close()
