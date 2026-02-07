"""Dashboard - Pagina 3: Ranking Comparativo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from datetime import date  # noqa: E402

from src.dashboard.utils import get_db, score_cor  # noqa: E402
from src.database.queries import buscar_metricas_dia, listar_vendedores
from src.reports.templates import formatar_tempo

st.title("Ranking")

# --- Seletor de data ---
data_selecionada = st.date_input("Data", value=date.today())
data_str = data_selecionada.strftime("%Y-%m-%d")

# --- Carregar dados ---
with get_db() as db:
    metricas_raw = buscar_metricas_dia(db, data_str)
    vendedores_raw = listar_vendedores(db)

    metricas = [
        {
            "vendedor_id": m.vendedor_id,
            "total_atendimentos": m.total_atendimentos,
            "score_medio": m.score_medio,
            "total_mql": m.total_mql,
            "total_sql": m.total_sql,
            "total_conversoes": m.total_conversoes,
            "leads_sem_resposta": m.leads_sem_resposta,
            "tempo_primeira_resp_seg": m.tempo_primeira_resp_seg,
            "tempo_medio_resposta_seg": m.tempo_medio_resposta_seg,
        }
        for m in metricas_raw
    ]
    nomes = {v.id: v.nome for v in vendedores_raw}

if not metricas:
    st.info(f"Nenhuma metrica encontrada para {data_selecionada.strftime('%d/%m/%Y')}.")
    st.stop()

# Ordenar por score (desc), None fica no final
metricas.sort(key=lambda m: m["score_medio"] if m["score_medio"] is not None else -1, reverse=True)

# --- Grafico: Barras horizontais por score ---
st.subheader("Ranking por Score")

nomes_ordenados = [nomes.get(m["vendedor_id"], f"ID {m['vendedor_id']}") for m in metricas]
scores = [m["score_medio"] or 0 for m in metricas]
cores = [score_cor(m["score_medio"]) for m in metricas]

fig = go.Figure(
    data=[
        go.Bar(
            y=nomes_ordenados[::-1],
            x=scores[::-1],
            orientation="h",
            marker_color=cores[::-1],
            text=[f"{s:.1f}" if s else "--" for s in scores[::-1]],
            textposition="auto",
        )
    ]
)
fig.update_layout(
    xaxis_title="Score",
    xaxis_range=[0, 10],
    height=max(300, len(metricas) * 50),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

# --- Melhor / Pior ---
com_score = [m for m in metricas if m["score_medio"] is not None]
if com_score:
    melhor = com_score[0]
    pior = com_score[-1]
    col1, col2 = st.columns(2)
    col1.success(f"Melhor: {nomes.get(melhor['vendedor_id'])} — Score {melhor['score_medio']}")
    col2.error(f"Pior: {nomes.get(pior['vendedor_id'])} — Score {pior['score_medio']}")

# --- Tabela comparativa ---
st.subheader("Comparativo Detalhado")
tabela = []
for m in metricas:
    tabela.append({
        "Vendedor": nomes.get(m["vendedor_id"], f"ID {m['vendedor_id']}"),
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
