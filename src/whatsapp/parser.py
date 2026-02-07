"""Parser para mensagens recebidas da Evolution API v2."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MensagemParseada:
    """Resultado do parse de uma mensagem do webhook."""

    telefone_remetente: str  # numero de quem enviou
    telefone_destinatario: str  # numero de quem recebeu
    nome_contato: str  # pushName do remetente
    conteudo: str  # texto da mensagem
    tipo: str  # texto, audio, imagem, etc
    enviada_por_mim: bool  # True = vendedor enviou, False = lead enviou
    timestamp: datetime
    message_id: str
    instance_name: str
    instance_phone: str  # telefone do dono da instancia


def parsear_webhook(payload: dict) -> MensagemParseada | None:
    """
    Transforma o payload do webhook da Evolution API em um objeto estruturado.
    Retorna None se a mensagem nao for processavel (ex: notificacao de status).
    """
    evento = payload.get("event", "")

    if evento != "messages.upsert":
        return None

    data = payload.get("data", {})
    key = data.get("key", {})
    message = data.get("message", {})

    # Extrair numero remoto (sem @s.whatsapp.net)
    remote_jid = key.get("remoteJid", "")
    if not remote_jid or "@g.us" in remote_jid:
        # Ignorar mensagens de grupo
        return None

    telefone_remoto = remote_jid.replace("@s.whatsapp.net", "")
    enviada_por_mim = key.get("fromMe", False)

    # Extrair conteudo da mensagem
    conteudo, tipo = _extrair_conteudo(message)
    if not conteudo:
        return None

    # Timestamp
    ts = data.get("messageTimestamp")
    if ts:
        timestamp = datetime.fromtimestamp(int(ts))
    else:
        timestamp = datetime.now()

    # Se fromMe=True, o vendedor enviou (remetente = instancia, destinatario = remoto)
    # Se fromMe=False, o lead enviou (remetente = remoto, destinatario = instancia)
    instance_name = payload.get("instance", "")

    # Extrair telefone do dono da instancia (campo sender do payload)
    sender = payload.get("sender", "")
    instance_phone = sender.replace("@s.whatsapp.net", "") if sender else ""

    return MensagemParseada(
        telefone_remetente=telefone_remoto if not enviada_por_mim else "",
        telefone_destinatario=telefone_remoto if enviada_por_mim else "",
        nome_contato=data.get("pushName", ""),
        conteudo=conteudo,
        tipo=tipo,
        enviada_por_mim=enviada_por_mim,
        timestamp=timestamp,
        message_id=key.get("id", ""),
        instance_name=instance_name,
        instance_phone=instance_phone,
    )


def _extrair_conteudo(message: dict) -> tuple[str, str]:
    """Extrai texto e tipo da mensagem. Retorna (conteudo, tipo)."""
    # Texto simples
    if "conversation" in message:
        return message["conversation"], "texto"

    # Texto com citacao/resposta
    if "extendedTextMessage" in message:
        return message["extendedTextMessage"].get("text", ""), "texto"

    # Imagem com legenda
    if "imageMessage" in message:
        caption = message["imageMessage"].get("caption", "[imagem]")
        return caption, "imagem"

    # Audio
    if "audioMessage" in message:
        return "[audio]", "audio"

    # Video
    if "videoMessage" in message:
        caption = message["videoMessage"].get("caption", "[video]")
        return caption, "video"

    # Documento
    if "documentMessage" in message:
        filename = message["documentMessage"].get("fileName", "[documento]")
        return filename, "documento"

    return "", "desconhecido"
