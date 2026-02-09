# Agente Comercial - Contexto do Projeto

## O que é
Sistema de análise de atendimentos comerciais no WhatsApp. Monitora conversas de vendedores, analisa qualidade com IA (OpenAI), gera métricas/KPIs e envia relatórios diários via WhatsApp.

## Stack
- **Backend:** Python 3.11+, FastAPI (porta 8000)
- **Dashboard:** Streamlit (porta 8501), 7 páginas
- **Banco:** PostgreSQL (SQLAlchemy ORM)
- **WhatsApp:** Evolution API v2 (webhooks)
- **IA:** OpenAI gpt-4o-mini (prompt customizável por empresa)
- **Deploy:** Docker, Easypanel (Hostinger VPS)

## Arquitetura Multi-Tenant
- Isolamento por `empresa_id` em todas as queries
- Auth via token na URL: `?token=uuid` (sem login/senha)
- Webhook routing: `instance_name` → `InstanciaEvolution` → `empresa_id` → `Vendedor`
- Config cascade: empresa DB → global DB → .env → default
- Admin protegido por `admin_key` (separado do token empresa)

## Produção
- **Dashboard:** https://app.reaumarketing.com (porta 8501)
- **API:** https://api.reaumarketing.com (porta 8000)
- **Evolution API:** https://evo.reaumarketing.com
- **Easypanel:** https://easypanel.reaumarketing.com
- **Domínios:** Internal Protocol = HTTP (Traefik faz TLS)
- **Deploy:** push para GitHub → deploy manual no Easypanel

## Estrutura de Arquivos
```
src/
├── main.py                    # FastAPI app, endpoints admin
├── config.py                  # Settings (pydantic)
├── config_manager.py          # get_config(chave, empresa_id)
├── database/
│   ├── connection.py          # Engine, SessionLocal, pool config
│   ├── models.py              # 9 modelos SQLAlchemy
│   └── queries.py             # Todas queries com empresa_id
├── whatsapp/
│   ├── webhook.py             # POST /webhook/messages
│   ├── parser.py              # Parseia payload Evolution API
│   └── sender.py              # Envia mensagem via Evolution API
├── analysis/
│   ├── analyzer.py            # OpenAI analysis
│   └── router.py              # POST /analisar/{conversa_id}
├── metrics/
│   └── router.py              # 4 endpoints de métricas
├── reports/
│   ├── templates.py           # Templates do relatório WhatsApp
│   ├── scheduler.py           # APScheduler (1 job/empresa, TZ São Paulo)
│   └── router.py              # POST /relatorio/enviar
└── dashboard/
    ├── Home.py                # Página inicial Streamlit
    ├── utils.py               # validar_token_empresa(), get_db()
    ├── theme.py               # Tema visual
    └── pages/                 # 7 páginas do dashboard
```

## Convenções
- Queries sempre filtram por `empresa_id`
- Configurações: DB tem prioridade sobre .env
- Scheduler usa timezone `America/Sao_Paulo`
- Webhook requer header `apikey` matching `WEBHOOK_SECRET`
- Evolution API: POST /webhook/set/{name} com body `{"webhook": {...}}`
