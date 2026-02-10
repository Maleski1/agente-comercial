# Como Adicionar um Novo Vendedor

Guia completo para adicionar um vendedor com WhatsApp monitorado na plataforma.

## Pre-requisitos

- Acesso ao Dashboard: `https://app.reaumarketing.com/?token=SEU_TOKEN`
- WhatsApp do vendedor disponivel para escanear QR Code
- Evolution API e chave configuradas (aba Configuracoes > Evolution API)

## Passo 1: Cadastrar o Vendedor

1. Acesse **Vendedores** no menu lateral
2. Abra o expander **"Cadastrar Novo Vendedor"**
3. Preencha:
   - **Nome**: nome do vendedor (ex: "Eduarda")
   - **Telefone**: numero completo com DDI+DDD (ex: `554991397222`)
4. Clique **"Cadastrar Vendedor"**

> O telefone deve ser exatamente o numero do WhatsApp que sera conectado, sem espacos ou caracteres especiais.

## Passo 2: Criar a Instancia WhatsApp

1. Acesse **Configuracoes** no menu lateral
2. Va para a aba **"Instancias WhatsApp"**
3. Role ate **"Adicionar Instancia"**
4. Preencha:
   - **Nome da instancia**: nome que identifica essa conexao (ex: "Eduarda ReAu")
   - **Telefone**: mesmo numero do vendedor (ex: `554991397222`)
5. Clique **"Criar Instancia"**

O sistema ira automaticamente:
- Criar a instancia na Evolution API
- Configurar o webhook para receber mensagens
- Mostrar o QR Code para conexao

## Passo 3: Conectar o WhatsApp

1. Apos clicar "Criar Instancia", um **QR Code** aparecera na tela
2. No celular do vendedor, abra **WhatsApp > Dispositivos conectados > Conectar dispositivo**
3. Escaneie o QR Code exibido
4. Aguarde a conexao ser confirmada

> Se o QR Code expirar, use o botao **"QR Code"** na instancia para gerar um novo.

## Passo 4: Verificar

1. Na aba **Instancias WhatsApp**, clique **"Status"** na instancia criada
2. Deve aparecer **"Conectada (open)"**
3. Envie uma mensagem de teste para o WhatsApp do vendedor
4. Verifique se a conversa aparece em **Conversas** no dashboard

## Solucao de Problemas

### Instancia criada mas webhook nao funciona
- Va em **Configuracoes > Instancias WhatsApp**
- Clique no botao **"Webhook"** da instancia
- Isso reconfigura o webhook automaticamente

### Mensagens nao aparecem no dashboard
1. Verifique se o **Status** da instancia esta "open"
2. Verifique se o **nome da instancia** no dashboard eh identico ao nome no Evolution
3. Use o botao **"Webhook"** para reconfigurar

### QR Code nao aparece
- Verifique se a Evolution API esta configurada (aba Evolution API > Testar Conexao)
- Tente usar o botao **"QR Code"** na instancia existente

## Remover um Vendedor

1. Acesse **Vendedores** no menu lateral
2. Abra o expander **"Gerenciar Vendedores"**
3. Clique **"Remover"** ao lado do vendedor
4. O vendedor sera desativado (historico preservado)
