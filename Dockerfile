FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar config do supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Criar diretório de dados
RUN mkdir -p /app/data

EXPOSE 8000 8501

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
