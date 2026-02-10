"""Dashboard - Página 1: Visão Geral — multi-tenant."""

import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402

from src.dashboard.utils import get_db, score_cor, validar_token_empresa  # noqa: E402
from src.dashboard.theme import (  # noqa: E402
    aplicar_tema,
    render_kpi_card,
    render_sidebar,
    render_page_header,
    render_footer,
    render_alerta,
    criar_funnel,
    CORES,
    COR_CLASSIFICACAO,
    COR_SENTIMENTO,
)
from src.database.queries import (  # noqa: E402
    buscar_metricas_periodo,
    listar_vendedores,
    buscar_conversas_periodo,
)
from src.metrics.calculator import calcular_metricas  # noqa: E402
from src.reports.daily import detectar_alertas  # noqa: E402
from src.reports.templates import formatar_tempo  # noqa: E402

# --- Tema e autenticação ---
aplicar_tema()
empresa_id, empresa_nome = validar_token_empresa()
render_sidebar(empresa_nome)
render_page_header("Visão Geral", f"Dashboard de performance — {empresa_nome}")

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

    # Auto-calcular métricas do dia atual se não existem
    hoje = date.today().isoformat()
    if not metricas_raw or not any(m.data == hoje for m in metricas_raw):
        if str_inicio <= hoje <= str_fim:
            calcular_metricas(db, hoje, empresa_id=empresa_id)
            metricas_raw = buscar_metricas_periodo(db, str_inicio, str_fim, empresa_id=empresa_id)

    vendedores_raw = listar_vendedores(db, empresa_id=empresa_id)
    conversas_raw = buscar_conversas_periodo(db, str_inicio, str_fim, empresa_id=empresa_id)

    nomes = {v.id: v.nome for v in vendedores_raw}

    # Agregar métricas por vendedor (soma do período)
    por_vendedor = defaultdict(lambda: {
        "total_atendimentos": 0, "scores": [], "total_mql": 0, "total_sql": 0,
        "total_conversoes": 0, "leads_sem_resposta": 0, "tempos": [],
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
        if m.tempo_medio_resposta_seg is not None:
            v["tempos"].append(m.tempo_medio_resposta_seg)

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
            "tempo_medio_resposta_seg": round(sum(v["tempos"]) / len(v["tempos"])) if v["tempos"] else None,
        })

    # Extrair análises para donuts
    sentimentos = []
    classificacoes = []
    for c in conversas_raw:
        if c.analises:
            a = max(c.analises, key=lambda x: x.analisada_em)
            if a.sentimento_lead:
                sentimentos.append(a.sentimento_lead)
            if a.classificacao:
                classificacoes.append(a.classificacao)

if not metricas:
    render_alerta(
        f"Nenhuma métrica encontrada para o período {data_inicio.strftime('%d/%m/%Y')} — {data_fim.strftime('%d/%m/%Y')}.",
        "info",
    )
    st.stop()

# --- KPI Cards (8 cards em 2 linhas) ---
total_atend = sum(m["total_atendimentos"] for m in metricas)
scores = [m["score_medio"] for m in metricas if m["score_medio"] is not None]
score_geral = round(sum(scores) / len(scores), 1) if scores else None
total_mql = sum(m["total_mql"] for m in metricas)
total_sql = sum(m["total_sql"] for m in metricas)
total_conv = sum(m["total_conversoes"] for m in metricas)
total_sem_resp = sum(m["leads_sem_resposta"] for m in metricas)
taxa_conversao = round((total_conv / total_atend) * 100, 1) if total_atend > 0 else 0

# Tempo médio geral
tempos = [m["tempo_medio_resposta_seg"] for m in metricas if m["tempo_medio_resposta_seg"]]
tempo_medio_geral = round(sum(tempos) / len(tempos)) if tempos else None

# Linha 1: 4 KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Atendimentos", total_atend, accent=CORES["primaria"])
with c2:
    render_kpi_card("Score Médio", score_geral or "--", accent=score_cor(score_geral))
with c3:
    render_kpi_card(
        "Taxa de Conversão", f"{taxa_conversao}%",
        accent=CORES["sucesso"] if taxa_conversao >= 10 else CORES["alerta"],
    )
