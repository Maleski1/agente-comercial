"""Tema corporativo — paleta, CSS enterprise, componentes HTML, template Plotly."""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# =============================================================================
# Paleta de Cores
# =============================================================================

CORES = {
    "primaria": "#1B6CA8",
    "primaria_escura": "#0F3460",
    "primaria_clara": "#5DADE2",
    "primaria_bg": "#EBF5FB",
    "sucesso": "#27AE60",
    "alerta": "#F39C12",
    "perigo": "#E74C3C",
    "neutro": "#566573",
    "texto": "#1C2833",
    "texto_secundario": "#566573",
    "texto_muted": "#ABB2B9",
    "borda": "#D5D8DC",
    "fundo": "#F8F9FA",
    "branco": "#FFFFFF",
}

COR_CLASSIFICACAO = {
    "cliente": "#27AE60",
    "sql": "#1B6CA8",
    "mql": "#F39C12",
    "lead": "#ABB2B9",
}

COR_SENTIMENTO = {
    "positivo": "#27AE60",
    "neutro": "#1B6CA8",
    "negativo": "#E74C3C",
}

# Sequência de 8 cores para gráficos
CHART_COLORS = [
    "#1B6CA8", "#5DADE2", "#0F3460", "#27AE60",
    "#F39C12", "#E74C3C", "#8E44AD", "#1ABC9C",
]


def score_cor(score: float | None) -> str:
    """Retorna cor hex baseada no score (0-10)."""
    if score is None:
        return CORES["neutro"]
    if score >= 7:
        return CORES["sucesso"]
    if score >= 5:
        return CORES["alerta"]
    return CORES["perigo"]


def score_accent(score: float | None) -> str:
    """Retorna cor de accent para borda de cards."""
    return score_cor(score)


# =============================================================================
# CSS Global — Enterprise / HubSpot-inspired
# =============================================================================

_CSS = """
<style>
/* --- Sidebar escura --- */
section[data-testid="stSidebar"] {
    background: #2D3436;
}
section[data-testid="stSidebar"] * {
    color: #DFE6E9 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] span {
    color: #ABB2B9 !important;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stTextInput label {
    color: #ABB2B9 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1);
}

/* --- Headers limpos --- */
h1 {
    color: #1C2833 !important;
    font-weight: 700;
    font-size: 1.6rem !important;
    border: none !important;
}
h2 {
    color: #1C2833 !important;
    font-weight: 600;
    font-size: 1.15rem !important;
}
h3 {
    color: #566573 !important;
    font-weight: 600;
    font-size: 1rem !important;
}

/* --- Metric cards override --- */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #EAECEE;
    border-radius: 8px;
    padding: 16px;
}
div[data-testid="stMetric"] label {
    text-transform: uppercase;
    font-size: 0.7rem !important;
    letter-spacing: 0.06em;
    color: #566573 !important;
    font-weight: 600;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700;
    color: #1C2833 !important;
}

/* --- KPI Card --- */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #EAECEE;
    border-radius: 8px;
    padding: 20px 16px;
    text-align: center;
    transition: box-shadow 0.15s ease;
}
.kpi-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.kpi-card .kpi-label {
    text-transform: uppercase;
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    color: #566573;
    font-weight: 600;
    margin-bottom: 6px;
}
.kpi-card .kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1C2833;
    line-height: 1.2;
}
.kpi-card .kpi-delta {
    font-size: 0.78rem;
    margin-top: 4px;
    color: #566573;
}
.kpi-card .kpi-accent-bar {
    width: 32px;
    height: 3px;
    border-radius: 2px;
    margin: 0 auto 10px auto;
}

/* --- Alert card --- */
.alert-card {
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 6px;
    border-left: 3px solid;
    font-size: 0.88rem;
    line-height: 1.5;
    color: #1C2833;
}
.alert-card.warning {
    background: #FEF9E7;
    border-left-color: #F39C12;
}
.alert-card.danger {
    background: #FDEDEC;
    border-left-color: #E74C3C;
}
.alert-card.success {
    background: #EAFAF1;
    border-left-color: #27AE60;
}
.alert-card.info {
    background: #EBF5FB;
    border-left-color: #1B6CA8;
}

/* --- Expanders --- */
div[data-testid="stExpander"] {
    border: 1px solid #EAECEE;
    border-radius: 8px;
    margin-bottom: 6px;
}

/* --- Tabs --- */
button[data-baseweb="tab"] {
    font-weight: 500;
    font-size: 0.9rem;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom-color: #1B6CA8 !important;
    color: #1B6CA8 !important;
}

/* --- Primary buttons --- */
button[data-testid="stBaseButton-primary"] {
    background: #1B6CA8;
    border: none;
    border-radius: 6px;
    font-weight: 600;
}
button[data-testid="stBaseButton-primary"]:hover {
    background: #0F3460;
}

/* --- Badge --- */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 4px;
}

/* --- Footer --- */
.footer {
    text-align: center;
    padding: 20px 0 10px 0;
    color: #ABB2B9;
    font-size: 0.75rem;
    border-top: 1px solid #EAECEE;
    margin-top: 40px;
}

/* --- Page header --- */
.page-header {
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #EAECEE;
}
.page-header h1 {
    margin-bottom: 2px !important;
    padding-bottom: 0 !important;
    border: none !important;
}
.page-header .subtitle {
    color: #566573;
    font-size: 0.88rem;
}
</style>
"""


