"""Utilitarios compartilhados do dashboard: sessao DB, cores, helpers."""

import sys
from contextlib import contextmanager
from pathlib import Path

# Fix sys.path para imports "from src.xxx" funcionarem
# quando Streamlit roda como processo separado (streamlit run src/dashboard/app.py)
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.database.connection import SessionLocal  # noqa: E402


@contextmanager
def get_db():
    """Context manager para sessao do banco. Mesmo padrao do daily.py."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Paleta de cores para graficos
CORES = {
    "primaria": "#1f77b4",
    "sucesso": "#2ca02c",
    "alerta": "#ff7f0e",
    "perigo": "#d62728",
    "neutro": "#7f7f7f",
}

COR_CLASSIFICACAO = {
    "cliente": "#2ca02c",
    "sql": "#1f77b4",
    "mql": "#ff7f0e",
    "lead": "#7f7f7f",
}

COR_SENTIMENTO = {
    "positivo": "#2ca02c",
    "neutro": "#1f77b4",
    "negativo": "#d62728",
}


def score_cor(score: float | None) -> str:
    """Retorna cor hex baseada no score de qualidade do vendedor (0-10)."""
    if score is None:
        return CORES["neutro"]
    if score >= 7:
        return CORES["sucesso"]
    if score >= 5:
        return CORES["alerta"]
    return CORES["perigo"]
