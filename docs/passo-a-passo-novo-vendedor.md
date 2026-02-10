# Como Adicionar um Novo Vendedor

Guia completo para adicionar um vendedor com WhatsApp monitorado na plataforma.

## Pre-requisitos

- Acesso ao Dashboard: `https://app.reaumarketing.com/?token=SEU_TOKEN`
- WhatsApp do vendedor disponivel para escanear QR Code
- Evolution API e chave configuradas (aba Configuracoes > Evolution API)
- Variaveis de ambiente no Easypanel:
  - `WEBHOOK_URL=https://api.reaumarketing.com/webhook/messages`
  - `WEBHOOK_SECRET=<apikey do Evolution>`

## Passo 1: Cadastrar o Vendedor

1. Acesse **Vendedores** no menu lateral
2. Abra o expander **"Cadastrar Novo Vendedor"**
3. Preencha:
   - **Nome**: nome do vendedor (ex: "Eduarda")
   - **Telefone**: numero com DDI+DDD (ex: `554991397222`)
4. Clique **"Cadastrar Vendedor"**

> O formato do telefone nao precisa ser exato. O sistema compara os
> ultimos 8 digitos, entao tanto `554991125253` quanto `5549991125253`
> funcionam para o mesmo numero.

> Se o vendedor ja existiu e foi removido anteriormente, o sistema
> reativa o cadastro antigo automaticamente, preservando o historico.

## Passo 2: Registrar a Instancia WhatsApp

1. Acesse **Configuracoes** no menu lateral
2. Va para a aba **"Instancias WhatsApp"**
3. Na secao **"Adicionar Instancia"**, ha duas opcoes:

### Opcao A: Vincular instancia existente (recomendado)

Se a instancia ja foi criada no Evolution (via Manager ou anteriormente):
1. O sistema mostra um **dropdown** com as instancias do Evolution nao registradas
2. Selecione a instancia desejada
3. Clique **"Adicionar e Configurar Webhook"**

> O nome e preenchido automaticamente a partir do Evolution, eliminando
> erros de digitacao.

### Opcao B: Criar nova instancia

Se precisa criar uma instancia do zero:
1. Abra o expander **"Criar nova instancia no Evolution"**
2. Informe o nome da instancia
3. Clique **"Criar Instancia"**

O sistema ira automaticamente:
- Criar a instancia na Evolution API
- Configurar o webhook para receber mensagens
- Mostrar o QR Code para conexao

## Passo 3: Conectar o WhatsApp

1. Na instancia criada/registrada, clique o botao **"QR Code"**
2. No celular do vendedor, abra **WhatsApp > Dispositivos conectados > Conectar dispositivo**
3. Escaneie o QR Code exibido
4. Aguarde a conexao ser confirmada

> Se o QR Code expirar, clique **"QR Code"** novamente para gerar um novo.

## Passo 4: Verificar

1. Na aba **Instancias WhatsApp**, clique **"Status"** na instancia
2. Deve aparecer **"Conectada (open)"**
3. Envie uma mensagem de teste para o WhatsApp do vendedor
4. Verifique se a conversa aparece em **Conversas** no dashboard

## Gerenciar Instancias

Cada instancia registrada tem os seguintes botoes:

| Botao | Funcao |
|-------|--------|
| **Status** | Verifica se a instancia esta conectada |
| **QR Code** | Gera QR Code para conectar/reconectar |
| **Webhook** | (Re)configura o webhook automaticamente |
| **Salvar alteracoes** | Atualiza nome ou telefone da instancia |
| **Remover instancia** | Remove do Evolution e do banco |

## Remover um Vendedor

1. Acesse **Vendedores** no menu lateral
2. Abra o expander **"Gerenciar Vendedores"**
3. Clique **"Remover"** ao lado do vendedor
4. O vendedor sera desativado (historico de conversas e metricas preservado)

> Se precisar recadastrar o mesmo numero depois, basta criar novamente —
> o sistema reativa o vendedor antigo automaticamente.

## Solucao de Problemas

### Mensagens nao aparecem no dashboard

1. Verifique se o **Status** da instancia esta "open"
2. Clique o botao **"Webhook"** para (re)configurar
3. Verifique se `WEBHOOK_URL` e `WEBHOOK_SECRET` estao corretos no Easypanel
4. Tente desconectar e reconectar a instancia (logout + QR Code)

### Mensagens aparecem no vendedor errado

- Historico: o sistema ja compara os ultimos 8 digitos do telefone,
  entao o formato com ou sem 9o digito funciona automaticamente
- Se persistir, verifique se o telefone do vendedor esta cadastrado
  corretamente em **Vendedores > Gerenciar Vendedores**

### Erro "already in use" ao criar instancia

- A instancia ja existe no Evolution. Use a **Opcao A** (dropdown)
  para vincular a instancia existente

### QR Code nao aparece

- Verifique se a Evolution API esta configurada (aba Evolution API > Testar Conexao)
- Tente usar o botao **"QR Code"** na instancia existente

### Erro ao cadastrar vendedor com mesmo telefone

- O sistema automaticamente reativa vendedores inativos com o mesmo
  numero. Se der erro, verifique se ja existe um vendedor ativo com
  esse telefone