with c4:
    render_kpi_card(
        "Tempo Médio", formatar_tempo(tempo_medio_geral) if tempo_medio_geral else "--",
        accent=CORES["primaria"],
    )

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Linha 2: 4 KPIs
c5, c6, c7, c8 = st.columns(4)
with c5:
    render_kpi_card("MQL", total_mql, accent=CORES["primaria"])
with c6:
    render_kpi_card("SQL", total_sql, accent=CORES["primaria"])
with c7:
    render_kpi_card("Conversões", total_conv, accent=CORES["sucesso"])
with c8:
    render_kpi_card(
        "Sem Resposta", total_sem_resp,
        accent=CORES["perigo"] if total_sem_resp > 0 else CORES["sucesso"],
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Alertas ---
alertas = detectar_alertas(metricas, nomes)
if alertas:
    st.subheader("Alertas")
    for alerta in alertas:
        render_alerta(alerta, "warning")

# --- Gráficos: Bar + Funnel ---
col_chart, col_funnel = st.columns([3, 2])

with col_chart:
    st.subheader("Atendimentos por Vendedor")
    nomes_vendedores = [nomes.get(m["vendedor_id"], f"ID {m['vendedor_id']}") for m in metricas]
    atendimentos = [m["total_atendimentos"] for m in metricas]
    cores_barras = [score_cor(m["score_medio"]) for m in metricas]

    fig = go.Figure(
        data=[
            go.Bar(
                x=nomes_vendedores,
                y=atendimentos,
                marker_color=cores_barras,
                text=atendimentos,
                textposition="auto",
                textfont=dict(color="#FFFFFF", size=13),
            )
        ]
    )
    fig.update_layout(
        xaxis_title="Vendedor",
        yaxis_title="Atendimentos",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_funnel:
    st.subheader("Pipeline de Leads")
    etapas = ["Leads", "MQL", "SQL", "Conversão"]
    valores = [total_atend, total_mql, total_sql, total_conv]
    fig_funnel = criar_funnel(etapas, valores)
    st.plotly_chart(fig_funnel, use_container_width=True)

# --- Gráficos: Donut Sentimento + Donut Classificação ---
if sentimentos or classificacoes:
    col_sent, col_class = st.columns(2)

    with col_sent:
        if sentimentos:
            st.subheader("Sentimento dos Leads")
            contagem_sent = {}
            for s in sentimentos:
                contagem_sent[s] = contagem_sent.get(s, 0) + 1
            labels_s = list(contagem_sent.keys())
            values_s = list(contagem_sent.values())
            cores_s = [COR_SENTIMENTO.get(l, CORES["neutro"]) for l in labels_s]

            fig_sent = go.Figure(
                go.Pie(
                    labels=[l.capitalize() for l in labels_s],
                    values=values_s,
                    hole=0.55,
                    marker=dict(colors=cores_s),
                    textinfo="label+percent",
                    textfont=dict(size=12),
                )
            )
            fig_sent.update_layout(
                height=300, margin=dict(l=20, r=20, t=20, b=20), showlegend=False,
            )
            st.plotly_chart(fig_sent, use_container_width=True)

    with col_class:
        if classificacoes:
            st.subheader("Classificação dos Leads")
            contagem_cl = {}
            for c in classificacoes:
                contagem_cl[c] = contagem_cl.get(c, 0) + 1
            labels_c = list(contagem_cl.keys())
            values_c = list(contagem_cl.values())
            cores_c = [COR_CLASSIFICACAO.get(l, CORES["neutro"]) for l in labels_c]

            fig_class = go.Figure(
                go.Pie(
                    labels=[l.upper() for l in labels_c],
                    values=values_c,
                    hole=0.55,
                    marker=dict(colors=cores_c),
                    textinfo="label+percent",
                    textfont=dict(size=12),
                )
            )
            fig_class.update_layout(
                height=300, margin=dict(l=20, r=20, t=20, b=20), showlegend=False,
            )
            st.plotly_chart(fig_class, use_container_width=True)

render_footer()
