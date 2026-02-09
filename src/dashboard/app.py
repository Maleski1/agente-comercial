"""Dashboard Streamlit — Hub de navegação com st.navigation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Agente Comercial",
    page_icon=":material/monitoring:",
    layout="wide",
)

# --- Navegação com seções ---
pg = st.navigation(
    {
        "Dashboard": [
            st.Page("pages/1_Visao_Geral.py", title="Visão Geral", icon=":material/dashboard:", default=True),
            st.Page("pages/2_Vendedores.py", title="Vendedores", icon=":material/group:"),
            st.Page("pages/3_Ranking.py", title="Ranking", icon=":material/leaderboard:"),
            st.Page("pages/4_Conversas.py", title="Conversas", icon=":material/chat:"),
            st.Page("pages/7_Insights.py", title="Insights", icon=":material/insights:"),
        ],
        "Administração": [
            st.Page("pages/5_Configuracoes.py", title="Configurações", icon=":material/settings:"),
            st.Page("pages/6_Admin.py", title="Admin", icon=":material/admin_panel_settings:"),
        ],
    }
)

pg.run()
