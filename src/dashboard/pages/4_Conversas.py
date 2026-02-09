"""Dashboard - Página 4: Drill-down de Conversas — multi-tenant."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import json  # noqa: E402

import streamlit as st  # noqa: E402
from datetime import date, timedelta  # noqa: E402

from src.dashboard.utils import get_db, validar_token_empresa  # noqa: E402
from src.dashboard.theme import (  # noqa: E402
    aplicar_tema,
    render_sidebar,
    render_page_header,
    render_footer,
    render_alerta,
    render_badge,
    score_cor,
    COR_CLASSIFICACAO,
    COR_SENTIMENTO,
    CORES,
)
from src.database.queries import buscar_conversas_periodo, listar_vendedores

# --- Tema e autenticação ---
aplicar_tema()
empresa_id, empresa_nome = validar_token_empresa()
render_sidebar(empresa_nome)
render_page_header("Conversas", "Drill-down por conversa com análise IA")

# --- Carregar vendedores da empresa ---
with get_db() as db:
    vendedores_raw = listar_vendedores(db, empresa_id=empresa_id)
    vendedores = {v.id: v.nome for v in vendedores_raw}

# --- Filtros ---
col1, col2 = st.columns(2)
with col1:
    date_range = st.date_input(
        "Período",
        value=(date.today() - timedelta(days=6), date.today()),
    )
with col2:
    opcoes_vendedor = ["Todos"] + list(vendedores.values())
    vendedor_filtro = st.selectbox("Vendedor", opcoes_vendedor)

if not isinstance(date_range, tuple) or len(date_range) != 2:
    st.info("Selecione a data final do período.")
    st.stop()

data_inicio, data_fim = date_range
str_inicio = data_inicio.strftime("%Y-%m-%d")
str_fim = data_fim.strftime("%Y-%m-%d")

vendedor_id = None
if vendedor_filtro != "Todos":
    vendedor_id = [k for k, v in vendedores.items() if v == vendedor_filtro][0]

# --- Carregar conversas (filtrado por empresa) ---
with get_db() as db:
    conversas_raw = buscar_conversas_periodo(db, str_inicio, str_fim, vendedor_id, empresa_id=empresa_id)

    conversas = []
    for c in conversas_raw:
        analise_mais_recente = None
        if c.analises:
            a = max(c.analises, key=lambda x: x.analisada_em)
            erros = []
            if a.erros:
                try:
                    erros = json.loads(a.erros)
                except (json.JSONDecodeError, TypeError):
                    erros = []
            analise_mais_recente = {
                "score": a.score_qualidade,
                "classificacao": a.classificacao,
                "sentimento": a.sentimento_lead,
                "feedback": a.feedback_ia,
                "erros": erros,
            }

        mensagens = [
            {
                "remetente": m.remetente,
                "conteudo": m.conteudo,
                "tipo": m.tipo,
                "enviada_em": m.enviada_em.strftime("%H:%M"),
            }
            for m in c.mensagens
        ]

        conversas.append({
            "id": c.id,
            "lead_nome": c.lead_nome or c.lead_telefone,
            "vendedor_nome": vendedores.get(c.vendedor_id, f"ID {c.vendedor_id}"),
            "num_mensagens": len(mensagens),
            "analise": analise_mais_recente,
            "mensagens": mensagens,
        })

if not conversas:
    st.info(f"Nenhuma conversa encontrada para o período {data_inicio.strftime('%d/%m/%Y')} — {data_fim.strftime('%d/%m/%Y')}.")
    st.stop()

st.caption(f"{len(conversas)} conversa(s) encontrada(s)")

# --- Lista de conversas com expander ---
for conv in conversas:
    analise = conv["analise"]
    score_txt = f"Score {analise['score']}" if analise and analise["score"] else "Sem análise"
    classif = analise["classificacao"] if analise else ""
    label = f"{conv['lead_nome']} — {conv['vendedor_nome']} | {score_txt} | {classif} | {conv['num_mensagens']} msgs"

    with st.expander(label):
        # --- Análise IA com badges ---
        if analise:
            st.markdown("**Análise IA**")

            # Badges coloridos
            badges_html = ""
            if analise["score"] is not None:
                cor_s = score_cor(analise["score"])
                badges_html += render_badge(f"Score {analise['score']}", cor_s)
            if analise["classificacao"]:
                cor_c = COR_CLASSIFICACAO.get(analise["classificacao"], CORES["neutro"])
                badges_html += render_badge(analise["classificacao"].upper(), cor_c)
            if analise["sentimento"]:
                cor_sent = COR_SENTIMENTO.get(analise["sentimento"], CORES["neutro"])
                badges_html += render_badge(analise["sentimento"].capitalize(), cor_sent)

            if badges_html:
                st.markdown(badges_html, unsafe_allow_html=True)

            if analise["feedback"]:
                st.markdown(f"**Feedback:** {analise['feedback']}")

            if analise["erros"]:
                st.markdown("**Erros identificados:**")
                for erro in analise["erros"]:
                    if isinstance(erro, dict):
                        render_alerta(
                            f"<strong>{erro.get('tipo', '')}</strong>: {erro.get('descricao', '')}",
                            "danger",
                        )
                    else:
                        render_alerta(str(erro), "danger")

            st.divider()

        # --- Timeline de mensagens ---
        st.markdown("**Mensagens**")
        for msg in conv["mensagens"]:
            role = "assistant" if msg["remetente"] == "vendedor" else "user"
            with st.chat_message(role):
                prefix = f"[{msg['enviada_em']}] "
                if msg["tipo"] != "texto":
                    st.markdown(f"{prefix}_{msg['tipo']}_ — {msg['conteudo']}")
                else:
                    st.markdown(f"{prefix}{msg['conteudo']}")

render_footer()
