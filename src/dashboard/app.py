"""Dashboard Streamlit - Pagina 1: Visao Geral."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from datetime import date  # noqa: E402

from src.dashboard.utils import get_db, CORES, score_cor  # noqa: E402
from src.database.queries import buscar_metricas_dia, buscar_prompt_ativo, listar_vendedores, salvar_prompt
from src.analysis.prompts import SYSTEM_PROMPT
from src.reports.daily import detectar_alertas

st.set_page_config(
    page_title="Agente Comercial",
    page_icon="📊",
    layout="wide",
)

@st.dialog("Configuracoes — Prompt de Analise IA", width="large")
def dialog_configuracoes():
    st.caption(
        "Edite o system prompt usado pela IA para analisar conversas. "
        "Mudancas sao aplicadas imediatamente nas proximas analises."
    )
    with get_db() as db:
        config_ativa = buscar_prompt_ativo(db)

    prompt_atual = config_ativa.conteudo if config_ativa else SYSTEM_PROMPT
    is_customizado = config_ativa is not None

    if is_customizado:
        st.info("Usando prompt customizado (salvo no banco).")
    else:
        st.info("Usando prompt padrao do sistema.")

    prompt_editado = st.text_area("System Prompt", value=prompt_atual, height=400)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar", type="primary"):
            if not prompt_editado.strip():
                st.error("O prompt nao pode estar vazio.")
            elif prompt_editado.strip() == prompt_atual.strip():
                st.warning("Nenhuma alteracao detectada.")
            else:
                with get_db() as db:
                    salvar_prompt(db, prompt_editado.strip())
                st.success("Prompt salvo com sucesso!")
                st.rerun()
    with col2:
        if st.button("Restaurar Padrao"):
            if not is_customizado:
                st.warning("Ja esta usando o prompt padrao.")
            else:
                with get_db() as db:
                    salvar_prompt(db, SYSTEM_PROMPT)
                st.success("Prompt padrao restaurado!")
                st.rerun()


# --- Header com botao de config ---
header_left, header_right = st.columns([6, 1])
with header_left:
    st.title("Visao Geral")
with header_right:
    st.markdown("<div style='margin-top: 12px'>", unsafe_allow_html=True)
    if st.button("⚙️", help="Configuracoes do prompt IA"):
        dialog_configuracoes()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Seletor de data ---
data_selecionada = st.date_input("Data", value=date.today())
data_str = data_selecionada.strftime("%Y-%m-%d")

# --- Carregar dados ---
with get_db() as db:
    metricas_raw = buscar_metricas_dia(db, data_str)
    vendedores_raw = listar_vendedores(db)

    # Converter para dicts (st.cache_data nao aceita objetos SQLAlchemy)
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

# --- KPI Cards ---
total_atend = sum(m["total_atendimentos"] for m in metricas)
scores = [m["score_medio"] for m in metricas if m["score_medio"] is not None]
score_geral = round(sum(scores) / len(scores), 1) if scores else None
total_mql = sum(m["total_mql"] for m in metricas)
total_sql = sum(m["total_sql"] for m in metricas)
total_conv = sum(m["total_conversoes"] for m in metricas)
total_sem_resp = sum(m["leads_sem_resposta"] for m in metricas)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Atendimentos", total_atend)
c2.metric("Score Medio", score_geral or "--")
c3.metric("MQL", total_mql)
c4.metric("SQL", total_sql)
c5.metric("Conversoes", total_conv)
c6.metric("Sem Resposta", total_sem_resp)

# --- Alertas ---
alertas = detectar_alertas(metricas, nomes)
if alertas:
    st.subheader("Alertas")
    for alerta in alertas:
        st.warning(alerta)

# --- Grafico: Atendimentos por vendedor ---
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
