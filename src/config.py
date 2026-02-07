from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Evolution API
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance_name: str = "agente-comercial"

    # Banco de dados
    database_url: str = "sqlite:///data/agente_comercial.db"

    # Configuracoes do sistema
    gestor_telefone: str = ""
    horario_relatorio: str = "20:00"
    webhook_url: str = "http://host.docker.internal:8000/webhook/messages"

    model_config = {"env_file": ".env"}


settings = Settings()
