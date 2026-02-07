"""Testes do modulo de relatorios: templates, alertas, divisao e pipeline."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Analise, Conversa, Mensagem, MetricaDiaria, Vendedor
from src.main import app
from src.reports.daily import detectar_alertas, dividir_mensagens, gerar_e_enviar_relatorio
from src.reports.templates import (
    formatar_alertas,
    formatar_cabecalho,
    formatar_resumo_geral,
    formatar_tempo,
    formatar_vendedor,
    montar_relatorio_completo,
)


# === Helpers ===


def _metrica(
    vendedor_id: int = 1,
    total_atendimentos: int = 5,
    score_medio: float | None = 7.0,
    total_mql: int = 2,
    total_sql: int = 1,
    total_conversoes: int = 0,
    leads_sem_resposta: int = 0,
    tempo_primeira_resp_seg: int | None = 90,
    tempo_medio_resposta_seg: int | None = 120,
) -> dict:
    return {
        "vendedor_id": vendedor_id,
        "total_atendimentos": total_atendimentos,
        "score_medio": score_medio,
        "total_mql": total_mql,
        "total_sql": total_sql,
        "total_conversoes": total_conversoes,
        "leads_sem_resposta": leads_sem_resposta,
        "tempo_primeira_resp_seg": tempo_primeira_resp_seg,
        "tempo_medio_resposta_seg": tempo_medio_resposta_seg,
    }


# === Testes formatar_tempo ===


def test_formatar_tempo_none():
    assert formatar_tempo(None) == "--"


def test_formatar_tempo_segundos():
    assert formatar_tempo(45) == "45s"


def test_formatar_tempo_minutos_e_segundos():
    assert formatar_tempo(150) == "2min30s"


def test_formatar_tempo_minutos_exatos():
    assert formatar_tempo(120) == "2min"


def test_formatar_tempo_zero():
    assert formatar_tempo(0) == "0s"


# === Testes formatar_cabecalho ===


def test_formatar_cabecalho():
    resultado = formatar_cabecalho("2026-02-07")
    assert "07/02/2026" in resultado
    assert "RELATORIO DIARIO" in resultado


# === Testes formatar_resumo_geral ===


def test_formatar_resumo_geral():
    metricas = [
        _metrica(vendedor_id=1, total_atendimentos=7, score_medio=8.0, total_mql=4, total_sql=2, total_conversoes=1),
        _metrica(vendedor_id=2, total_atendimentos=5, score_medio=6.0, total_mql=2, total_sql=1, total_conversoes=0, leads_sem_resposta=2),
    ]
    texto = formatar_resumo_geral(metricas)
    assert "Total atendimentos: 12" in texto
    assert "Score medio: 7.0" in texto
    assert "MQL: 6" in texto
    assert "SQL: 3" in texto
    assert "Conversoes: 1" in texto
    assert "Leads sem resposta: 2" in texto


def test_formatar_resumo_geral_sem_score():
    metricas = [_metrica(score_medio=None)]
    texto = formatar_resumo_geral(metricas)
    assert "Score medio: --" in texto


# === Testes formatar_vendedor ===


def test_formatar_vendedor():
    m = _metrica(tempo_primeira_resp_seg=105, tempo_medio_resposta_seg=130)
    texto = formatar_vendedor(m, "Joao Silva")
    assert "*Joao Silva*" in texto
    assert "Atendimentos: 5" in texto
    assert "Score: 7.0" in texto
    assert "1a resposta: 1min45s" in texto
    assert "Media: 2min10s" in texto


# === Testes formatar_alertas ===


def test_formatar_alertas_vazio():
    assert formatar_alertas([]) == ""


def test_formatar_alertas_com_itens():
    alertas = ["⚠ Score baixo: Maria (4.2)", "⚠ Resposta lenta: Maria (12min)"]
    texto = formatar_alertas(alertas)
    assert "*ALERTAS*" in texto
    assert "Score baixo" in texto
    assert "Resposta lenta" in texto


# === Testes montar_relatorio_completo ===


def test_montar_relatorio_completo():
    metricas = [_metrica(vendedor_id=1), _metrica(vendedor_id=2)]
    nomes = {1: "Joao", 2: "Maria"}
    alertas = ["⚠ Score baixo: Maria (4.2)"]

    texto = montar_relatorio_completo("2026-02-07", metricas, nomes, alertas)
    assert "RELATORIO DIARIO" in texto
    assert "RESUMO GERAL" in texto
    assert "*Joao*" in texto
    assert "*Maria*" in texto
    assert "ALERTAS" in texto


def test_montar_relatorio_sem_alertas():
    metricas = [_metrica(vendedor_id=1)]
    nomes = {1: "Joao"}
    texto = montar_relatorio_completo("2026-02-07", metricas, nomes, [])
    assert "ALERTAS" not in texto


# === Testes detectar_alertas ===


def test_detectar_alertas_score_baixo():
    metricas = [_metrica(vendedor_id=1, score_medio=4.2)]
    nomes = {1: "Maria"}
    alertas = detectar_alertas(metricas, nomes)
    assert any("Score baixo" in a and "Maria" in a and "4.2" in a for a in alertas)


def test_detectar_alertas_leads_sem_resposta():
    metricas = [_metrica(vendedor_id=1, leads_sem_resposta=3)]
    nomes = {1: "Pedro"}
    alertas = detectar_alertas(metricas, nomes)
    assert any("Leads sem resposta" in a and "Pedro" in a and "3 leads" in a for a in alertas)


def test_detectar_alertas_resposta_lenta():
    metricas = [_metrica(vendedor_id=1, tempo_primeira_resp_seg=750)]
    nomes = {1: "Ana"}
    alertas = detectar_alertas(metricas, nomes)
    assert any("Resposta lenta" in a and "Ana" in a for a in alertas)


def test_detectar_alertas_nenhum():
    metricas = [_metrica(vendedor_id=1, score_medio=8.0, leads_sem_resposta=0, tempo_primeira_resp_seg=60)]
    nomes = {1: "Joao"}
    alertas = detectar_alertas(metricas, nomes)
    assert alertas == []


def test_detectar_alertas_score_none_nao_dispara():
    """score_medio=None nao deve disparar alerta de score baixo."""
    metricas = [_metrica(vendedor_id=1, score_medio=None, leads_sem_resposta=0, tempo_primeira_resp_seg=60)]
    nomes = {1: "Joao"}
    alertas = detectar_alertas(metricas, nomes)
    assert not any("Score baixo" in a for a in alertas)


# === Testes dividir_mensagens ===


def test_dividir_mensagens_curta():
    texto = "Oi"
    assert dividir_mensagens(texto) == ["Oi"]


def test_dividir_mensagens_longa():
    blocos = [f"Bloco {i}: " + "x" * 500 for i in range(10)]
    texto = "\n\n".join(blocos)
    partes = dividir_mensagens(texto, limite=2000)
    assert len(partes) > 1
    # Reconstruir deve ter todo o conteudo
    reconstruido = "\n\n".join(partes)
    assert reconstruido == texto


# === Teste de integracao: gerar_e_enviar_relatorio ===


@pytest.mark.asyncio
async def test_gerar_e_enviar_relatorio_com_mock():
    """Pipeline completo com sender mockado."""
    criar_tabelas()
    db = SessionLocal()
    db.query(MetricaDiaria).delete()
    db.query(Analise).delete()
    db.query(Mensagem).delete()
    db.query(Conversa).delete()
    db.query(Vendedor).delete()

    v = Vendedor(nome="Teste Report", telefone="5511900000099")
    db.add(v)
    db.flush()

    c = Conversa(vendedor_id=v.id, lead_telefone="5511911111199", lead_nome="Lead Test")
    db.add(c)
    db.flush()
    db.add(Mensagem(
        conversa_id=c.id, remetente="lead", conteudo="Oi",
        enviada_em=datetime(2026, 2, 7, 10, 0, 0),
    ))
    db.add(Mensagem(
        conversa_id=c.id, remetente="vendedor", conteudo="Ola!",
        enviada_em=datetime(2026, 2, 7, 10, 2, 0),
    ))
    db.add(Analise(
        conversa_id=c.id, score_qualidade=7.5, classificacao="mql",
        sentimento_lead="positivo", feedback_ia="Bom atendimento",
    ))
    db.commit()
    db.close()

    with patch("src.reports.daily.enviar_mensagem", new_callable=AsyncMock) as mock_enviar:
        mock_enviar.return_value = {"status": "ok"}

        resultado = await gerar_e_enviar_relatorio("2026-02-07")

        assert resultado["data"] == "2026-02-07"
        assert resultado["vendedores"] >= 1
        assert resultado["mensagens_enviadas"] >= 1
        assert mock_enviar.called
        # Verifica que o texto enviado contem o nome do vendedor
        texto_enviado = mock_enviar.call_args_list[0][0][1]
        assert "RELATORIO DIARIO" in texto_enviado


# === Teste endpoint POST /relatorio/enviar ===


def test_endpoint_enviar_relatorio():
    """Testa endpoint manual com sender mockado."""
    criar_tabelas()

    with patch("src.reports.daily.enviar_mensagem", new_callable=AsyncMock) as mock_enviar:
        mock_enviar.return_value = {"status": "ok"}
        client = TestClient(app)
        response = client.post("/relatorio/enviar?data=2026-02-07")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "vendedores" in data
        assert "mensagens_enviadas" in data