def aplicar_tema():
    """Injeta CSS global. Chamar uma vez no topo de cada página."""
    st.markdown(_CSS, unsafe_allow_html=True)


# =============================================================================
# Componentes HTML
# =============================================================================


def render_kpi_card(label: str, value, accent: str = "", delta: str = ""):
    """Renderiza um KPI card enterprise. Usar dentro de st.columns."""
    accent_html = (
        f'<div class="kpi-accent-bar" style="background:{accent}"></div>'
        if accent else '<div style="height:13px"></div>'
    )
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    html = f"""
    <div class="kpi-card">
        {accent_html}
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_sidebar(empresa_nome: str):
    """Branding na sidebar."""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 12px 0 6px 0;">
                <div style="font-size:1.1rem; font-weight:700; color:#FFFFFF !important;
                     letter-spacing: 0.02em;">
                    Agente Comercial
                </div>
                <div style="font-size:0.78rem; color:#ABB2B9 !important; margin-top:4px;">
                    {empresa_nome}
                </div>
            </div>
            <hr style="border-color:rgba(255,255,255,0.1); margin: 6px 0 12px 0;">
            """,
            unsafe_allow_html=True,
        )


def render_page_header(titulo: str, subtitulo: str = ""):
    """Header de página limpo."""
    sub_html = f'<div class="subtitle">{subtitulo}</div>' if subtitulo else ""
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{titulo}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Rodapé padrão."""
    st.markdown(
        '<div class="footer">Agente Comercial &mdash; Plataforma de Inteligência Comercial</div>',
        unsafe_allow_html=True,
    )


def render_alerta(texto: str, tipo: str = "warning"):
    """Alerta estilizado. tipo: warning, danger, success, info."""
    st.markdown(
        f'<div class="alert-card {tipo}">{texto}</div>',
        unsafe_allow_html=True,
    )


def render_badge(texto: str, cor_fundo: str, cor_texto: str = "#FFFFFF"):
    """Retorna HTML de badge inline."""
    return f'<span class="badge" style="background:{cor_fundo};color:{cor_texto}">{texto}</span>'


# =============================================================================
# Template Plotly Corporativo
# =============================================================================

_corporate_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, -apple-system, sans-serif", color=CORES["texto"], size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CHART_COLORS,
        xaxis=dict(
            gridcolor="#F0F0F0",
            linecolor="#EAECEE",
            zerolinecolor="#EAECEE",
        ),
        yaxis=dict(
            gridcolor="#F0F0F0",
            linecolor="#EAECEE",
            zerolinecolor="#EAECEE",
        ),
        hoverlabel=dict(
            bgcolor="#2D3436",
            font_color="#FFFFFF",
            font_size=12,
        ),
        margin=dict(l=40, r=20, t=40, b=40),
    )
)

pio.templates["corporate_blue"] = _corporate_template
pio.templates.default = "plotly+corporate_blue"


# =============================================================================
# Gráficos Especiais
# =============================================================================


def criar_gauge(valor: float, titulo: str = "", maximo: float = 10):
    """Gauge chart para scores — faixas vermelho/amarelo/verde."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=valor,
            title={"text": titulo, "font": {"size": 14, "color": CORES["texto_secundario"]}},
            number={"font": {"size": 32, "color": CORES["texto"]}},
            gauge={
                "axis": {"range": [0, maximo], "tickcolor": CORES["borda"]},
                "bar": {"color": CORES["primaria"]},
                "bgcolor": "#F8F9FA",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, maximo * 0.5], "color": "#FDEDEC"},
                    {"range": [maximo * 0.5, maximo * 0.7], "color": "#FEF9E7"},
                    {"range": [maximo * 0.7, maximo], "color": "#EAFAF1"},
                ],
                "threshold": {
                    "line": {"color": CORES["perigo"], "width": 2},
                    "thickness": 0.8,
                    "value": maximo * 0.5,
                },
            },
        )
    )
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def criar_donut(labels: list, values: list, titulo: str = ""):
    """Donut chart para distribuições."""
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=CHART_COLORS[: len(labels)]),
            textinfo="label+percent",
            textfont=dict(size=11),
        )
    )
    fig.update_layout(
        title=titulo,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    return fig


def criar_funnel(etapas: list, valores: list):
    """Funnel chart para pipeline de leads."""
    cores_funnel = ["#0F3460", "#1B6CA8", "#5DADE2", "#27AE60"]
    fig = go.Figure(
        go.Funnel(
            y=etapas,
            x=valores,
            textinfo="value+percent initial",
            marker=dict(color=cores_funnel[: len(etapas)]),
            connector=dict(line=dict(color=CORES["borda"], width=1)),
        )
    )
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
    )
    return fig
