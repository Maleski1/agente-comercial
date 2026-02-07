# Manual de Implementacao — Agente Comercial

Sistema de analise automatica de atendimentos comerciais no WhatsApp.
Monitora conversas entre vendedores e leads, gera scores de qualidade com IA e envia relatorios diarios.

---

## 1. Pre-requisitos

- **Python 3.11+** (para rodar localmente)
- **Docker + Docker Compose** (para Evolution API e deploy)
- **Conta OpenAI** com API key (modelo gpt-4o-mini)
- **Celular com WhatsApp** (para conectar a instancia)

---

## 2. Instalacao Local

```bash
# Clonar o repositorio
git clone <url-do-repositorio> agente-comercial
cd agente-comercial

# Criar e ativar ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar variaveis de ambiente

Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
OPENAI_API_KEY=sk-sua-chave-openai-aqui
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=minha-chave-secreta-123
EVOLUTION_INSTANCE_NAME=agente-comercial
DATABASE_URL=sqlite:///data/agente_comercial.db
GESTOR_TELEFONE=5511999999999
HORARIO_RELATORIO=20:00
WEBHOOK_URL=http://host.docker.internal:8000/webhook/messages
```

---

## 3. Configuracao da Evolution API

A Evolution API conecta o sistema ao WhatsApp. Suba os servicos com Docker:

```bash
docker compose up -d evolution-api evolution-postgres evolution-redis
```

Aguarde ~30 segundos para todos os servicos iniciarem. Verifique:

```bash
curl http://localhost:8080
```

Deve retornar informacoes da API.

---

## 4. Configuracao do Webhook

O script automatizado cria a instancia WhatsApp e configura o webhook:

```bash
python scripts/setup_evolution.py
```

O script faz:
1. Verifica se a Evolution API esta online
2. Cria a instancia do WhatsApp
3. Configura o webhook para encaminhar mensagens ao FastAPI
4. Exibe o QR code para conexao

### Conectar o WhatsApp

1. Acesse `http://localhost:8080/instance/connect/agente-comercial` no navegador
2. Escaneie o QR code com o WhatsApp do vendedor
3. Aguarde a confirmacao de conexao

### Testar o webhook manualmente

```bash
curl -X POST http://localhost:8000/webhook/messages \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "agente-comercial",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "teste123"
      },
      "pushName": "Lead Teste",
      "message": {
        "conversation": "Ola, quero saber mais sobre o produto"
      },
      "messageTimestamp": 1700000000
    }
  }'
```

---

## 5. Cadastrar Vendedores

Cadastre vendedores via API. O telefone deve incluir codigo do pais (55) + DDD:

```bash
# Iniciar o FastAPI
uvicorn src.main:app --reload

# Em outro terminal, cadastrar vendedor
curl -X POST http://localhost:8000/vendedores \
  -H "Content-Type: application/json" \
  -d '{"nome": "Maria Silva", "telefone": "5511988887777"}'
```

**Importante:** O telefone cadastrado deve ser o mesmo numero conectado na Evolution API. O sistema identifica o vendedor pelo numero do remetente das mensagens.

---

## 6. Testar o Fluxo Completo

Com o FastAPI rodando e o WhatsApp conectado:

1. **Envie uma mensagem** de outro WhatsApp para o numero conectado
2. **Verifique o webhook** — a mensagem aparece nos logs do FastAPI
3. **Confira no banco** — acesse `http://localhost:8000/conversas` para ver a conversa criada
4. **Rode a analise** — chame o endpoint de analise:

```bash
# Substituir 1 pelo ID da conversa
curl -X POST http://localhost:8000/analisar/1
```

5. **Veja no dashboard** — inicie o Streamlit e confira:

```bash
streamlit run src/dashboard/app.py
```

Acesse `http://localhost:8501` no navegador.

---

## 7. Deploy com Docker

Para rodar tudo (API + Dashboard + Evolution API) em containers:

```bash
# Garantir que o .env esta configurado
# Subir todos os servicos
docker compose up --build -d
```

Servicos disponiveis:

