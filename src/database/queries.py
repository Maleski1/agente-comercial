"""Operacoes de banco de dados (CRUD)."""

import json
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from src.database.models import (
    Analise,
    ConfiguracaoPrompt,
    Conversa,
    Mensagem,
    MetricaDiaria,
    Vendedor,
)


def buscar_vendedor_por_telefone(db: Session, telefone: str) -> Vendedor | None:
    return db.query(Vendedor).filter(Vendedor.telefone == telefone).first()


def criar_vendedor(db: Session, nome: str, telefone: str) -> Vendedor:
    vendedor = Vendedor(nome=nome, telefone=telefone)
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return vendedor


def buscar_ou_criar_conversa(
    db: Session, vendedor_id: int, lead_telefone: str, lead_nome: str = ""
) -> Conversa:
    """Busca conversa ativa entre vendedor e lead ou cria uma nova."""
    conversa = (
        db.query(Conversa)
        .filter(
            Conversa.vendedor_id == vendedor_id,
            Conversa.lead_telefone == lead_telefone,
        )
        .first()
    )

    if not conversa:
        conversa = Conversa(
            vendedor_id=vendedor_id,
            lead_telefone=lead_telefone,
            lead_nome=lead_nome or None,
        )
        db.add(conversa)
        db.commit()
        db.refresh(conversa)
    elif lead_nome and not conversa.lead_nome:
        conversa.lead_nome = lead_nome
        db.commit()

    return conversa


def salvar_mensagem(
    db: Session,
    conversa_id: int,
    remetente: str,
    conteudo: str,
    tipo: str = "texto",
    enviada_em: datetime | None = None,
) -> Mensagem:
    mensagem = Mensagem(
        conversa_id=conversa_id,
        remetente=remetente,
        conteudo=conteudo,
        tipo=tipo,
        enviada_em=enviada_em or datetime.now(),
    )
    db.add(mensagem)

    # Atualizar timestamp da conversa
    conversa = db.query(Conversa).get(conversa_id)
    if conversa:
        conversa.atualizada_em = datetime.now()

    db.commit()
    db.refresh(mensagem)
    return mensagem


def listar_vendedores(db: Session, apenas_ativos: bool = True) -> list[Vendedor]:
    query = db.query(Vendedor)
    if apenas_ativos:
        query = query.filter(Vendedor.ativo.is_(True))
    return query.all()


def buscar_conversa_com_mensagens(db: Session, conversa_id: int) -> Conversa | None:
    """Busca conversa por ID, carregando mensagens em ordem cronologica."""
    return (
        db.query(Conversa)
        .options(joinedload(Conversa.mensagens))
        .filter(Conversa.id == conversa_id)
        .first()
    )


def salvar_analise(
    db: Session,
    conversa_id: int,
    score_qualidade: float,
    classificacao: str,
    erros: list[dict],
    sentimento_lead: str,
    feedback_ia: str,
) -> Analise:
    """Salva resultado de analise no banco."""
    analise = Analise(
        conversa_id=conversa_id,
        score_qualidade=score_qualidade,
        classificacao=classificacao,
        erros=json.dumps(erros, ensure_ascii=False),
        sentimento_lead=sentimento_lead,
        feedback_ia=feedback_ia,
    )
    db.add(analise)
    db.commit()
    db.refresh(analise)
    return analise


def buscar_analises_por_conversa(db: Session, conversa_id: int) -> list[Analise]:
    """Busca todas as analises de uma conversa, mais recente primeiro."""
    return (
        db.query(Analise)
        .filter(Analise.conversa_id == conversa_id)
        .order_by(Analise.analisada_em.desc())
        .all()
    )


# === Queries de Metricas ===


def buscar_conversas_do_dia(
    db: Session, data: str, vendedor_id: int | None = None
) -> list[Conversa]:
    """Busca conversas com atividade (mensagens) num dia especifico.

    Args:
        data: formato YYYY-MM-DD
        vendedor_id: se informado, filtra por vendedor
    """
    inicio = datetime.strptime(data, "%Y-%m-%d")
    fim = datetime.strptime(data, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    query = (
        db.query(Conversa)
        .join(Mensagem)
        .filter(Mensagem.enviada_em >= inicio, Mensagem.enviada_em <= fim)
        .options(joinedload(Conversa.mensagens), joinedload(Conversa.analises))
    )
    if vendedor_id is not None:
        query = query.filter(Conversa.vendedor_id == vendedor_id)

    return query.distinct().all()


def upsert_metrica_diaria(
    db: Session, vendedor_id: int, data: str, **valores
) -> MetricaDiaria:
    """Cria ou atualiza MetricaDiaria para (vendedor_id, data). Idempotente."""
    metrica = (
        db.query(MetricaDiaria)
        .filter(MetricaDiaria.vendedor_id == vendedor_id, MetricaDiaria.data == data)
        .first()
    )
    if metrica:
        for campo, valor in valores.items():
            setattr(metrica, campo, valor)
    else:
        metrica = MetricaDiaria(vendedor_id=vendedor_id, data=data, **valores)
        db.add(metrica)

    db.commit()
    db.refresh(metrica)
    return metrica


def buscar_metricas_vendedor(
    db: Session, vendedor_id: int, limit: int = 30
) -> list[MetricaDiaria]:
    """Historico de metricas de um vendedor, mais recente primeiro."""
    return (
        db.query(MetricaDiaria)
        .filter(MetricaDiaria.vendedor_id == vendedor_id)
        .order_by(MetricaDiaria.data.desc())
        .limit(limit)
        .all()
    )


def buscar_metricas_dia(db: Session, data: str) -> list[MetricaDiaria]:
    """Metricas de todos os vendedores num dia."""
    return (
        db.query(MetricaDiaria)
        .filter(MetricaDiaria.data == data)
        .all()
    )


# === Queries de Prompt Customizavel ===


def buscar_prompt_ativo(db: Session, nome: str = "prompt_analise") -> ConfiguracaoPrompt | None:
    """Busca o prompt ativo pelo nome. Retorna None se nenhum configurado."""
    return (
        db.query(ConfiguracaoPrompt)
        .filter(ConfiguracaoPrompt.nome == nome, ConfiguracaoPrompt.ativo.is_(True))
        .order_by(ConfiguracaoPrompt.atualizado_em.desc())
        .first()
    )


def salvar_prompt(db: Session, conteudo: str, nome: str = "prompt_analise") -> ConfiguracaoPrompt:
    """Salva novo prompt e desativa os anteriores com mesmo nome."""
    # Desativar prompts anteriores
    db.query(ConfiguracaoPrompt).filter(
        ConfiguracaoPrompt.nome == nome,
        ConfiguracaoPrompt.ativo.is_(True),
    ).update({"ativo": False})

    # Criar novo prompt ativo
    novo = ConfiguracaoPrompt(
        nome=nome,
        conteudo=conteudo,
        ativo=True,
        atualizado_em=datetime.now(),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
