"""Formatacao de texto do relatorio diario para WhatsApp."""

from datetime import datetime


def formatar_tempo(segundos: int | None) -> str:
    """Formata segundos em texto legivel: '2min30s', '45s', ou '--'."""
    if segundos is None:
        return "--"
    if segundos >= 60:
        minutos = segundos // 60
        segs = segundos % 60
        return f"{minutos}min{segs:02d}s" if segs else f"{minutos}min"
    return f"{segundos}s"


def formatar_cabecalho(data: str) -> str:
    """Header com data DD/MM/YYYY. Recebe data no formato YYYY-MM-DD."""
    dt = datetime.strptime(data, "%Y-%m-%d")
    return f"*RELATORIO DIARIO - {dt.strftime('%d/%m/%Y')}*\n================================"


def formatar_resumo_geral(metricas: list[dict]) -> str:
    """Agrega totais de todos os vendedores."""
    total_atend = sum(m.get("total_atendimentos", 0) for m in metricas)
    total_mql = sum(m.get("total_mql", 0) for m in metricas)
    total_sql = sum(m.get("total_sql", 0) for m in metricas)
    total_conv = sum(m.get("total_conversoes", 0) for m in metricas)
    total_sem_resp = sum(m.get("leads_sem_resposta", 0) for m in metricas)

    scores = [m["score_medio"] for m in metricas if m.get("score_medio") is not None]
    score_geral = round(sum(scores) / len(scores), 1) if scores else None
    score_txt = str(score_geral) if score_geral is not None else "--"

    return (
        f"\n*RESUMO GERAL*\n"
        f"Total atendimentos: {total_atend}\n"
        f"Score medio: {score_txt}\n"
        f"MQL: {total_mql} | SQL: {total_sql} | Conversoes: {total_conv}\n"
        f"Leads sem resposta: {total_sem_resp}"
    )


def formatar_vendedor(metrica: dict, nome: str) -> str:
    """Secao individual de um vendedor."""
    score_txt = str(metrica["score_medio"]) if metrica.get("score_medio") is not None else "--"
    primeira = formatar_tempo(metrica.get("tempo_primeira_resp_seg"))
    media = formatar_tempo(metrica.get("tempo_medio_resposta_seg"))

    return (
        f"\n*{nome}*\n"
        f"Atendimentos: {metrica.get('total_atendimentos', 0)} | Score: {score_txt}\n"
        f"1a resposta: {primeira} | Media: {media}\n"
        f"MQL: {metrica.get('total_mql', 0)} | "
        f"SQL: {metrica.get('total_sql', 0)} | "
        f"Conversoes: {metrica.get('total_conversoes', 0)}"
    )


def formatar_alertas(alertas: list[str]) -> str:
    """Formata lista de alertas. Retorna string vazia se nao houver alertas."""
    if not alertas:
        return ""
    linhas = "\n".join(alertas)
    return f"\n*ALERTAS*\n{linhas}"


def montar_relatorio_completo(
    data: str,
    metricas: list[dict],
    nomes: dict[int, str],
    alertas: list[str],
) -> str:
    """Monta o relatorio final juntando todas as secoes."""
    partes = [formatar_cabecalho(data)]
    partes.append(formatar_resumo_geral(metricas))

    for metrica in metricas:
        vid = metrica["vendedor_id"]
        nome = nomes.get(vid, f"Vendedor {vid}")
        partes.append("--------------------------------")
        partes.append(formatar_vendedor(metrica, nome))

    secao_alertas = formatar_alertas(alertas)
    if secao_alertas:
        partes.append("--------------------------------")
        partes.append(secao_alertas)

    return "\n".join(partes)
