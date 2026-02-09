"""Dashboard - Página 6: Admin — CRUD de empresas (protegido por senha)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import os  # noqa: E402
import streamlit as st  # noqa: E402

from src.dashboard.utils import get_db  # noqa: E402
from src.dashboard.theme import aplicar_tema, render_page_header, render_footer  # noqa: E402
from src.config import settings  # noqa: E402
from src.database.models import Empresa  # noqa: E402
from src.database.queries import (  # noqa: E402
    criar_empresa,
    listar_empresas,
    listar_instancias_empresa,
    listar_vendedores,
)

aplicar_tema()
render_page_header("Admin", "Gerenciamento de empresas")

# --- Autenticação por admin_key ---

admin_key = st.query_params.get("admin_key", "")
if not admin_key:
    admin_key = st.text_input("Senha Admin", type="password", key="admin_key_input")
    if st.button("Entrar", key="admin_login"):
        if admin_key == settings.admin_key:
            st.query_params["admin_key"] = admin_key
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()
elif admin_key != settings.admin_key:
    st.error("Chave admin inválida.")
    st.stop()

st.success("Acesso admin autorizado.")

# =============================================================================
# Listar Empresas
# =============================================================================
st.subheader("Empresas Cadastradas")

with get_db() as db:
    empresas = listar_empresas(db, apenas_ativas=False)
    empresas_data = []
    for e in empresas:
        vendedores = listar_vendedores(db, empresa_id=e.id, apenas_ativos=False)
        instancias = listar_instancias_empresa(db, e.id)
        empresas_data.append({
            "id": e.id,
            "nome": e.nome,
            "token": e.token,
            "ativa": e.ativa,
            "criada_em": str(e.criada_em),
            "vendedores": len(vendedores),
            "instancias": len(instancias),
        })

if not empresas_data:
    st.info("Nenhuma empresa cadastrada.")
else:
    for emp in empresas_data:
        status = "Ativa" if emp["ativa"] else "Inativa"
        with st.expander(f"{emp['nome']} ({status}) — {emp['vendedores']} vendedor(es)"):
            st.text(f"ID: {emp['id']}")
            st.text(f"Criada em: {emp['criada_em']}")
            st.text(f"Vendedores: {emp['vendedores']}")
            st.text(f"Instâncias Evolution: {emp['instancias']}")
            st.divider()
            st.text(f"Token: {emp['token']}")
            base_url = os.environ.get("DASHBOARD_URL", "http://localhost:8501")
            dashboard_url = f"{base_url}/?token={emp['token']}"
            st.code(dashboard_url, language=None)

            label_btn = "Desativar" if emp["ativa"] else "Ativar"
            if st.button(label_btn, key=f"toggle_{emp['id']}"):
                with get_db() as db:
                    db.query(Empresa).filter(Empresa.id == emp["id"]).update(
                        {"ativa": not emp["ativa"]}
                    )
                    db.commit()
                st.rerun()

# =============================================================================
# Criar Nova Empresa
# =============================================================================
st.divider()
st.subheader("Criar Nova Empresa")

novo_nome = st.text_input("Nome da empresa", key="nova_empresa_nome")

if st.button("Criar Empresa", type="primary", key="criar_empresa"):
    if not novo_nome.strip():
        st.error("Informe o nome da empresa.")
    else:
        with get_db() as db:
            empresa = criar_empresa(db, novo_nome.strip())
        st.success(f"Empresa '{empresa.nome}' criada!")
        st.text(f"Token: {empresa.token}")
        base_url = os.environ.get("DASHBOARD_URL", "http://localhost:8501")
        dashboard_url = f"{base_url}/?token={empresa.token}"
        st.code(dashboard_url, language=None)
        st.caption("Compartilhe este link com o dono da empresa.")

# =============================================================================
# Importar Dados (dump SQL) — temporário
# =============================================================================
dump_path = Path(__file__).resolve().parent.parent.parent.parent / "dump_dados.sql"
if dump_path.exists():
    st.divider()
    st.subheader("Importar Dados (dump)")
    st.caption("Importa dados do dump_dados.sql para o banco atual. Use apenas uma vez.")

    if st.button("Importar Dados", type="secondary", key="importar_dump"):
        from sqlalchemy import text
        from src.database.connection import engine

        with open(dump_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        statements = [
            line.strip()
            for line in sql_content.split("\n")
            if line.strip().startswith("INSERT INTO")
            or line.strip().startswith("SELECT pg_catalog.setval")
        ]

        tabelas = [
            "configuracoes", "configuracoes_prompt", "metricas_diarias",
            "analises", "mensagens", "conversas", "vendedores",
            "instancias_evolution", "empresas",
        ]

        with engine.begin() as conn:
            for tabela in tabelas:
                try:
                    conn.execute(text(f"DELETE FROM {tabela}"))
                except Exception:
                    pass

            ok, erros = 0, 0
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                    ok += 1
                except Exception:
                    erros += 1

        with engine.begin() as conn:
            for tabela in reversed(tabelas):
                try:
                    max_id = conn.execute(text(f"SELECT MAX(id) FROM {tabela}")).scalar()
                    if max_id:
                        conn.execute(text(f"SELECT setval('{tabela}_id_seq', {max_id})"))
                except Exception:
                    pass

        st.success(f"Importação concluída! {ok} inserts OK, {erros} erros.")
        st.rerun()

render_footer()
