"""Dashboard - Página 5: Insights & Inteligência — multi-tenant."""

import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402

from src.dashboard.utils import get_db, validar_token_empresa  # noqa: E402
from src.dashboard.theme import (  # noqa: E402
    aplicar_tema,
    render_sidebar,
    render_page_header,
    render_footer,
    render_alerta,
    CORES,
    COR_SENTIMENTO,
)
from src.database.queries import (  # noqa: E402
    buscar_metricas_periodo,
    buscar_analises_periodo,
    buscar_mensagens_periodo,
    listar_vendedores,
)

# --- Tema e autenticação ---
aplicar_tema()
empresa_id, empresa_nome = validar_token_empresa()
render_sidebar(empresa_nome)
render_page_header("Insights", "Inteligência e tendências da equipe")

# --- Seletor de período ---
periodo = st.selectbox("Período", ["7 dias", "15 dias", "30 dias"])
dias = int(periodo.split()[0])
data_fim = date.today()
data_inicio = data_fim - timedelta(days=dias - 1)
str_inicio = data_inicio.strftime("%Y-%m-%d")
str_fim = data_fim.strftime("%Y-%m-%d")

# --- Carregar dados ---
with get_db() as db:
    metricas_raw = buscar_metricas_periodo(db, str_inicio, str_fim, empresa_id=empresa_id)
    analises_raw = buscar_analises_periodo(db, str_inicio, str_fim, empresa_id=empresa_id)
    mensagens_raw = buscar_mensagens_periodo(db, str_inicio, str_fim, empresa_id=empresa_id)
    vendedores_raw = listar_vendedores(db, empresa_id=empresa_id)
    nomes = {v.id: v.nome for v in vendedores_raw}

if not metricas_raw and not analises_raw:
    render_alerta("Nenhum dado encontrado para o período selecionado.", "info")
    st.stop()

# =============================================================================
# 1. Tendência do Período
# =============================================================================
st.subheader("Tendência do Período")

if metricas_raw:
    # Agregar métricas por dia
    por_dia = defaultdict(lambda: {"atend": 0, "scores": [], "conv": 0, "mql": 0, "sql": 0})
    for m in metricas_raw:
        d = por_dia[m.data]
        d["atend"] += m.total_atendimentos
        d["conv"] += m.total_conversoes
        d["mql"] += m.total_mql
        d["sql"] += m.total_sql
        if m.score_medio is not None:
            d["scores"].append(m.score_medio)

    datas = sorted(por_dia.keys())
    atendimentos = [por_dia[d]["atend"] for d in datas]
    scores_dia = [
        round(sum(por_dia[d]["scores"]) / len(por_dia[d]["scores"]), 1) if por_dia[d]["scores"] else None
        for d in datas
    ]
    conversoes_dia = [por_dia[d]["conv"] for d in datas]

    col_tend1, col_tend2 = st.columns(2)

    with col_tend1:
        fig_atend = go.Figure()
        fig_atend.add_trace(go.Scatter(
            x=datas, y=atendimentos, mode="lines+markers",
            name="Atendimentos", line=dict(color=CORES["primaria"], width=2),
            fill="tozeroy", fillcolor="rgba(27, 108, 168, 0.1)",
        ))
        fig_atend.add_trace(go.Scatter(
            x=datas, y=conversoes_dia, mode="lines+markers",
            name="Conversões", line=dict(color=CORES["sucesso"], width=2),
            fill="tozeroy", fillcolor="rgba(39, 174, 96, 0.08)",
        ))
        fig_atend.update_layout(
            title="Atendimentos e Conversões",
            height=320, yaxis_title="Quantidade",
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig_atend, use_container_width=True)

    with col_tend2:
        fig_score = go.Figure()
        fig_score.add_trace(go.Scatter(
            x=datas, y=scores_dia, mode="lines+markers",
            name="Score Médio", line=dict(color=CORES["primaria"], width=2),
            fill="tozeroy", fillcolor="rgba(27, 108, 168, 0.1)",
            connectgaps=True,
        ))
        fig_score.add_hrect(y0=0, y1=5, fillcolor="rgba(231,76,60,0.06)", line_width=0)
        fig_score.add_hline(y=5, line_dash="dash", line_color=CORES["perigo"],
                            annotation_text="Mínimo")
        fig_score.update_layout(
            title="Score Médio da Equipe",
            height=320, yaxis_title="Score", yaxis_range=[0, 10],
        )
        st.plotly_chart(fig_score, use_container_width=True)

