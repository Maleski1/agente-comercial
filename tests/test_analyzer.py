"""Testes do modulo de analise com mock da OpenAI."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.analysis.analyzer import ResultadoAnalise, _validar_resultado, analisar_conversa
from src.analysis.prompts import formatar_transcricao


# === Testes do formatar_transcricao ===

def test_formatar_transcricao_basico():
    mensagens = [
        {"remetente": "lead", "conteudo": "Oi, quero saber do preco", "enviada_em": "2024-02-07 10:00"},
        {"remetente": "vendedor", "conteudo": "Ola! Custa R$ 199/mes", "enviada_em": "2024-02-07 10:01"},
    ]
    resultado = formatar_transcricao(mensagens)
    assert "LEAD: Oi, quero saber do preco" in resultado
    assert "VENDEDOR: Ola! Custa R$ 199/mes" in resultado


def test_formatar_transcricao_vazio():
    assert formatar_transcricao([]) == ""


# === Testes do _validar_resultado ===

def test_validar_resultado_completo():
    data = {
        "score_qualidade": 7.5,
        "classificacao": "sql",
        "erros": [{"erro": "Sem urgencia", "detalhe": "Nao criou pressao"}],
        "sentimento_lead": "positivo",
        "feedback_ia": "Bom atendimento geral.",
    }
    r = _validar_resultado(data)
    assert r.score_qualidade == 7.5
    assert r.classificacao == "sql"
    assert len(r.erros) == 1
    assert r.sentimento_lead == "positivo"


def test_validar_resultado_score_fora_do_range():
    r = _validar_resultado({"score_qualidade": 15.0})
    assert r.score_qualidade == 10.0

    r = _validar_resultado({"score_qualidade": -3.0})
    assert r.score_qualidade == 0.0


def test_validar_resultado_score_invalido():
    r = _validar_resultado({"score_qualidade": "abc"})
    assert r.score_qualidade == 5.0


def test_validar_resultado_classificacao_invalida():
    r = _validar_resultado({"classificacao": "desconhecido"})
    assert r.classificacao == "frio"


def test_validar_resultado_sentimento_invalido():
    r = _validar_resultado({"sentimento_lead": "furioso"})
    assert r.sentimento_lead == "neutro"


def test_validar_resultado_erros_formato_invalido():
    # Erros sem campo 'erro' devem ser ignorados
    r = _validar_resultado({"erros": [{"descricao": "algo"}]})
    assert r.erros == []

    # Erros como string devem ser ignorados
    r = _validar_resultado({"erros": "nenhum"})
    assert r.erros == []


def test_validar_resultado_campos_ausentes():
    """JSON vazio deve retornar todos os fallbacks."""
    r = _validar_resultado({})
    assert r.score_qualidade == 5.0
    assert r.classificacao == "frio"
    assert r.erros == []
    assert r.sentimento_lead == "neutro"
    assert r.feedback_ia == "Analise nao disponivel."


# === Testes do analisar_conversa (com mock) ===

RESPOSTA_MOCK = {
    "score_qualidade": 8.0,
    "classificacao": "mql",
    "erros": [{"erro": "Sem proximo passo", "detalhe": "Nao agendou reuniao"}],
    "sentimento_lead": "positivo",
    "feedback_ia": "Vendedor atencioso, respondeu rapido. Faltou definir proxima acao.",
}

MENSAGENS_TESTE = [
    {"remetente": "lead", "conteudo": "Oi, vi o anuncio de voces", "enviada_em": "2024-02-07 10:00"},
    {"remetente": "vendedor", "conteudo": "Ola! Que bom! Como posso ajudar?", "enviada_em": "2024-02-07 10:01"},
    {"remetente": "lead", "conteudo": "Quero saber sobre o plano premium", "enviada_em": "2024-02-07 10:02"},
    {"remetente": "vendedor", "conteudo": "O plano premium custa R$ 199/mes com tudo incluso!", "enviada_em": "2024-02-07 10:03"},
]


@pytest.mark.asyncio
async def test_analisar_conversa_sucesso():
    """Testa fluxo completo com mock da OpenAI."""
    mock_message = MagicMock()
    mock_message.content = json.dumps(RESPOSTA_MOCK)

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("src.analysis.analyzer.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create = AsyncMock(return_value=mock_response)

        resultado = await analisar_conversa(MENSAGENS_TESTE)

    assert isinstance(resultado, ResultadoAnalise)
    assert resultado.score_qualidade == 8.0
    assert resultado.classificacao == "mql"
    assert resultado.sentimento_lead == "positivo"
    assert len(resultado.erros) == 1
    assert resultado.erros[0]["erro"] == "Sem proximo passo"


@pytest.mark.asyncio
async def test_analisar_conversa_vazia():
    """Conversa vazia deve lancar ValueError."""
    with pytest.raises(ValueError, match="sem mensagens"):
        await analisar_conversa([])


@pytest.mark.asyncio
async def test_analisar_conversa_erro_openai():
    """Erro na API deve lancar RuntimeError."""
    with patch("src.analysis.analyzer.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create = AsyncMock(
            side_effect=Exception("API timeout")
        )

        with pytest.raises(RuntimeError, match="Falha ao chamar OpenAI"):
            await analisar_conversa(MENSAGENS_TESTE)


# === Testes do endpoint (integracao com mock) ===

from fastapi.testclient import TestClient
from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Analise, Conversa, Mensagem, Vendedor
from src.main import app


def _setup_conversa_teste():
    """Cria vendedor + conversa + mensagens para testes de endpoint."""
    criar_tabelas()
    db = SessionLocal()
    db.query(Analise).delete()
    db.query(Mensagem).delete()
    db.query(Conversa).delete()
    db.query(Vendedor).delete()

    vendedor = Vendedor(nome="Teste Vendedor", telefone="5511900000000")
    db.add(vendedor)
    db.flush()

    conversa = Conversa(
        vendedor_id=vendedor.id,
        lead_telefone="5511911111111",
        lead_nome="Lead Teste",
    )
    db.add(conversa)
    db.flush()

    for i, (rem, txt) in enumerate([
        ("lead", "Oi, quero saber do produto"),
        ("vendedor", "Ola! Claro, posso te ajudar. Qual produto te interessou?"),
        ("lead", "O plano anual. Quanto custa?"),
        ("vendedor", "O plano anual sai por R$ 1.990. Posso te enviar uma proposta?"),
    ]):
        db.add(Mensagem(conversa_id=conversa.id, remetente=rem, conteudo=txt))

    db.commit()
    conversa_id = conversa.id
    db.close()
    return conversa_id


def test_endpoint_analisar_sucesso():
    """POST /analisar/{id} retorna analise com mock."""
    conversa_id = _setup_conversa_teste()
    client = TestClient(app)

    mock_message = MagicMock()
    mock_message.content = json.dumps(RESPOSTA_MOCK)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("src.analysis.analyzer.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create = AsyncMock(return_value=mock_response)

        response = client.post(f"/analisar/{conversa_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["score_qualidade"] == 8.0
    assert data["classificacao"] == "mql"
    assert data["analise_id"] is not None


def test_endpoint_analisar_conversa_inexistente():
    """POST /analisar/999 retorna 404."""
    client = TestClient(app)
    response = client.post("/analisar/999")
    assert response.status_code == 404


def test_endpoint_listar_analises():
    """GET /analises/{id} retorna analises salvas."""
    conversa_id = _setup_conversa_teste()
    client = TestClient(app)

    # Primeiro, criar uma analise via mock
    mock_message = MagicMock()
    mock_message.content = json.dumps(RESPOSTA_MOCK)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("src.analysis.analyzer.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create = AsyncMock(return_value=mock_response)
        client.post(f"/analisar/{conversa_id}")

    # Agora buscar
    response = client.get(f"/analises/{conversa_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["score_qualidade"] == 8.0


if __name__ == "__main__":
    print("=" * 60)
    print("  TESTES DO ANALYZER - AGENTE COMERCIAL")
    print("=" * 60)

    # Testes sincronos
    test_formatar_transcricao_basico()
    print("  [OK] formatar_transcricao basico")

    test_formatar_transcricao_vazio()
    print("  [OK] formatar_transcricao vazio")

    test_validar_resultado_completo()
    print("  [OK] validar_resultado completo")

    test_validar_resultado_score_fora_do_range()
    print("  [OK] validar_resultado score fora do range")

    test_validar_resultado_score_invalido()
    print("  [OK] validar_resultado score invalido")

    test_validar_resultado_classificacao_invalida()
    print("  [OK] validar_resultado classificacao invalida")

    test_validar_resultado_sentimento_invalido()
    print("  [OK] validar_resultado sentimento invalido")

    test_validar_resultado_erros_formato_invalido()
    print("  [OK] validar_resultado erros formato invalido")

    test_validar_resultado_campos_ausentes()
    print("  [OK] validar_resultado campos ausentes")

    # Testes de endpoint
    test_endpoint_analisar_sucesso()
    print("  [OK] endpoint analisar sucesso")

    test_endpoint_analisar_conversa_inexistente()
    print("  [OK] endpoint analisar conversa inexistente")

    test_endpoint_listar_analises()
    print("  [OK] endpoint listar analises")

    print("\n" + "=" * 60)
    print("  TODOS OS TESTES SINCRONOS PASSARAM!")
    print("  (Para testes async, rode: pytest tests/test_analyzer.py)")
    print("=" * 60)
