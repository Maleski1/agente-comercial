"""Dashboard - Página 3: Ranking Comparativo — multi-tenant."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import pandas as pd  # noqa: E402
from collections import defaultdict  # noqa: E402
from datetime import date, timedelta  # noqa: E402

from src.dashboard.utils import get_db, score_cor, validar_token_empresa  # noqa: E402
from src.dashboard.theme import (  # noqa: E402
    aplicar_tema,
    render_sidebar,
    render_page_header,
    render_footer,
    criar_gauge,
    CORES,
)
from src.database.queries import buscar_metricas_periodo, listar_vendedores
from src.reports.templates import formatar_tempo

# --- Tema e autenticação ---
aplicar_tema()
empresa_id, empresa_nome = validar_token_empresa()
render_sidebar(empresa_nome)
render_page_header("Ranking", "Comparativo de performance da equipe")

# --- Seletor de período ---
date_range = st.date_input(
    "Período",
    value=(date.today() - timedelta(days=6), date.today()),
)
if not isinstance(date_range, tuple) or len(date_range) != 2:
    st.info("Selecione a data final do período.")
    st.stop()

data_inicio, data_fim = date_range
str_inicio = data_inicio.strftime("%Y-%m-%d")
str_fim = data_fim.strftime("%Y-%m-%d")

# --- Carregar dados (filtrado por empresa) ---
with get_db() as db:
    metricas_raw = buscar_metricas_periodo(db, str_inicio, str_fim, empresa_id=empresa_id)
    vendedores_raw = listar_vendedores(db, empresa_id=empresa_id)

    nomes = {v.id: v.nome for v in vendedores_raw}

    # Agregar métricas por vendedor (soma/média do período)
    por_vendedor = defaultdict(lambda: {
        "total_atendimentos": 0, "scores": [], "total_mql": 0, "total_sql": 0,
        "total_conversoes": 0, "leads_sem_resposta": 0, "tempos_primeira": [], "tempos_media": [],
    })
    for m in metricas_raw:
        v = por_vendedor[m.vendedor_id]
        v["total_atendimentos"] += m.total_atendimentos
        v["total_mql"] += m.total_mql
        v["total_sql"] += m.total_sql
        v["total_conversoes"] += m.total_conversoes
        v["leads_sem_resposta"] += m.leads_sem_resposta
        if m.score_medio is not None:
            v["scores"].append(m.score_medio)
        if m.tempo_primeira_resp_seg is not None:
            v["tempos_primeira"].append(m.tempo_primeira_resp_seg)
        if m.tempo_medio_resposta_seg is not None:
            v["tempos_media"].append(m.tempo_medio_resposta_seg)

    metricas = []
    for vid, v in por_vendedor.items():
        metricas.append({
            "vendedor_id": vid,
            "total_atendimentos": v["total_atendimentos"],
            "score_medio": round(sum(v["scores"]) / len(v["scores"]), 1) if v["scores"] else None,
            "total_mql": v["total_mql"],
            "total_sql": v["total_sql"],
            "total_conversoes": v["total_conversoes"],
            "leads_sem_resposta": v["leads_sem_resposta"],
            "tempo_primeira_resp_seg": round(sum(v["tempos_primeira"]) / len(v["tempos_primeira"])) if v["tempos_primeira"] else None,
            "tempo_medio_resposta_seg": round(sum(v["tempos_media"]) / len(v["tempos_media"])) if v["tempos_media"] else None,
        })

if not metricas:
    st.info(f"Nenhuma métrica encontrada para o período {data_inicio.strftime('%d/%m/%Y')} — {data_fim.strftime('%d/%m/%Y')}.")
    st.stop()

# Ordenar por score (desc), None fica no final
metricas.sort(key=lambda m: m["score_medio"] if m["score_medio"] is not None else -1, reverse=True)

# --- Gauge: Score médio da equipe ---
com_score = [m for m in metricas if m["score_medio"] is not None]
if com_score:
    score_equipe = round(sum(m["score_medio"] for m in com_score) / len(com_score), 1)

    col_gauge, col_cards = st.columns([2, 3])
    with col_gauge:
        fig_gauge = criar_gauge(score_equipe, "Score Médio da Equipe")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_cards:
        melhor = com_score[0]
        pior = com_score[-1]

        # Card Melhor
        st.markdown(
            f"""
            <div style="background:#EAFAF1; border-left:3px solid {CORES['sucesso']};
                        border-radius:6px; padding:16px; margin-bottom:12px;">
                <div style="font-size:0.7rem; text-transform:uppercase; color:{CORES['sucesso']};
                            font-weight:600; letter-spacing:0.06em;">Melhor Performance</div>
                <div style="font-size:1.2rem; font-weight:700; color:{CORES['texto']}; margin-top:4px;">
                    {nomes.get(melhor['vendedor_id'], '—')}
                </div>
                <div style="font-size:0.9rem; color:{CORES['sucesso']}; margin-top:2px;">
                    Score {melhor['score_medio']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Card Precisa Atenção
        st.markdown(
            f"""
            <div style="background:#FDEDEC; border-left:3px solid {CORES['perigo']};
                        border-radius:6px; padding:16px;">
                <div style="font-size:0.7rem; text-transform:uppercase; color:{CORES['perigo']};
                            font-weight:600; letter-spacing:0.06em;">Precisa Atenção</div>
                <div style="font-size:1.2rem; font-weight:700; color:{CORES['texto']}; margin-top:4px;">
                    {nomes.get(pior['vendedor_id'], '—')}
                </div>
                <div style="font-size:0.9rem; color:{CORES['perigo']}; margin-top:2px;">
                    Score {pior['score_medio']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

# --- Gráfico: Barras horizontais por score ---
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
            textposition="outside",
            textfont=dict(size=12),
        )
    ]
)
fig.update_layout(
    xaxis_title="Score",
    xaxis_range=[0, 10.5],
    height=max(300, len(metricas) * 55),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

# --- Tabela comparativa ---
st.subheader("Comparativo Detalhado")
tabela = []
for m in metricas:
    tabela.append({
        "Vendedor": nomes.get(m["vendedor_id"], f"ID {m['vendedor_id']}"),
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