else:
    render_alerta("Sem métricas no período para gerar tendência.", "info")

# =============================================================================
# 2. Horário de Pico
# =============================================================================
st.subheader("Horário de Pico")

if mensagens_raw:
    contagem_hora = [0] * 24
    for msg in mensagens_raw:
        contagem_hora[msg.enviada_em.hour] += 1

    # Pico = horas acima da média (ignora horas zeradas)
    valores_positivos = [c for c in contagem_hora if c > 0]
    media = sum(valores_positivos) / len(valores_positivos) if valores_positivos else 0
    cores_hora = [
        CORES["primaria_escura"] if c >= media and c > 0 else CORES["primaria_clara"]
        for c in contagem_hora
    ]

    fig_hora = go.Figure(
        go.Bar(
            x=list(range(24)),
            y=contagem_hora,
            marker_color=cores_hora,
            text=contagem_hora,
            textposition="auto",
        )
    )
    fig_hora.update_layout(
        xaxis_title="Hora do Dia",
        yaxis_title="Mensagens",
        xaxis=dict(tickmode="linear", dtick=1),
        height=350,
        showlegend=False,
    )
    st.plotly_chart(fig_hora, use_container_width=True)
else:
    render_alerta("Sem mensagens no período para análise de horário.", "info")

# =============================================================================
# 3. Top Erros Mais Comuns
# =============================================================================
st.subheader("Top Erros Mais Comuns")

if analises_raw:
    todos_erros = []
    for a in analises_raw:
        if a.erros:
            try:
                erros = json.loads(a.erros)
                for erro in erros:
                    if isinstance(erro, dict):
                        todos_erros.append(erro.get("tipo", "Outro"))
                    else:
                        todos_erros.append(str(erro))
            except (json.JSONDecodeError, TypeError):
                pass

    if todos_erros:
        contagem_erros = Counter(todos_erros).most_common(10)
        tipos = [e[0] for e in contagem_erros]
        qtds = [e[1] for e in contagem_erros]

        fig_erros = go.Figure(
            go.Bar(
                y=tipos[::-1],
                x=qtds[::-1],
                orientation="h",
                marker_color=CORES["perigo"],
                text=qtds[::-1],
                textposition="outside",
            )
        )
        fig_erros.update_layout(
            height=max(250, len(tipos) * 40),
            showlegend=False,
            xaxis_title="Ocorrências",
        )
        st.plotly_chart(fig_erros, use_container_width=True)
    else:
        render_alerta("Nenhum erro identificado no período.", "success")
else:
    render_alerta("Sem análises no período.", "info")

# =============================================================================
# 4. Sentimento por Vendedor
# =============================================================================
st.subheader("Sentimento por Vendedor")

if analises_raw:
    sent_por_vend = defaultdict(lambda: Counter())
    for a in analises_raw:
        if a.sentimento_lead and a.conversa:
            vend_id = a.conversa.vendedor_id
            vend_nome = nomes.get(vend_id, f"ID {vend_id}")
            sent_por_vend[vend_nome][a.sentimento_lead] += 1

    if sent_por_vend:
        vend_nomes = sorted(sent_por_vend.keys())
        categorias = ["positivo", "neutro", "negativo"]

        fig_sent = go.Figure()
        for cat in categorias:
            fig_sent.add_trace(go.Bar(
                name=cat.capitalize(),
                x=vend_nomes,
                y=[sent_por_vend[v][cat] for v in vend_nomes],
                marker_color=COR_SENTIMENTO.get(cat, CORES["neutro"]),
            ))

        fig_sent.update_layout(
            barmode="stack",
            height=350,
            yaxis_title="Conversas",
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        render_alerta("Sem dados de sentimento no período.", "info")

render_footer()
