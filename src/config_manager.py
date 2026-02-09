"""Gerenciador de configuracoes: DB first (empresa → global), .env fallback."""

from src.config import settings
from src.database.connection import SessionLocal
from src.database.queries import buscar_configuracao

# Mapa: chave no banco -> atributo do settings (.env)
_SETTINGS_MAP = {
    "openai_api_key": "openai_api_key",
    "evolution_api_url": "evolution_api_url",
    "evolution_api_key": "evolution_api_key",
    "evolution_instance_name": "evolution_instance_name",
    "gestor_telefone": "gestor_telefone",
    "horario_relatorio": "horario_relatorio",
}


def get_config(
    chave: str, empresa_id: int | None = None, default: str | None = None
) -> str | None:
    """Busca configuracao com cascata: empresa → global (DB) → .env → default.

    Args:
        chave: nome da configuracao (ex: "openai_api_key")
        empresa_id: se informado, busca config da empresa primeiro
        default: valor padrao caso nao encontre em nenhum lugar
    """
    # 1. Busca no banco (empresa first, global fallback via query)
    db = SessionLocal()
    try:
        config = buscar_configuracao(db, chave, empresa_id=empresa_id)
        if config and config.valor:
            return config.valor
    finally:
        db.close()

    # 2. Fallback para settings (.env)
    attr = _SETTINGS_MAP.get(chave)
    if attr:
        valor = getattr(settings, attr, None)
        if valor:
            return valor

    # 3. Fallback para default
    return default
