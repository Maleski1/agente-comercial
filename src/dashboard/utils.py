"""Utilitarios compartilhados do dashboard: sessao DB, cores, helpers, auth."""

import sys
from contextlib import contextmanager
from pathlib import Path

import streamlit as st

# Fix sys.path para imports "from src.xxx" funcionarem
# quando Streamlit roda como processo separado (streamlit run src/dashboard/app.py)
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.database.connection import SessionLocal, criar_tabelas  # noqa: E402
from src.database.queries import buscar_empresa_por_token  # noqa: E402

# Garantir que todas as tabelas existem
criar_tabelas()


@contextmanager
def get_db():
    """Context manager para sessao do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validar_token_empresa():
    """Valida token na URL e seta empresa no session_state. Bloqueia se invalido.

    Returns:
        tuple (empresa_id, empresa_nome)
    """
    # Ja validado nesta sessao?
    if "empresa_id" in st.session_state and st.session_state["empresa_id"]:
        return st.session_state["empresa_id"], st.session_state["empresa_nome"]

    token = st.query_params.get("token")
    if not token:
        st.error("Acesso negado. Use o link fornecido pela empresa.")
        st.stop()

    with get_db() as db:
        empresa = buscar_empresa_por_token(db, token)

    if not empresa:
        st.error("Token invalido ou empresa desativada.")
        st.stop()

    st.session_state["empresa_id"] = empresa.id
    st.session_state["empresa_nome"] = empresa.nome
    st.session_state["empresa_token"] = token
    return empresa.id, empresa.nome


# Re-exportar paleta e helpers do theme.py (backward compatibility)
from src.dashboard.theme import CORES, COR_CLASSIFICACAO, COR_SENTIMENTO, score_cor  # noqa: F401
