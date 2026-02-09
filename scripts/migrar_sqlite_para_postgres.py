"""
Script de migração: SQLite → PostgreSQL

Uso:
    python -m scripts.migrar_sqlite_para_postgres \
        --sqlite sqlite:///data/agente_comercial.db \
        --postgres postgresql://agente:agente123@localhost:5432/agente_comercial

Este script lê todos os dados do SQLite existente e os insere no PostgreSQL,
respeitando a ordem de foreign keys.
"""

import argparse
import sys

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Importar todos os modelos para registrar no metadata
from src.database.connection import Base
import src.database.models as models  # noqa: F401


# Ordem de migração (respeita dependências de FK)
TABELAS_ORDEM = [
    models.Empresa,
    models.InstanciaEvolution,
    models.Vendedor,
    models.Conversa,
    models.Mensagem,
    models.Analise,
    models.MetricaDiaria,
    models.ConfiguracaoPrompt,
    models.Configuracao,
]


def migrar_tabela(modelo, session_sqlite, session_pg):
    """Migra todos os registros de uma tabela do SQLite para PostgreSQL."""
    registros = session_sqlite.query(modelo).all()
    colunas = [c.key for c in inspect(modelo).columns]
    for reg in registros:
        dados = {col: getattr(reg, col) for col in colunas}
        session_pg.merge(modelo(**dados))
    return len(registros)


def main():
    parser = argparse.ArgumentParser(description="Migrar dados de SQLite para PostgreSQL")
    parser.add_argument("--sqlite", required=True, help="URL de conexão SQLite")
    parser.add_argument("--postgres", required=True, help="URL de conexão PostgreSQL")
    args = parser.parse_args()

    print(f"Origem:  {args.sqlite}")
    print(f"Destino: {args.postgres}")

    # Conectar ao SQLite (origem)
    engine_sqlite = create_engine(args.sqlite)
    SessionSqlite = sessionmaker(bind=engine_sqlite)

    # Conectar ao PostgreSQL (destino)
    engine_pg = create_engine(args.postgres)
    SessionPg = sessionmaker(bind=engine_pg)

    # Criar tabelas no PostgreSQL (caso não existam)
    Base.metadata.create_all(bind=engine_pg)
    print("Tabelas criadas no PostgreSQL.\n")

    session_sqlite = SessionSqlite()
    session_pg = SessionPg()

    try:
        total_geral = 0
        for modelo in TABELAS_ORDEM:
            nome = modelo.__tablename__
            count = migrar_tabela(modelo, session_sqlite, session_pg)
            if count is None:
                count = 0
            print(f"  {nome}: {count} registros migrados")
            total_geral += count

        session_pg.commit()

        # Resetar sequences do PostgreSQL para evitar conflito de IDs
        print("\nAjustando sequences...")
        for modelo in TABELAS_ORDEM:
            nome = modelo.__tablename__
            max_id = session_pg.execute(text(f"SELECT MAX(id) FROM {nome}")).scalar()
            if max_id:
                session_pg.execute(text(f"SELECT setval('{nome}_id_seq', {max_id})"))
                print(f"  {nome}_id_seq → {max_id}")
        session_pg.commit()

        print(f"\nMigração concluída! Total: {total_geral} registros.")

    except Exception as e:
        session_pg.rollback()
        print(f"\nErro na migração: {e}")
        sys.exit(1)

    finally:
        session_sqlite.close()
        session_pg.close()


if __name__ == "__main__":
    main()
