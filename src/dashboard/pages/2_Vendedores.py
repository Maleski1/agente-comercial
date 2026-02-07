"""Dashboard - Pagina 2: Historico Individual do Vendedor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402

from src.dashboard.utils import get_db, CORES  # noqa: E402
from src.database.queries import buscar_metricas_vendedor, listar_vendedores
from src.reports.templates import formatar_tempo

st.title("Vendedores")

# --- Carregar vendedores ---
with get_db() as db:
    vendedores_raw = listar_vendedores(db)
    vendedores = {v.id: v.nome for v in vendedores_raw}

if not vendedores:
    st.info("Nenhum vendedor cadastrado.")
    st.stop()

# --- Seletores ---
col1, col2 = st.columns(2)
with col1:
    vendedor_nome = st.selectbox("Vendedor", list(vendedores.values()))
    vendedor_id = [k for k, v in vendedores.items() if v == vendedor_nome][0]
with col2:
    periodo = st.selectbox("Periodo", ["7 dias", "15 dias", "30 dias"])
    limit = int(periodo.split()[0])

# --- Carregar metricas ---
with get_db() as db:
    metricas_raw = buscar_metricas_vendedor(db, vendedor_id, limit=limit)
    metricas = [
        {
            "data": m.data,
            "score_medio": m.score_medio,
            "total_atendimentos": m.total_atendimentos,
            "tempo_primeira_resp_seg": m.tempo_primeira_resp_seg,
            "tempo_medio_resposta_seg": m.tempo_medio_resposta_seg,
            "total_mql": m.total_mql,
            "total_sql": m.total_sql,
            "total_conversoes": m.total_conversoes,
            "leads_sem_resposta": m.leads_sem_resposta,
        }
        for m in metricas_raw
    ]

if not metricas:
    st.info(f"Sem metricas para {vendedor_nome} nos ultimos {limit} dias.")
    st.stop()

# Ordenar cronologicamente (query retorna desc)
metricas.sort(key=lambda m: m["data"])
datas = [m["data"] for m in metricas]

# --- Grafico: Score ao longo do tempo ---
st.subheader("Score de Qualidade")
scores = [m["score_medio"] for m in metricas]

fig_score = go.Figure()
fig_score.add_trace(
    go.Scatter(
        x=datas, y=scores, mode="lines+markers",
        name="Score", line=dict(color=CORES["primaria"], width=2),
    )
)
fig_score.add_hline(y=5.0, line_dash="dash", line_color=CORES["perigo"],
                    annotation_text="Minimo aceitavel")
fig_score.update_layout(yaxis_title="Score", height=350, yaxis_range=[0, 10])
st.plotly_chart(fig_score, use_container_width=True)

# --- Grafico: Tempos de resposta ---
st.subheader("Tempos de Resposta")
tempos_primeira = [m["tempo_primeira_resp_seg"] for m in metricas]
tempos_media = [m["tempo_medio_resposta_seg"] for m in metricas]

fig_tempo = go.Figure()
fig_tempo.add_trace(
    go.Scatter(
        x=datas, y=tempos_primeira, mode="lines+markers",
        name="1a Resposta", line=dict(color=CORES["alerta"], width=2),
    )
)
fig_tempo.add_trace(
    go.Scatter(
        x=datas, y=tempos_media, mode="lines+markers",
        name="Media", line=dict(color=CORES["primaria"], width=2),
    )
)
fig_tempo.update_layout(yaxis_title="Segundos", height=350)
st.plotly_chart(fig_tempo, use_container_width=True)

# --- Tabela detalhada ---
st.subheader("Detalhamento Diario")
tabela = []
for m in metricas:
    tabela.append({
        "Data": m["data"],
        "Atendimentos": m["total_atendimentos"],
        "Score": m["score_medio"] or "--",
        "1a Resposta": formatar_tempo(m["tempo_primeira_resp_seg"]),
        "Tempo Medio": formatar_tempo(m["tempo_medio_resposta_seg"]),
        "MQL": m["total_mql"],
        "SQL": m["total_sql"],
        "Conversoes": m["total_conversoes"],
        "Sem Resposta": m["leads_sem_resposta"],
    })
st.dataframe(tabela, use_container_width=True, hide_index=True)
