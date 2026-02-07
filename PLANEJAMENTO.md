# Agente Comercial - Planejamento do Projeto

## Visao Geral

Sistema de IA que analisa atendimentos de vendedores no WhatsApp e gera
feedback automatizado para gestores, funcionando como um "gestor comercial virtual".

---

## Stack Tecnologica

| Camada           | Tecnologia         | Motivo                                    |
|------------------|--------------------|--------------------------------------------|
| Linguagem        | Python 3.11+       | Melhor para IA, dados e iniciantes         |
| WhatsApp         | Evolution API v2   | Open source, gratuita, self-hosted         |
| LLM              | OpenAI GPT-4o-mini | Custo-beneficio, bom em PT-BR              |
| Banco de Dados   | SQLite (inicio)    | Zero config, migra para PostgreSQL depois  |
| API Framework    | FastAPI            | Moderno, rapido, facil de aprender         |
| Dashboard        | Streamlit          | Dashboard em Python puro, ideal p/ inicio  |
| Agendamento      | APScheduler        | Jobs agendados (relatorios diarios)        |

---

## Arquitetura do Sistema

```
┌─────────────────┐     Webhook      ┌──────────────────┐
│  Evolution API  │ ────────────────► │   FastAPI         │
│  (WhatsApp)     │                   │   (Receptor)      │
└─────────────────┘                   └────────┬─────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │   SQLite          │
                                      │   (Mensagens)     │
                                      └────────┬─────────┘
                                               │
                                      ┌────────▼─────────┐
                                      │   Processador     │
                                      │   de Metricas     │
                                      └────────┬─────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                     │  Analise IA  │ │  Metricas    │ │  Relatorio   │
                     │  (OpenAI)    │ │  Calculadas  │ │  Diario      │
                     └──────────────┘ └──────────────┘ └──────────────┘
                                               │
                                      ┌────────▼─────────┐
                                      │   Dashboard       │
                                      │   (Streamlit)     │
                                      └──────────────────┘
```

---

## Metricas a Serem Rastreadas

### Metricas de Velocidade
- **Tempo de primeira resposta**: Quanto tempo o vendedor leva para responder o primeiro contato
- **Tempo medio de resposta**: Media entre mensagens durante a conversa
- **Horario de atendimento**: Se o vendedor responde fora do horario

### Metricas de Qualificacao
- **Taxa de qualificacao**: % de leads que sao qualificados corretamente
- **MQL (Marketing Qualified Lead)**: Leads que demonstram interesse inicial
- **SQL (Sales Qualified Lead)**: Leads prontos para compra
- **Taxa MQL → SQL**: Conversao de interesse para oportunidade real

### Metricas de Conversao
- **Taxa de conversao geral**: % de conversas que viram venda
- **Taxa de conversao por vendedor**: Comparativo entre vendedores
- **Funil de vendas**: Distribuicao dos leads por etapa

### Metricas de Qualidade
- **Score de atendimento**: Nota da IA sobre qualidade da conversa
- **Erros identificados**: Padrao de erros cometidos pelo vendedor
- **Uso de script/metodologia**: Se segue o processo de vendas definido
- **Sentimento do lead**: Analise de sentimento das respostas do lead

### Metricas de Volume
- **Atendimentos por dia/vendedor**: Quantidade de conversas
- **Mensagens por atendimento**: Volume de interacao
- **Leads sem resposta**: Leads ignorados ou esquecidos

---

## Fases de Desenvolvimento

### FASE 1 - Fundacao (Semana 1-2)
**Objetivo**: Ambiente configurado + captura de mensagens funcionando

- [ ] Configurar ambiente Python (venv, dependencias)
- [ ] Instalar e configurar Evolution API local (Docker)
- [ ] Criar servidor FastAPI basico
- [ ] Configurar webhook para receber mensagens
- [ ] Criar banco de dados SQLite com schema inicial
- [ ] Armazenar mensagens recebidas no banco
- [ ] Identificar e separar conversas por vendedor e lead

**Entregavel**: Sistema capturando e armazenando todas as mensagens do WhatsApp

---

### FASE 2 - Analise com IA (Semana 3-4)
**Objetivo**: IA analisando conversas e extraindo informacoes

