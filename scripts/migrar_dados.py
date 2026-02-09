"""Migracao para multi-tenancy: cria empresa default e associa dados existentes.

SQLite nao suporta ALTER TABLE ADD COLUMN com FK constraint diretamente.
Estrategia: recriar tabelas via SQLAlchemy (criar_tabelas cria as que faltam)
e usar SQL direto para adicionar colunas nas tabelas existentes.

Uso:
    python -m scripts.migrar_dados
"""

import sqlite3
import sys
from pathlib import Path
from uuid import uuid4

# Fix path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings


def get_db_path() -> str:
    """Extrai caminho do arquivo SQLite da URL de conexao."""
    url = settings.database_url
    return url.replace("sqlite:///", "")


def migrar():
    """Executa a migracao para multi-tenancy."""
    db_path = get_db_path()
    print(f"Banco de dados: {db_path}")

    if not Path(db_path).exists():
        print("Banco nao existe. Nada para migrar — as tabelas serao criadas automaticamente.")
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    try:
        # 1. Criar tabela empresas (se nao existe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                token VARCHAR(36) UNIQUE NOT NULL,
                ativa BOOLEAN DEFAULT 1,
                criada_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Tabela 'empresas' criada/verificada.")

        # 2. Criar tabela instancias_evolution (se nao existe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instancias_evolution (
                id INTEGER PRIMARY KEY,
                empresa_id INTEGER NOT NULL REFERENCES empresas(id),
                nome_instancia VARCHAR(100) NOT NULL,
                telefone VARCHAR(20),
                ativa BOOLEAN DEFAULT 1,
                criada_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(empresa_id, nome_instancia)
            )
        """)
        print("[OK] Tabela 'instancias_evolution' criada/verificada.")

        # 3. Criar empresa default
        token = str(uuid4())
        cursor.execute("SELECT id FROM empresas LIMIT 1")
        empresa_existente = cursor.fetchone()

        if empresa_existente:
            empresa_id = empresa_existente[0]
            print(f"[OK] Empresa default ja existe (id={empresa_id}).")
        else:
            cursor.execute(
                "INSERT INTO empresas (nome, token) VALUES (?, ?)",
                ("Minha Empresa", token),
            )
            empresa_id = cursor.lastrowid
            print(f"[OK] Empresa default criada: id={empresa_id}, token={token}")

        # 4. Adicionar empresa_id nos vendedores
        _adicionar_coluna(cursor, "vendedores", "empresa_id", "INTEGER")
        cursor.execute(
            "UPDATE vendedores SET empresa_id = ? WHERE empresa_id IS NULL",
            (empresa_id,),
        )
        afetados = cursor.rowcount
        print(f"[OK] {afetados} vendedor(es) associado(s) a empresa default.")

        # 5. Adicionar empresa_id nas conversas
        _adicionar_coluna(cursor, "conversas", "empresa_id", "INTEGER")
        cursor.execute(
            "UPDATE conversas SET empresa_id = ? WHERE empresa_id IS NULL",
            (empresa_id,),
        )
        afetados = cursor.rowcount
        print(f"[OK] {afetados} conversa(s) associada(s) a empresa default.")

        # 6. Adicionar empresa_id nas configuracoes
        _adicionar_coluna(cursor, "configuracoes", "empresa_id", "INTEGER")
        # Configs existentes ficam como globais (empresa_id = NULL) — correto

        # 7. Adicionar empresa_id nas configuracoes_prompt
        _adicionar_coluna(cursor, "configuracoes_prompt", "empresa_id", "INTEGER")
        # Prompts existentes ficam como globais (empresa_id = NULL) — correto

        # 8. Criar instancia Evolution para empresa default (se configurada)
        from src.config import settings as s
        if s.evolution_instance_name:
            cursor.execute(
                "SELECT id FROM instancias_evolution WHERE nome_instancia = ?",
                (s.evolution_instance_name,),
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO instancias_evolution (empresa_id, nome_instancia) VALUES (?, ?)",
                    (empresa_id, s.evolution_instance_name),
                )
                print(f"[OK] Instancia Evolution '{s.evolution_instance_name}' criada.")
            else:
                print(f"[OK] Instancia Evolution '{s.evolution_instance_name}' ja existe.")

        conn.commit()
        print("\n=== Migracao concluida com sucesso! ===")

        # Mostrar token para acesso
        cursor.execute("SELECT token FROM empresas WHERE id = ?", (empresa_id,))
        token_final = cursor.fetchone()[0]
        print(f"\nToken de acesso ao dashboard: {token_final}")
        print(f"URL: http://localhost:8501/?token={token_final}")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERRO] Migracao falhou: {e}")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


def _adicionar_coluna(cursor, tabela: str, coluna: str, tipo: str):
    """Adiciona coluna se nao existir (SQLite nao tem IF NOT EXISTS para ALTER)."""
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [row[1] for row in cursor.fetchall()]
    if coluna not in colunas:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
        print(f"[OK] Coluna '{coluna}' adicionada em '{tabela}'.")
    else:
        print(f"[OK] Coluna '{coluna}' ja existe em '{tabela}'.")


if __name__ == "__main__":
    migrar()
