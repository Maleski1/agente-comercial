from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    token: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationships
    vendedores: Mapped[list["Vendedor"]] = relationship(back_populates="empresa")
    instancias_evolution: Mapped[list["InstanciaEvolution"]] = relationship(back_populates="empresa")
    configuracoes: Mapped[list["Configuracao"]] = relationship(back_populates="empresa")
    configuracoes_prompt: Mapped[list["ConfiguracaoPrompt"]] = relationship(back_populates="empresa")
    conversas: Mapped[list["Conversa"]] = relationship(back_populates="empresa")

    def __repr__(self):
        return f"<Empresa {self.nome} token={self.token[:8]}...>"


class InstanciaEvolution(Base):
    __tablename__ = "instancias_evolution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=False)
    nome_instancia: Mapped[str] = mapped_column(String(100), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint("empresa_id", "nome_instancia"),)

    # Relationships
    empresa: Mapped["Empresa"] = relationship(back_populates="instancias_evolution")

    def __repr__(self):
        return f"<InstanciaEvolution {self.nome_instancia} empresa={self.empresa_id}>"


class Vendedor(Base):
    __tablename__ = "vendedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id"))
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint("empresa_id", "telefone"),)

    # Relacionamentos
    empresa: Mapped["Empresa | None"] = relationship(back_populates="vendedores")
    conversas: Mapped[list["Conversa"]] = relationship(back_populates="vendedor")
    metricas: Mapped[list["MetricaDiaria"]] = relationship(back_populates="vendedor")

    def __repr__(self):
        return f"<Vendedor {self.nome} ({self.telefone})>"


class Conversa(Base):
    __tablename__ = "conversas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id"))
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"), nullable=False)
    lead_telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    lead_nome: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="novo")
    iniciada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    atualizada_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relacionamentos
    empresa: Mapped["Empresa | None"] = relationship(back_populates="conversas")
    vendedor: Mapped["Vendedor"] = relationship(back_populates="conversas")
    mensagens: Mapped[list["Mensagem"]] = relationship(
        back_populates="conversa", order_by="Mensagem.enviada_em"
    )
    analises: Mapped[list["Analise"]] = relationship(back_populates="conversa")

    def __repr__(self):
        return f"<Conversa vendedor={self.vendedor_id} lead={self.lead_telefone} status={self.status}>"


class Mensagem(Base):
    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversa_id: Mapped[int] = mapped_column(ForeignKey("conversas.id"), nullable=False)
    remetente: Mapped[str] = mapped_column(String(10), nullable=False)  # "vendedor" ou "lead"
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), default="texto")  # texto/audio/imagem
    enviada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relacionamento
    conversa: Mapped["Conversa"] = relationship(back_populates="mensagens")

    def __repr__(self):
        preview = self.conteudo[:50] if self.conteudo else ""
        return f"<Mensagem de={self.remetente} '{preview}...'>"


class Analise(Base):
    __tablename__ = "analises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversa_id: Mapped[int] = mapped_column(ForeignKey("conversas.id"), nullable=False)
    score_qualidade: Mapped[float | None] = mapped_column(Float)
    classificacao: Mapped[str | None] = mapped_column(String(20))
    erros: Mapped[str | None] = mapped_column(Text)
    sentimento_lead: Mapped[str | None] = mapped_column(String(20))
    feedback_ia: Mapped[str | None] = mapped_column(Text)
    analisada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    conversa: Mapped["Conversa"] = relationship(back_populates="analises")

    def __repr__(self):
        return f"<Analise conversa={self.conversa_id} score={self.score_qualidade}>"


class ConfiguracaoPrompt(Base):
    __tablename__ = "configuracoes_prompt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id"))
    nome: Mapped[str] = mapped_column(String(50), nullable=False)  # ex: "prompt_analise"
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relacionamento
    empresa: Mapped["Empresa | None"] = relationship(back_populates="configuracoes_prompt")

    def __repr__(self):
        return f"<ConfiguracaoPrompt nome={self.nome} ativo={self.ativo}>"


class Configuracao(Base):
    __tablename__ = "configuracoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("empresas.id"))
    chave: Mapped[str] = mapped_column(String(100), nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint("empresa_id", "chave"),)

    # Relacionamento
    empresa: Mapped["Empresa | None"] = relationship(back_populates="configuracoes")

    def __repr__(self):
        return f"<Configuracao {self.chave}>"


class MetricaDiaria(Base):
    __tablename__ = "metricas_diarias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"), nullable=False)
    data: Mapped[str] = mapped_column(String(10), nullable=False)  # formato: YYYY-MM-DD
    total_atendimentos: Mapped[int] = mapped_column(Integer, default=0)
    tempo_medio_resposta_seg: Mapped[int | None] = mapped_column(Integer)
    tempo_primeira_resp_seg: Mapped[int | None] = mapped_column(Integer)
    total_mql: Mapped[int] = mapped_column(Integer, default=0)
    total_sql: Mapped[int] = mapped_column(Integer, default=0)
    total_conversoes: Mapped[int] = mapped_column(Integer, default=0)
    score_medio: Mapped[float | None] = mapped_column(Float)
    leads_sem_resposta: Mapped[int] = mapped_column(Integer, default=0)

    # Relacionamento
    vendedor: Mapped["Vendedor"] = relationship(back_populates="metricas")

    def __repr__(self):
        return f"<Metrica vendedor={self.vendedor_id} data={self.data}>"
