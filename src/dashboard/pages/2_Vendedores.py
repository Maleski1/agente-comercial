"""Dashboard - Página 2: Histórico Individual do Vendedor — multi-tenant."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import pandas as pd  # noqa: E402
from collections import defaultdict  # noqa: E402
from datetime import date, timedelta  # noqa: E402

from src.dashboard.utils import get_db, validar_token_empresa  # noqa: E402
from src.dashboard.theme import (  # noqa: E402
    aplicar_tema,
    render_sidebar,
    render_page_header,
    render_footer,
    CORES,
)
from src.database.queries import buscar_metricas_vendedor, buscar_metricas_periodo, listar_vendedores
from src.reports.templates import formatar_tempo

# --- Tema e autenticação ---
aplicar_tema()
empresa_id, empresa_nome = validar_token_empresa()
render_sidebar(empresa_nome)
render_page_header("Vendedores", "Histórico individual de performance")

# --- Carregar vendedores da empresa ---
with get_db() as db:
    vendedores_raw = listar_vendedores(db, empresa_id=empresa_id)
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
    periodo = st.selectbox("Período", ["7 dias", "15 dias", "30 dias"])
    limit = int(periodo.split()[0])

# --- Carregar métricas ---
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
    st.info(f"Sem métricas para {vendedor_nome} nos últimos {limit} dias.")
    st.stop()

# Ordenar cronologicamente (query retorna desc)
metricas.sort(key=lambda m: m["data"])
datas = [m["data"] for m in metricas]

# --- Carregar média da equipe para comparação ---
data_inicio_periodo = (date.today() - timedelta(days=limit - 1)).strftime("%Y-%m-%d")
data_fim_periodo = date.today().strftime("%Y-%m-%d")
with get_db() as db:
    todas_metricas = buscar_metricas_periodo(db, data_inicio_periodo, data_fim_periodo, empresa_id=empresa_id)

# Agregar média da equipe por dia
media_equipe_por_dia = defaultdict(list)
for m in todas_metricas:
    if m.score_medio is not None:
        media_equipe_por_dia[m.data].append(m.score_medio)
media_equipe = [
    round(sum(media_equipe_por_dia[d]) / len(media_equipe_por_dia[d]), 1) if d in media_equipe_por_dia else None
    for d in datas
]

# --- Gráfico: Score ao longo do tempo + média da equipe ---
st.subheader("Score de Qualidade")
scores = [m["score_medio"] for m in metricas]

fig_score = go.Figure()
fig_score.add_trace(
    go.Scatter(
        x=datas, y=scores, mode="lines+markers",
        name=vendedor_nome,
        line=dict(color=CORES["primaria"], width=2),
        fill="tozeroy",
        fillcolor="rgba(27, 108, 168, 0.12)",
        marker=dict(size=6, color=CORES["primaria"]),
    )
)
fig_score.add_trace(
    go.Scatter(
        x=datas, y=media_equipe, mode="lines",
        name="Média da Equipe",
        line=dict(color=CORES["texto_muted"], width=2, dash="dot"),
        connectgaps=True,
    )
)
# Faixa de atenção 0-5
fig_score.add_hrect(
    y0=0, y1=5,
    fillcolor="rgba(231, 76, 60, 0.06)",
    line_width=0,
)
fig_score.add_hline(
    y=5.0, line_dash="dash", line_color=CORES["perigo"],
    annotation_text="Mínimo aceitável",
    annotation_font_color=CORES["perigo"],
)
fig_score.update_layout(
    yaxis_title="Score", height=350, yaxis_range=[0, 10],
    legend=dict(orientation="h", y=-0.15),
)
st.plotly_chart(fig_score, use_container_width=True)

# --- Gráfico: Tempos de resposta ---
st.subheader("Tempos de Resposta")
tempos_primeira = [m["tempo_primeira_resp_seg"] for m in metricas]
tempos_media = [m["tempo_medio_resposta_seg"] for m in metricas]

fig_tempo = go.Figure()
fig_tempo.add_trace(
    go.Scatter(
        x=datas, y=tempos_primeira, mode="lines+markers",
        name="1ª Resposta",
        line=dict(color=CORES["alerta"], width=2),
        fill="tozeroy",
        fillcolor="rgba(243, 156, 18, 0.1)",
        marker=dict(size=5),
    )
)
fig_tempo.add_trace(
    go.Scatter(
        x=datas, y=tempos_media, mode="lines+markers",
        name="Média",
        line=dict(color=CORES["primaria"], width=2),
        fill="tozeroy",
        fillcolor="rgba(27, 108, 168, 0.08)",
        marker=dict(size=5),
    )
)
fig_tempo.update_layout(
    yaxis_title="Segundos", height=350,
    legend=dict(orientation="h", y=-0.15),
)
st.plotly_chart(fig_tempo, use_container_width=True)

# --- Gráfico: Evolução do Pipeline ---
st.subheader("Evolução do Pipeline")
mql_dia = [m["total_mql"] for m in metricas]
sql_dia = [m["total_sql"] for m in metricas]
conv_dia = [m["total_conversoes"] for m in metricas]

fig_pipeline = go.Figure()
fig_pipeline.add_trace(go.Bar(
    x=datas, y=mql_dia, name="MQL", marker_color=CORES["alerta"],
))
fig_pipeline.add_trace(go.Bar(
    x=datas, y=sql_dia, name="SQL", marker_color=CORES["primaria"],
))
fig_pipeline.add_trace(go.Bar(
    x=datas, y=conv_dia, name="Conversões", marker_color=CORES["sucesso"],
))
fig_pipeline.update_layout(
    barmode="stack", height=320, yaxis_title="Quantidade",
    legend=dict(orientation="h", y=-0.15),
)
st.plotly_chart(fig_pipeline, use_container_width=True)

# --- Tabela detalhada ---
st.subheader("Detalhamento Diário")

tabela = []
for m in metricas:
    tabela.append({
        "Data": m["data"],
        "Atendimentos": m["total_atendimentos"],
        "Score": m["score_medio"] if m["score_medio"] is not None else 0,
        "1ª Resposta": formatar_tempo(m["tempo_primeira_resp_seg"]),
        "Tempo Médio": formatar_tempo(m["tempo_medio_resposta_seg"]),
        "MQL": m["total_mql"],
        "SQL": m["total_sql"],
        "Conversões": m["total_conversoes"],
        "Sem Resposta": m["leads_sem_resposta"],
    })

df = pd.DataFrame(tabela)
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score": st.column_config.ProgressColumn(
            "Score", min_value=0, max_value=10, format="%.1f",
        ),
    },
)

render_footer()