- [ ] Configurar OpenAI API
- [ ] Criar prompts para classificacao de leads (MQL/SQL)
- [ ] Criar prompts para analise de qualidade do atendimento
- [ ] Criar prompts para identificacao de erros do vendedor
- [ ] Implementar analise de sentimento
- [ ] Criar sistema de scores por atendimento
- [ ] Pipeline de processamento: conversa → analise → resultado

**Entregavel**: Cada conversa analisada automaticamente com score e classificacao

---

### FASE 3 - Motor de Metricas (Semana 5-6)
**Objetivo**: Calcular todos os KPIs a partir dos dados coletados

- [ ] Calcular tempo de primeira resposta
- [ ] Calcular tempo medio de resposta
- [ ] Implementar classificacao do funil (lead → MQL → SQL → cliente)
- [ ] Calcular taxas de conversao por vendedor
- [ ] Identificar leads sem resposta
- [ ] Criar rankings de vendedores
- [ ] Armazenar metricas historicas

**Entregavel**: Todas as metricas calculadas e disponíveis para consulta

---

### FASE 4 - Relatorio Diario (Semana 7-8)
**Objetivo**: Relatorio automatico enviado ao gestor todo dia

- [ ] Definir template do relatorio diario
- [ ] Criar job agendado (APScheduler) para executar todo dia as 20h
- [ ] Gerar relatorio consolidado com todas as metricas
- [ ] Gerar feedback individual por vendedor
- [ ] Enviar relatorio via WhatsApp para o gestor
- [ ] Incluir alertas (vendedor com performance baixa, lead sem resposta)

**Entregavel**: Gestor recebe relatorio completo todo dia no WhatsApp

---

### FASE 5 - Dashboard Web (Semana 9-10)
**Objetivo**: Interface visual para acompanhamento em tempo real

- [ ] Criar dashboard com Streamlit
- [ ] Visao geral: metricas do dia, semana, mes
- [ ] Visao por vendedor: metricas individuais
- [ ] Graficos de evolucao temporal
- [ ] Funil de vendas visual
- [ ] Ranking de vendedores
- [ ] Detalhes de conversas individuais

**Entregavel**: Dashboard web funcional com todas as metricas visuais

---

### FASE 6 - Refinamento (Semana 11-12+)
**Objetivo**: Polir, escalar e adicionar features avancadas

- [ ] Migrar SQLite para PostgreSQL
- [ ] Alertas em tempo real (vendedor demorou para responder)
- [ ] Comparativo semanal/mensal de evolucao
- [ ] Sugestoes de melhoria personalizadas por vendedor
- [ ] Integracao com CRM (se aplicavel)
- [ ] Deploy em VPS para uso em producao
- [ ] Sistema de metas e acompanhamento

**Entregavel**: Sistema robusto pronto para producao

---

## Estrutura de Pastas do Projeto

```
agente-comercial/
├── PLANEJAMENTO.md          # Este arquivo
├── README.md                # Documentacao do projeto
├── .env                     # Variaveis de ambiente (API keys)
├── .gitignore
├── requirements.txt         # Dependencias Python
│
├── src/                     # Codigo fonte principal
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada FastAPI
│   ├── config.py            # Configuracoes
│   │
│   ├── whatsapp/            # Integracao WhatsApp
│   │   ├── __init__.py
│   │   ├── webhook.py       # Receptor de webhooks
│   │   ├── sender.py        # Envio de mensagens
│   │   └── parser.py        # Parser de mensagens
│   │
│   ├── database/            # Banco de dados
│   │   ├── __init__.py
│   │   ├── models.py        # Modelos/tabelas
│   │   ├── connection.py    # Conexao com banco
│   │   └── queries.py       # Consultas
│   │
│   ├── analysis/            # Analise com IA
│   │   ├── __init__.py
│   │   ├── analyzer.py      # Analisador principal
│   │   ├── prompts.py       # Prompts para OpenAI
│   │   ├── classifier.py    # Classificacao de leads
│   │   └── sentiment.py     # Analise de sentimento
│   │
│   ├── metrics/             # Motor de metricas
│   │   ├── __init__.py
│   │   ├── calculator.py    # Calculo de metricas
│   │   ├── response_time.py # Tempo de resposta
│   │   ├── conversion.py    # Taxas de conversao
│   │   └── scoring.py       # Sistema de pontuacao
│   │
│   ├── reports/             # Geracao de relatorios
│   │   ├── __init__.py
│   │   ├── daily.py         # Relatorio diario
│   │   ├── templates.py     # Templates de mensagem
│   │   └── scheduler.py     # Agendamento
│   │
│   └── dashboard/           # Dashboard web
│       ├── __init__.py
│       └── app.py           # Streamlit app
│
├── tests/                   # Testes
│   ├── __init__.py
│   ├── test_webhook.py
│   ├── test_analyzer.py
│   └── test_metrics.py
│
└── data/                    # Dados locais
    └── agente_comercial.db  # Banco SQLite
```

