"""Operacoes de banco de dados (CRUD) — multi-tenant."""

import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session, joinedload

from src.database.models import (
    Analise,
    Configuracao,
    ConfiguracaoPrompt,
    Conversa,
    Empresa,
    InstanciaEvolution,
    Mensagem,
    MetricaDiaria,
    Vendedor,
)


# === Queries de Empresa ===


def buscar_empresa_por_token(db: Session, token: str) -> Empresa | None:
    return db.query(Empresa).filter(Empresa.token == token, Empresa.ativa.is_(True)).first()


def criar_empresa(db: Session, nome: str) -> Empresa:
    empresa = Empresa(nome=nome, token=str(uuid4()))
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


def listar_empresas(db: Session, apenas_ativas: bool = True) -> list[Empresa]:
    query = db.query(Empresa)
    if apenas_ativas:
        query = query.filter(Empresa.ativa.is_(True))
    return query.all()


# === Queries de InstanciaEvolution ===


def buscar_instancia_por_nome(db: Session, nome_instancia: str) -> InstanciaEvolution | None:
    return (
        db.query(InstanciaEvolution)
        .filter(InstanciaEvolution.nome_instancia == nome_instancia, InstanciaEvolution.ativa.is_(True))
        .first()
    )


def listar_instancias_empresa(db: Session, empresa_id: int) -> list[InstanciaEvolution]:
    return (
        db.query(InstanciaEvolution)
        .filter(InstanciaEvolution.empresa_id == empresa_id)
        .all()
    )


def criar_instancia_evolution(
    db: Session, empresa_id: int, nome_instancia: str, telefone: str | None = None
) -> InstanciaEvolution:
    instancia = InstanciaEvolution(
        empresa_id=empresa_id, nome_instancia=nome_instancia, telefone=telefone
    )
    db.add(instancia)
    db.commit()
    db.refresh(instancia)
    return instancia


def atualizar_instancia(
    db: Session, instancia_id: int, empresa_id: int,
    nome_instancia: str | None = None, telefone: str | None = None,
) -> InstanciaEvolution | None:
    """Atualiza dados de uma instancia Evolution."""
    instancia = (
        db.query(InstanciaEvolution)
        .filter(InstanciaEvolution.id == instancia_id, InstanciaEvolution.empresa_id == empresa_id)
        .first()
    )
    if not instancia:
        return None
    if nome_instancia is not None:
        instancia.nome_instancia = nome_instancia
    if telefone is not None:
        instancia.telefone = telefone
    db.commit()
    db.refresh(instancia)
    return instancia


def desativar_instancia(db: Session, instancia_id: int, empresa_id: int) -> InstanciaEvolution | None:
    """Desativa uma instancia Evolution (soft delete)."""
    instancia = (
        db.query(InstanciaEvolution)
        .filter(InstanciaEvolution.id == instancia_id, InstanciaEvolution.empresa_id == empresa_id)
        .first()
    )
    if not instancia:
        return None
    instancia.ativa = False
    db.commit()
    db.refresh(instancia)
    return instancia


# === Queries de Vendedor ===


def buscar_vendedor_por_telefone(
    db: Session, empresa_id: int, telefone: str
) -> Vendedor | None:
    return (
        db.query(Vendedor)
        .filter(
            Vendedor.empresa_id == empresa_id,
            Vendedor.telefone == telefone,
        )
        .first()
    )


def criar_vendedor(db: Session, nome: str, telefone: str, empresa_id: int | None = None) -> Vendedor:
    vendedor = Vendedor(nome=nome, telefone=telefone, empresa_id=empresa_id)
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return vendedor


def desativar_vendedor(db: Session, vendedor_id: int, empresa_id: int) -> Vendedor | None:
    """Desativa um vendedor (soft delete). Histórico de conversas e métricas permanece intacto."""
    vendedor = (
        db.query(Vendedor)
        .filter(Vendedor.id == vendedor_id, Vendedor.empresa_id == empresa_id)
        .first()
    )
    if not vendedor:
        return None
    vendedor.ativo = False
    db.commit()
    db.refresh(vendedor)
    return vendedor