| Servico | URL | Descricao |
|---------|-----|-----------|
| FastAPI | http://localhost:8000 | API REST |
| Dashboard | http://localhost:8501 | Interface Streamlit |
| Evolution API | http://localhost:8080 | Gateway WhatsApp |

### Verificar se tudo esta rodando

```bash
# Status dos containers
docker compose ps

# Testar API
curl http://localhost:8000/health

# Logs do agente
docker compose logs -f agente-comercial
```

### Dados persistentes

O banco SQLite fica em `./data/agente_comercial.db`, montado como volume Docker. Os dados sobrevivem a restarts e rebuilds dos containers.

---

## 8. Personalizar Prompt da IA

O system prompt que a IA usa para analisar conversas pode ser editado pelo gestor:

1. Acesse o Dashboard em `http://localhost:8501`
2. No menu lateral, clique em **Configuracoes**
3. Edite o texto do prompt no campo de texto
4. Clique **Salvar**

O novo prompt e aplicado imediatamente nas proximas analises.

Para voltar ao prompt original, clique **Restaurar Padrao**.

**Dicas para customizar o prompt:**
- Mantenha a instrucao de retornar JSON com os campos obrigatorios (score_qualidade, classificacao, erros, sentimento_lead, feedback_ia)
- Ajuste os criterios de avaliacao para seu segmento (ex: adicionar criterios especificos do seu produto)
- Modifique os tipos de erros para refletir os problemas mais comuns da sua equipe

---

## 9. Agendamento do Relatorio Diario

O sistema envia automaticamente um relatorio diario via WhatsApp para o gestor.

### Configurar

No `.env`, defina:

```env
# Numero do gestor (com codigo do pais)
GESTOR_TELEFONE=5511999999999

# Horario do relatorio (formato HH:MM)
HORARIO_RELATORIO=20:00
```

O scheduler roda automaticamente quando o FastAPI inicia. O relatorio inclui:
- Resumo geral do dia (total atendimentos, score medio, conversoes)
- Metricas individuais por vendedor
- Alertas automaticos (vendedores com score baixo, sem resposta, etc.)

### Enviar manualmente

Para enviar o relatorio a qualquer momento:

```bash
# Relatorio de hoje
curl -X POST http://localhost:8000/relatorio/enviar

# Relatorio de data especifica
curl -X POST "http://localhost:8000/relatorio/enviar?data=2025-01-15"
```

---

## 10. Troubleshooting

### Evolution API nao inicia

```
[ERRO] Evolution API nao esta rodando!
```

- Verifique se Docker esta rodando: `docker compose ps`
- Confira os logs: `docker compose logs evolution-api`
- O PostgreSQL pode demorar para iniciar na primeira vez. Aguarde 30s e tente novamente

### Webhook nao recebe mensagens

- Confirme que o FastAPI esta rodando na porta 8000
- Verifique o WEBHOOK_URL no `.env` — dentro do Docker use `http://host.docker.internal:8000/webhook/messages`
- Rode o setup novamente: `python scripts/setup_evolution.py`
- Confira se o WhatsApp esta conectado: acesse `http://localhost:8080/instance/connectionState/agente-comercial`

### QR code nao aparece

- A instancia pode ja estar conectada. Verifique o status da conexao
- Tente desconectar e reconectar: acesse `http://localhost:8080/instance/connect/agente-comercial`

### Erro na analise com OpenAI

```
Falha ao chamar OpenAI: ...
```

- Verifique se `OPENAI_API_KEY` esta correta no `.env`
- Confirme que a chave tem creditos disponiveis
- O modelo `gpt-4o-mini` deve estar disponivel na sua conta

### Dashboard nao carrega dados

- Verifique se existem metricas calculadas para a data selecionada
- Rode o calculo de metricas: `curl -X POST "http://localhost:8000/metricas/calcular?data=2025-01-15"`
- Confirme que o banco `data/agente_comercial.db` existe e nao esta corrompido

### Container do Agente nao inicia

```bash
# Ver logs detalhados
docker compose logs agente-comercial

# Reconstruir imagem
docker compose build --no-cache agente-comercial
docker compose up -d agente-comercial
```

- Confirme que o `.env` existe na raiz do projeto
- Verifique se a pasta `data/` existe: `mkdir -p data`
