"""Motor de analise de conversas usando OpenAI."""

import json
import logging
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from src.analysis.prompts import SYSTEM_PROMPT, TEMPLATE_ANALISE, formatar_transcricao
from src.config import settings
from src.database.connection import SessionLocal
from src.database.queries import buscar_prompt_ativo

logger = logging.getLogger(__name__)

CLASSIFICACOES_VALIDAS = {"frio", "mql", "sql", "cliente"}
SENTIMENTOS_VALIDOS = {"positivo", "neutro", "negativo"}


@dataclass
class ResultadoAnalise:
    score_qualidade: float
    classificacao: str
    erros: list[dict]
    sentimento_lead: str
    feedback_ia: str


def _validar_resultado(data: dict) -> ResultadoAnalise:
    """Valida e normaliza o JSON retornado pela IA, com fallbacks defensivos."""
    # Score
    score = data.get("score_qualidade", 5.0)
    try:
        score = float(score)
        score = max(0.0, min(10.0, score))
    except (TypeError, ValueError):
        score = 5.0

    # Classificacao
    classificacao = data.get("classificacao", "frio")
    if classificacao not in CLASSIFICACOES_VALIDAS:
        classificacao = "frio"

    # Erros
    erros_raw = data.get("erros", [])
    erros = []
    if isinstance(erros_raw, list):
        for e in erros_raw:
            if isinstance(e, dict) and "erro" in e:
                erros.append({
                    "erro": str(e["erro"]),
                    "detalhe": str(e.get("detalhe", "")),
                })

    # Sentimento
    sentimento = data.get("sentimento_lead", "neutro")
    if sentimento not in SENTIMENTOS_VALIDOS:
        sentimento = "neutro"

    # Feedback
    feedback = str(data.get("feedback_ia", "Analise nao disponivel."))

    return ResultadoAnalise(
        score_qualidade=round(score, 1),
        classificacao=classificacao,
        erros=erros,
        sentimento_lead=sentimento,
        feedback_ia=feedback,
    )


def _carregar_prompt_do_banco() -> str:
    """Busca prompt ativo no banco. Retorna SYSTEM_PROMPT hardcoded como fallback."""
    db = SessionLocal()
    try:
        config = buscar_prompt_ativo(db)
        if config:
            return config.conteudo
        return SYSTEM_PROMPT
    finally:
        db.close()


async def analisar_conversa(
    mensagens: list[dict], system_prompt: str | None = None
) -> ResultadoAnalise:
    """Envia a conversa para o GPT-4o-mini e retorna a analise estruturada.

    Args:
        mensagens: lista de dicts com 'remetente', 'conteudo', 'enviada_em'
        system_prompt: prompt customizado (se None, carrega do banco ou usa padrao)

    Raises:
        ValueError: se a conversa estiver vazia
        RuntimeError: se a chamada a OpenAI falhar
    """
    if not mensagens:
        raise ValueError("Conversa sem mensagens para analisar.")

    if system_prompt is None:
        system_prompt = _carregar_prompt_do_banco()

    transcricao = formatar_transcricao(mensagens)
    prompt_usuario = TEMPLATE_ANALISE.format(transcricao=transcricao)

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        resposta = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_usuario},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        conteudo = resposta.choices[0].message.content
        data = json.loads(conteudo)
        logger.info("Analise recebida da OpenAI com sucesso.")
        return _validar_resultado(data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON invalido da OpenAI: {e}")
        raise RuntimeError(f"Resposta da IA nao e JSON valido: {e}")
    except Exception as e:
        logger.error(f"Erro na chamada OpenAI: {e}")
        raise RuntimeError(f"Falha ao chamar OpenAI: {e}")