---

## Modelo do Banco de Dados (Inicial)

### Tabela: vendedores
| Campo       | Tipo    | Descricao                    |
|-------------|---------|------------------------------|
| id          | INTEGER | ID unico                     |
| nome        | TEXT    | Nome do vendedor             |
| telefone    | TEXT    | Numero WhatsApp              |
| ativo       | BOOLEAN | Se esta ativo                |
| criado_em   | DATETIME| Data de cadastro             |

### Tabela: conversas
| Campo          | Tipo    | Descricao                     |
|----------------|---------|-------------------------------|
| id             | INTEGER | ID unico                      |
| vendedor_id    | INTEGER | FK para vendedores            |
| lead_telefone  | TEXT    | Telefone do lead              |
| lead_nome      | TEXT    | Nome do lead (se disponivel)  |
| status         | TEXT    | novo/mql/sql/cliente/perdido  |
| iniciada_em    | DATETIME| Quando comecou               |
| atualizada_em  | DATETIME| Ultima mensagem              |

### Tabela: mensagens
| Campo        | Tipo    | Descricao                      |
|--------------|---------|--------------------------------|
| id           | INTEGER | ID unico                       |
| conversa_id  | INTEGER | FK para conversas              |
| remetente    | TEXT    | vendedor ou lead               |
| conteudo     | TEXT    | Texto da mensagem              |
| tipo         | TEXT    | texto/audio/imagem             |
| enviada_em   | DATETIME| Timestamp da mensagem         |

### Tabela: analises
| Campo            | Tipo    | Descricao                     |
|------------------|---------|-------------------------------|
| id               | INTEGER | ID unico                      |
| conversa_id      | INTEGER | FK para conversas             |
| score_qualidade  | FLOAT   | 0-10 qualidade atendimento    |
| classificacao    | TEXT    | mql/sql/nao_qualificado       |
| erros            | TEXT    | JSON com erros identificados  |
| sentimento_lead  | TEXT    | positivo/neutro/negativo      |
| feedback_ia      | TEXT    | Feedback gerado pela IA       |
| analisada_em     | DATETIME| Quando foi analisada         |

### Tabela: metricas_diarias
| Campo                    | Tipo    | Descricao                   |
|--------------------------|---------|------------------------------|
| id                       | INTEGER | ID unico                     |
| vendedor_id              | INTEGER | FK para vendedores           |
| data                     | DATE    | Dia da metrica               |
| total_atendimentos       | INTEGER | Conversas no dia             |
| tempo_medio_resposta_seg | INTEGER | Em segundos                  |
| tempo_primeira_resp_seg  | INTEGER | Em segundos                  |
| total_mql                | INTEGER | Leads qualificados marketing |
| total_sql                | INTEGER | Leads qualificados vendas    |
| total_conversoes         | INTEGER | Vendas fechadas              |
| score_medio              | FLOAT   | Media de qualidade           |
| leads_sem_resposta       | INTEGER | Leads ignorados              |

---

## Prerequisitos para Comecar

1. **Python 3.11+** instalado
2. **Docker Desktop** instalado (para Evolution API)
3. **Conta OpenAI** com creditos (API key)
4. **Celular com WhatsApp** para conectar na Evolution API
5. **Editor de codigo** (VS Code recomendado)

---

## Proximo Passo

Comecar pela **FASE 1**: Configurar ambiente e capturar mensagens do WhatsApp.
