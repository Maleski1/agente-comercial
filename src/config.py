from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Evolution API
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance_name: str = "agente-comercial"

    # Banco de dados
    database_url: str = "postgresql://agente:agente123@localhost:5432/agente_comercial"

    # Configuracoes do sistema
    gestor_telefone: str = ""
    horario_relatorio: str = "20:00"
    webhook_url: str = "http://host.docker.internal:8000/webhook/messages"
    webhook_secret: str = ""  # secret para validar webhooks da Evolution API
    admin_key: str = "admin123"  # senha para pagina admin do dashboard

    model_config = {"env_file": ".env"}


settings = Settings()
