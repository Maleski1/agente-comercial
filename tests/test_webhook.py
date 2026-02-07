"""Testa o fluxo completo: webhook -> parser -> banco."""

from fastapi.testclient import TestClient

from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Conversa, Mensagem, Vendedor
from src.main import app


def setup():
    """Cria tabelas e insere vendedor de teste."""
    criar_tabelas()
    db = SessionLocal()
    # Limpar dados anteriores
    db.query(Mensagem).delete()
    db.query(Conversa).delete()
    db.query(Vendedor).delete()
    # Inserir vendedor de teste
    vendedor = Vendedor(nome="Carlos Vendedor", telefone="5511988887777")
    db.add(vendedor)
    db.commit()
    db.close()


def test_webhook_mensagem_do_lead():
    """Simula um lead enviando mensagem para o vendedor."""
    setup()
    client = TestClient(app)

    # Payload real da Evolution API (lead enviando mensagem)
    payload = {
        "event": "messages.upsert",
        "instance": "agente-comercial",
        "data": {
            "key": {
                "remoteJid": "5511999998888@s.whatsapp.net",
                "fromMe": False,
                "id": "MSG001",
            },
            "pushName": "Maria Lead",
            "messageTimestamp": 1707300000,
            "message": {
                "conversation": "Oi, vi o anuncio de voces. Quanto custa o plano premium?"
            },
        },
    }

    response = client.post("/webhook/messages", json=payload)
    result = response.json()

    print(f"\nResposta: {result}")
    assert result["status"] == "salvo"
    assert result["conversa_id"] is not None
    assert result["mensagem_id"] is not None

    # Verificar no banco
    db = SessionLocal()
    conversa = db.query(Conversa).first()
    mensagem = db.query(Mensagem).first()

    print(f"Conversa: {conversa}")
    print(f"Mensagem: {mensagem}")
    print(f"Lead: {conversa.lead_nome} ({conversa.lead_telefone})")

    assert conversa.lead_telefone == "5511999998888"
    assert conversa.lead_nome == "Maria Lead"
    assert mensagem.remetente == "lead"
    assert "plano premium" in mensagem.conteudo

    db.close()
    print("\nTeste passou! Webhook funcionando corretamente.")


def test_webhook_resposta_do_vendedor():
    """Simula o vendedor respondendo ao lead."""
    client = TestClient(app)

    payload = {
        "event": "messages.upsert",
        "instance": "agente-comercial",
        "data": {
            "key": {
                "remoteJid": "5511999998888@s.whatsapp.net",
                "fromMe": True,
                "id": "MSG002",
            },
            "pushName": "",
            "messageTimestamp": 1707300060,
            "message": {
                "conversation": "Ola Maria! O plano premium custa R$ 199/mes. Posso te explicar os beneficios?"
            },
        },
    }

    response = client.post("/webhook/messages", json=payload)
    result = response.json()

    print(f"\nResposta: {result}")
    assert result["status"] == "salvo"

    # Verificar que a conversa tem 2 mensagens agora
    db = SessionLocal()
    conversa = db.query(Conversa).first()
    mensagens = db.query(Mensagem).filter_by(conversa_id=conversa.id).all()

    print(f"Total de mensagens na conversa: {len(mensagens)}")
    for m in mensagens:
        print(f"  [{m.remetente}] {m.conteudo[:60]}...")

    assert len(mensagens) == 2
    assert mensagens[1].remetente == "vendedor"

    db.close()
    print("\nTeste passou! Conversa com 2 mensagens.")


def test_webhook_evento_ignorado():
    """Testa que eventos nao relevantes sao ignorados."""
    client = TestClient(app)

    payload = {
        "event": "connection.update",
        "instance": "agente-comercial",
        "data": {"state": "open"},
    }

    response = client.post("/webhook/messages", json=payload)
    result = response.json()
    assert result["status"] == "ignorado"
    print("\nEvento ignorado corretamente.")


if __name__ == "__main__":
    print("=" * 60)
    print("  TESTES DO WEBHOOK - AGENTE COMERCIAL")
    print("=" * 60)

    test_webhook_mensagem_do_lead()
    test_webhook_resposta_do_vendedor()
    test_webhook_evento_ignorado()

    print("\n" + "=" * 60)
    print("  TODOS OS TESTES PASSARAM!")
    print("=" * 60)
