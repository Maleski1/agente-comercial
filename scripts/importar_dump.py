"""
Script para importar dump SQL no PostgreSQL de produção.

Uso (dentro do container Easypanel):
    python -m scripts.importar_dump
"""

import os
import sys

from sqlalchemy import create_engine, text

DUMP_FILE = os.path.join(os.path.dirname(__file__), "..", "dump_dados.sql")


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Erro: DATABASE_URL não definida.")
        sys.exit(1)

    print(f"Conectando em: {database_url.split('@')[1] if '@' in database_url else database_url}")

    engine = create_engine(database_url)

    with open(DUMP_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Filtrar apenas INSERTs e SELECTs de setval (ignorar SET, comentários, etc.)
    statements = []
    for line in sql_content.split("\n"):
        line = line.strip()
        if line.startswith("INSERT INTO") or line.startswith("SELECT pg_catalog.setval"):
            statements.append(line)

    print(f"Encontrados {len(statements)} statements para executar.")

    with engine.begin() as conn:
        # Limpar tabelas na ordem reversa (respeitar FKs)
        tabelas = [
            "configuracoes", "configuracoes_prompt", "metricas_diarias",
            "analises", "mensagens", "conversas", "vendedores",
            "instancias_evolution", "empresas"
        ]
        for tabela in tabelas:
            try:
                conn.execute(text(f"DELETE FROM {tabela}"))
                print(f"  Limpou {tabela}")
            except Exception:
                pass

        # Executar inserts
        ok = 0
        erros = 0
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                ok += 1
            except Exception as e:
                print(f"  Erro: {e}")
                erros += 1

    # Resetar sequences
    print("\nAjustando sequences...")
    with engine.begin() as conn:
        for tabela in reversed(tabelas):
            try:
                result = conn.execute(text(f"SELECT MAX(id) FROM {tabela}")).scalar()
                if result:
                    conn.execute(text(f"SELECT setval('{tabela}_id_seq', {result})"))
                    print(f"  {tabela}_id_seq → {result}")
            except Exception:
                pass

    print(f"\nImportação concluída! {ok} inserts OK, {erros} erros.")


if __name__ == "__main__":
    main()
