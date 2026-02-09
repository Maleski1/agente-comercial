"""Dashboard - Página 6: Admin — CRUD de empresas (protegido por senha)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

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
            dashboard_url = f"http://localhost:8501/?token={emp['token']}"
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
        dashboard_url = f"http://localhost:8501/?token={empresa.token}"
        st.code(dashboard_url, language=None)
        st.caption("Compartilhe este link com o dono da empresa.")

render_footer()
