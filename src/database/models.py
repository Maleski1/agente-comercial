from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Vendedor(Base):
    __tablename__ = "vendedores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relacionamentos
    conversas: Mapped[list["Conversa"]] = relationship(back_populates="vendedor")
    metricas: Mapped[list["MetricaDiaria"]] = relationship(back_populates="vendedor")

    def __repr__(self):
        return f"<Vendedor {self.nome} ({self.telefone})>"


class Conversa(Base):
    __tablename__ = "conversas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendedor_id: Mapped[int] = mapped_column(ForeignKey("vendedores.id"), nullable=False)
    lead_telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    lead_nome: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="novo")
    iniciada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    atualizada_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relacionamentos
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
    nome: Mapped[str] = mapped_column(String(50), nullable=False)  # ex: "prompt_analise"
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ConfiguracaoPrompt nome={self.nome} ativo={self.ativo}>"


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
