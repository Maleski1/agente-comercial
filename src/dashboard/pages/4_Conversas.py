"""Dashboard - Pagina 4: Drill-down de Conversas."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import json  # noqa: E402

import streamlit as st  # noqa: E402
from datetime import date  # noqa: E402

from src.dashboard.utils import get_db, COR_CLASSIFICACAO, COR_SENTIMENTO, score_cor  # noqa: E402
from src.database.queries import buscar_conversas_do_dia, listar_vendedores

st.title("Conversas")

# --- Carregar vendedores ---
with get_db() as db:
    vendedores_raw = listar_vendedores(db)
    vendedores = {v.id: v.nome for v in vendedores_raw}

# --- Filtros ---
col1, col2 = st.columns(2)
with col1:
    data_selecionada = st.date_input("Data", value=date.today())
    data_str = data_selecionada.strftime("%Y-%m-%d")
with col2:
    opcoes_vendedor = ["Todos"] + list(vendedores.values())
    vendedor_filtro = st.selectbox("Vendedor", opcoes_vendedor)

vendedor_id = None
if vendedor_filtro != "Todos":
    vendedor_id = [k for k, v in vendedores.items() if v == vendedor_filtro][0]

# --- Carregar conversas ---
with get_db() as db:
    conversas_raw = buscar_conversas_do_dia(db, data_str, vendedor_id)

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
    st.info(f"Nenhuma conversa encontrada para {data_selecionada.strftime('%d/%m/%Y')}.")
    st.stop()

st.caption(f"{len(conversas)} conversa(s) encontrada(s)")

# --- Lista de conversas com expander ---
for conv in conversas:
    analise = conv["analise"]
    score_txt = f"Score {analise['score']}" if analise and analise["score"] else "Sem analise"
    classif = analise["classificacao"] if analise else ""
    label = f"{conv['lead_nome']} — {conv['vendedor_nome']} | {score_txt} | {classif} | {conv['num_mensagens']} msgs"

    with st.expander(label):
        # --- Analise IA ---
        if analise:
            st.markdown("**Analise IA**")
            m1, m2, m3 = st.columns(3)
            m1.metric("Score", analise["score"] or "--")
            m2.metric("Classificacao", analise["classificacao"] or "--")
            m3.metric("Sentimento", analise["sentimento"] or "--")

            if analise["feedback"]:
                st.markdown(f"**Feedback:** {analise['feedback']}")

            if analise["erros"]:
                st.markdown("**Erros identificados:**")
                for erro in analise["erros"]:
                    if isinstance(erro, dict):
                        st.markdown(f"- **{erro.get('tipo', '')}**: {erro.get('descricao', '')}")
                    else:
                        st.markdown(f"- {erro}")

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