def listar_vendedores(
    db: Session, empresa_id: int | None = None, apenas_ativos: bool = True
) -> list[Vendedor]:
    query = db.query(Vendedor)
    if empresa_id is not None:
        query = query.filter(Vendedor.empresa_id == empresa_id)
    if apenas_ativos:
        query = query.filter(Vendedor.ativo.is_(True))
    return query.all()


# === Queries de Conversa ===


def buscar_ou_criar_conversa(
    db: Session, vendedor_id: int, lead_telefone: str, lead_nome: str = "",
    empresa_id: int | None = None,
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
            empresa_id=empresa_id,
        )
        db.add(conversa)
        db.commit()
        db.refresh(conversa)
    elif lead_nome and not conversa.lead_nome:
        conversa.lead_nome = lead_nome
        db.commit()

    return conversa


def buscar_conversa_com_mensagens(db: Session, conversa_id: int) -> Conversa | None:
    """Busca conversa por ID, carregando mensagens em ordem cronologica."""
    return (
        db.query(Conversa)
        .options(joinedload(Conversa.mensagens))
        .filter(Conversa.id == conversa_id)
        .first()
    )


def buscar_conversas_do_dia(
    db: Session, data: str, vendedor_id: int | None = None,
    empresa_id: int | None = None,
) -> list[Conversa]:
    """Busca conversas com atividade (mensagens) num dia especifico.

    Args:
        data: formato YYYY-MM-DD
        vendedor_id: se informado, filtra por vendedor
        empresa_id: se informado, filtra por empresa
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
    if empresa_id is not None:
        query = query.filter(Conversa.empresa_id == empresa_id)

    return query.distinct().all()


def buscar_conversas_periodo(
    db: Session, data_inicio: str, data_fim: str,
    vendedor_id: int | None = None, empresa_id: int | None = None,
) -> list[Conversa]:
    """Busca conversas com atividade (mensagens) num período.

    Args:
        data_inicio: formato YYYY-MM-DD
        data_fim: formato YYYY-MM-DD
        vendedor_id: se informado, filtra por vendedor
        empresa_id: se informado, filtra por empresa
    """
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    query = (
        db.query(Conversa)
        .join(Mensagem)
        .filter(Mensagem.enviada_em >= inicio, Mensagem.enviada_em <= fim)
        .options(joinedload(Conversa.mensagens), joinedload(Conversa.analises))
    )
    if vendedor_id is not None:
        query = query.filter(Conversa.vendedor_id == vendedor_id)
    if empresa_id is not None:
        query = query.filter(Conversa.empresa_id == empresa_id)

    return query.distinct().all()


# === Queries de Mensagem ===


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


# === Queries de Analise ===


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


def buscar_metricas_dia(
    db: Session, data: str, empresa_id: int | None = None
) -> list[MetricaDiaria]:
    """Metricas de todos os vendedores num dia, opcionalmente filtrado por empresa."""
    query = db.query(MetricaDiaria).filter(MetricaDiaria.data == data)
    if empresa_id is not None:
        query = query.join(Vendedor).filter(Vendedor.empresa_id == empresa_id)
    return query.all()


# === Queries de Prompt Customizavel ===


def buscar_prompt_ativo(
    db: Session, empresa_id: int | None = None, nome: str = "prompt_analise"
) -> ConfiguracaoPrompt | None:
    """Busca o prompt ativo: empresa first, global fallback."""
    if empresa_id is not None:
        prompt = (
            db.query(ConfiguracaoPrompt)
            .filter(
                ConfiguracaoPrompt.empresa_id == empresa_id,
                ConfiguracaoPrompt.nome == nome,
                ConfiguracaoPrompt.ativo.is_(True),
            )
            .order_by(ConfiguracaoPrompt.atualizado_em.desc())
            .first()
        )
        if prompt:
            return prompt

    # Fallback: global (empresa_id IS NULL)
    return (
        db.query(ConfiguracaoPrompt)
        .filter(
            ConfiguracaoPrompt.empresa_id.is_(None),
            ConfiguracaoPrompt.nome == nome,
            ConfiguracaoPrompt.ativo.is_(True),
        )
        .order_by(ConfiguracaoPrompt.atualizado_em.desc())
        .first()
    )


def salvar_prompt(
    db: Session, conteudo: str, empresa_id: int | None = None, nome: str = "prompt_analise"
) -> ConfiguracaoPrompt:
    """Salva novo prompt e desativa os anteriores com mesmo nome (e mesma empresa)."""
    filtro = db.query(ConfiguracaoPrompt).filter(
        ConfiguracaoPrompt.nome == nome,
        ConfiguracaoPrompt.ativo.is_(True),
    )
    if empresa_id is not None:
        filtro = filtro.filter(ConfiguracaoPrompt.empresa_id == empresa_id)
    else:
        filtro = filtro.filter(ConfiguracaoPrompt.empresa_id.is_(None))

    filtro.update({"ativo": False})

    novo = ConfiguracaoPrompt(
        nome=nome,
        conteudo=conteudo,
        ativo=True,
        empresa_id=empresa_id,
        atualizado_em=datetime.now(),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


# === Queries de Configuracao (chave-valor) ===


def buscar_configuracao(
    db: Session, chave: str, empresa_id: int | None = None
) -> Configuracao | None:
    """Busca configuracao: empresa first, global fallback."""
    if empresa_id is not None:
        config = (
            db.query(Configuracao)
            .filter(Configuracao.empresa_id == empresa_id, Configuracao.chave == chave)
            .first()
        )
        if config:
            return config

    # Fallback: global
    return (
        db.query(Configuracao)
        .filter(Configuracao.empresa_id.is_(None), Configuracao.chave == chave)
        .first()
    )


def buscar_metricas_periodo(
    db: Session, data_inicio: str, data_fim: str, empresa_id: int | None = None
) -> list[MetricaDiaria]:
    """Metricas de todos os vendedores num periodo, ordenadas por data."""
    query = db.query(MetricaDiaria).filter(
        MetricaDiaria.data >= data_inicio,
        MetricaDiaria.data <= data_fim,
    )
    if empresa_id is not None:
        query = query.join(Vendedor).filter(Vendedor.empresa_id == empresa_id)
    return query.order_by(MetricaDiaria.data).all()


def buscar_analises_periodo(
    db: Session, data_inicio: str, data_fim: str, empresa_id: int | None = None
) -> list[Analise]:
    """Analises num periodo, com conversa carregada."""
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    query = (
        db.query(Analise)
        .join(Conversa)
        .filter(Analise.analisada_em >= inicio, Analise.analisada_em <= fim)
        .options(joinedload(Analise.conversa))
    )
    if empresa_id is not None:
        query = query.filter(Conversa.empresa_id == empresa_id)
    return query.all()


def buscar_mensagens_periodo(
    db: Session, data_inicio: str, data_fim: str, empresa_id: int | None = None
) -> list[Mensagem]:
    """Mensagens num periodo (para analise de horario)."""
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    query = (
        db.query(Mensagem)
        .join(Conversa)
        .filter(Mensagem.enviada_em >= inicio, Mensagem.enviada_em <= fim)
    )
    if empresa_id is not None:
        query = query.filter(Conversa.empresa_id == empresa_id)
    return query.all()


def salvar_configuracao(
    db: Session, chave: str, valor: str, empresa_id: int | None = None
) -> Configuracao:
    """Upsert: atualiza se (empresa_id, chave) ja existe, cria se nao."""
    if empresa_id is not None:
        config = (
            db.query(Configuracao)
            .filter(Configuracao.empresa_id == empresa_id, Configuracao.chave == chave)
            .first()
        )
    else:
        config = (
            db.query(Configuracao)
            .filter(Configuracao.empresa_id.is_(None), Configuracao.chave == chave)
            .first()
        )

    if config:
        config.valor = valor
        config.atualizado_em = datetime.now()
    else:
        config = Configuracao(chave=chave, valor=valor, empresa_id=empresa_id)
        db.add(config)
    db.commit()
    db.refresh(config)
    return config
