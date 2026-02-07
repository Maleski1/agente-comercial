"""Testes do motor de metricas com fixtures de timestamps controlados."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Analise, Conversa, Mensagem, MetricaDiaria, Vendedor
from src.main import app
from src.metrics.calculator import (
    TemposResposta,
    _calcular_score_medio,
    _contar_funil,
    _contar_leads_sem_resposta,
    calcular_tempos_resposta,
)


# === Helpers ===


def _make_msg(remetente: str, minuto: int, conteudo: str = "msg") -> MagicMock:
    """Cria mock de Mensagem com enviada_em controlado."""
    msg = MagicMock(spec=Mensagem)
    msg.remetente = remetente
    msg.enviada_em = datetime(2026, 2, 7, 10, minuto, 0)
    msg.conteudo = conteudo
    return msg


def _make_conversa(
    mensagens: list, classificacao: str | None = None, score: float | None = None
) -> MagicMock:
    """Cria mock de Conversa com mensagens e analise opcional."""
    conversa = MagicMock(spec=Conversa)
    conversa.mensagens = mensagens
    if classificacao is not None:
        analise = MagicMock(spec=Analise)
        analise.classificacao = classificacao
        analise.score_qualidade = score
        analise.analisada_em = datetime(2026, 2, 7, 12, 0, 0)
        conversa.analises = [analise]
    else:
        conversa.analises = []
    return conversa


# === Testes calcular_tempos_resposta ===


def test_tempos_resposta_basico():
    """Lead manda no minuto 0, vendedor responde no minuto 2."""
    msgs = [
        _make_msg("lead", 0),
        _make_msg("vendedor", 2),
    ]
    result = calcular_tempos_resposta(msgs)
    assert result.primeira_resposta_seg == 120
    assert result.media_resposta_seg == 120


def test_tempos_resposta_multiplos_turnos():
    """Dois turnos: lead->vendedor, lead->vendedor."""
    msgs = [
        _make_msg("lead", 0),       # lead fala min 0
        _make_msg("vendedor", 1),    # vendedor responde min 1 (60s)
        _make_msg("lead", 5),        # lead fala min 5
        _make_msg("vendedor", 8),    # vendedor responde min 8 (180s)
    ]
    result = calcular_tempos_resposta(msgs)
    assert result.primeira_resposta_seg == 60
    assert result.media_resposta_seg == 120  # (60 + 180) / 2


def test_tempos_resposta_vendedor_nunca_respondeu():
    """Lead manda msg mas vendedor nao responde -> None."""
    msgs = [_make_msg("lead", 0), _make_msg("lead", 5)]
    result = calcular_tempos_resposta(msgs)
    assert result.primeira_resposta_seg is None
    assert result.media_resposta_seg is None


def test_tempos_resposta_sem_mensagens():
    """Lista vazia -> None."""
    result = calcular_tempos_resposta([])
    assert result.primeira_resposta_seg is None
    assert result.media_resposta_seg is None


def test_tempos_resposta_so_vendedor():
    """So vendedor mandou msg (sem lead) -> None."""
    msgs = [_make_msg("vendedor", 0), _make_msg("vendedor", 5)]
    result = calcular_tempos_resposta(msgs)
    assert result.primeira_resposta_seg is None
    assert result.media_resposta_seg is None


def test_tempos_resposta_vendedor_mensagens_consecutivas():
    """Vendedor manda 2 msgs seguidas - so conta 1 delta."""
    msgs = [
        _make_msg("lead", 0),
        _make_msg("vendedor", 1),    # 60s - conta
        _make_msg("vendedor", 2),    # ignorada (lead nao falou de novo)
    ]
    result = calcular_tempos_resposta(msgs)
    assert result.primeira_resposta_seg == 60
    assert result.media_resposta_seg == 60


# === Testes _contar_funil ===


def test_contar_funil_basico():
    conversas = [
        _make_conversa([], classificacao="mql", score=7.0),
        _make_conversa([], classificacao="sql", score=8.0),
        _make_conversa([], classificacao="mql", score=6.0),
        _make_conversa([], classificacao="cliente", score=9.0),
    ]
    funil = _contar_funil(conversas)
    assert funil == {"mql": 2, "sql": 1, "cliente": 1}


def test_contar_funil_sem_analise():
    """Conversas sem analise nao contam."""
    conversas = [_make_conversa([], classificacao=None)]
    funil = _contar_funil(conversas)
    assert funil == {"mql": 0, "sql": 0, "cliente": 0}


def test_contar_funil_classificacao_frio():
    """Classificacao 'frio' nao entra no funil mql/sql/cliente."""
    conversas = [_make_conversa([], classificacao="frio", score=3.0)]
    funil = _contar_funil(conversas)
    assert funil == {"mql": 0, "sql": 0, "cliente": 0}


# === Testes _calcular_score_medio ===


def test_score_medio_basico():
    conversas = [
        _make_conversa([], classificacao="mql", score=8.0),
        _make_conversa([], classificacao="sql", score=6.0),
    ]
    assert _calcular_score_medio(conversas) == 7.0


def test_score_medio_sem_analise():
    conversas = [_make_conversa([], classificacao=None)]
    assert _calcular_score_medio(conversas) is None


# === Testes _contar_leads_sem_resposta ===


def test_leads_sem_resposta():
    conversas = [
        _make_conversa([_make_msg("lead", 0)]),                          # sem resposta
        _make_conversa([_make_msg("lead", 0), _make_msg("vendedor", 1)]),  # com resposta
        _make_conversa([_make_msg("lead", 0), _make_msg("lead", 5)]),    # sem resposta
    ]
    assert _contar_leads_sem_resposta(conversas) == 2


def test_leads_sem_resposta_so_vendedor():
    """So vendedor falou - nao conta como 'sem resposta'."""
    conversas = [_make_conversa([_make_msg("vendedor", 0)])]
    assert _contar_leads_sem_resposta(conversas) == 0


# === Testes de endpoint (integracao) ===


def _setup_dados_metricas():
    """Cria vendedor + conversas + mensagens + analises para testes de endpoint."""
    criar_tabelas()
    db = SessionLocal()
    db.query(MetricaDiaria).delete()
    db.query(Analise).delete()
    db.query(Mensagem).delete()
    db.query(Conversa).delete()
    db.query(Vendedor).delete()

    vendedor = Vendedor(nome="Vendedor Metricas", telefone="5511900000001")
    db.add(vendedor)
    db.flush()

    # Conversa 1: lead + vendedor (com analise mql)
    c1 = Conversa(vendedor_id=vendedor.id, lead_telefone="5511911111111", lead_nome="Lead 1")
    db.add(c1)
    db.flush()
    db.add(Mensagem(
        conversa_id=c1.id, remetente="lead", conteudo="Oi",
        enviada_em=datetime(2026, 2, 7, 10, 0, 0),
    ))
    db.add(Mensagem(
        conversa_id=c1.id, remetente="vendedor", conteudo="Ola!",
        enviada_em=datetime(2026, 2, 7, 10, 2, 0),
    ))
    db.add(Analise(
        conversa_id=c1.id, score_qualidade=8.0, classificacao="mql",
        sentimento_lead="positivo", feedback_ia="Bom",
    ))

    # Conversa 2: lead sem resposta (sem analise)
    c2 = Conversa(vendedor_id=vendedor.id, lead_telefone="5511922222222", lead_nome="Lead 2")
    db.add(c2)
    db.flush()
    db.add(Mensagem(
        conversa_id=c2.id, remetente="lead", conteudo="Alo?",
        enviada_em=datetime(2026, 2, 7, 14, 0, 0),
    ))

    db.commit()
    vid = vendedor.id
    db.close()
    return vid


def test_endpoint_calcular_metricas():
    vid = _setup_dados_metricas()
    client = TestClient(app)

    response = client.post(f"/metricas/calcular?data=2026-02-07&vendedor_id={vid}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == "2026-02-07"
    assert len(data["metricas"]) == 1

    m = data["metricas"][0]
    assert m["total_atendimentos"] == 2
    assert m["tempo_primeira_resp_seg"] == 120  # 2 minutos
    assert m["total_mql"] == 1
    assert m["leads_sem_resposta"] == 1


def test_endpoint_metricas_vendedor():
    vid = _setup_dados_metricas()
    client = TestClient(app)

    # Calcular primeiro
    client.post(f"/metricas/calcular?data=2026-02-07&vendedor_id={vid}")

    response = client.get(f"/metricas/vendedor/{vid}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["data"] == "2026-02-07"


def test_endpoint_metricas_dia():
    vid = _setup_dados_metricas()
    client = TestClient(app)

    client.post(f"/metricas/calcular?data=2026-02-07&vendedor_id={vid}")

    response = client.get("/metricas/dia/2026-02-07")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_endpoint_ranking():
    vid = _setup_dados_metricas()
    client = TestClient(app)

    client.post(f"/metricas/calcular?data=2026-02-07&vendedor_id={vid}")

    response = client.get("/metricas/ranking/2026-02-07")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["posicao"] == 1


def test_endpoint_metricas_dia_inexistente():
    client = TestClient(app)
    response = client.get("/metricas/dia/2020-01-01")
    assert response.status_code == 404


if __name__ == "__main__":
    print("=" * 60)
    print("  TESTES DE METRICAS - AGENTE COMERCIAL")
    print("=" * 60)

    test_tempos_resposta_basico()
    print("  [OK] tempos_resposta basico")

    test_tempos_resposta_multiplos_turnos()
    print("  [OK] tempos_resposta multiplos turnos")

    test_tempos_resposta_vendedor_nunca_respondeu()
    print("  [OK] tempos_resposta vendedor nunca respondeu")

    test_tempos_resposta_sem_mensagens()
    print("  [OK] tempos_resposta sem mensagens")

    test_tempos_resposta_so_vendedor()
    print("  [OK] tempos_resposta so vendedor")

    test_tempos_resposta_vendedor_mensagens_consecutivas()
    print("  [OK] tempos_resposta vendedor mensagens consecutivas")

    test_contar_funil_basico()
    print("  [OK] contar_funil basico")

    test_contar_funil_sem_analise()
    print("  [OK] contar_funil sem analise")

    test_contar_funil_classificacao_frio()
    print("  [OK] contar_funil classificacao frio")

    test_score_medio_basico()
    print("  [OK] score_medio basico")

    test_score_medio_sem_analise()
    print("  [OK] score_medio sem analise")

    test_leads_sem_resposta()
    print("  [OK] leads_sem_resposta")

    test_leads_sem_resposta_so_vendedor()
    print("  [OK] leads_sem_resposta so vendedor")

    test_endpoint_calcular_metricas()
    print("  [OK] endpoint calcular metricas")

    test_endpoint_metricas_vendedor()
    print("  [OK] endpoint metricas vendedor")

    test_endpoint_metricas_dia()
    print("  [OK] endpoint metricas dia")

    test_endpoint_ranking()
    print("  [OK] endpoint ranking")

    test_endpoint_metricas_dia_inexistente()
    print("  [OK] endpoint metricas dia inexistente")

    print("\n" + "=" * 60)
    print("  TODOS OS TESTES PASSARAM!")
    print("=" * 60)
