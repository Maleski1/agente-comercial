FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo da aplicacao
COPY . .

# Criar diretorio de dados
RUN mkdir -p /app/data

# Tornar script de inicio executavel
RUN chmod +x start.sh

EXPOSE 8000 8501

CMD ["./start.sh"]
