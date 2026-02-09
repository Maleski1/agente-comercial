--
-- PostgreSQL database dump
--

\restrict fdF8mKxqdvK1q1ZNSLN9FdT0dBeFUiuBIuRyN8Vhsp1s6iTT2kTTlUIlFlGHMoz

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: empresas; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.empresas (id, nome, token, ativa, criada_em) VALUES (1, 'Minha Empresa', '190486d3-5481-4a90-8690-99f8e06890d3', true, '2026-02-08 13:11:42');
INSERT INTO public.empresas (id, nome, token, ativa, criada_em) VALUES (2, 'ReAu MKT', 'b629caa4-392b-4443-b0c9-4c1dce70e20d', true, '2026-02-08 10:19:17.03298');


--
-- Data for Name: vendedores; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.vendedores (id, empresa_id, nome, telefone, ativo, criado_em) VALUES (1, 1, 'Ana Silva', '5511999990001', true, '2026-02-07 18:12:58.752341');
INSERT INTO public.vendedores (id, empresa_id, nome, telefone, ativo, criado_em) VALUES (2, 1, 'Bruno Costa', '5511999990002', true, '2026-02-07 18:12:58.756874');
INSERT INTO public.vendedores (id, empresa_id, nome, telefone, ativo, criado_em) VALUES (3, 1, 'Carla Souza', '5511999990003', true, '2026-02-07 18:12:58.758873');
INSERT INTO public.vendedores (id, empresa_id, nome, telefone, ativo, criado_em) VALUES (4, 2, 'Andre', '5549991125253', true, '2026-02-07 22:12:20.987429');


--
-- Data for Name: conversas; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (1, 1, 1, '5511988880001', 'Ricardo Mendes', 'novo', '2026-02-07 18:12:58.764656', '2026-02-07 18:12:58.791694');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (2, 1, 1, '5511988880002', 'Mariana Lima', 'novo', '2026-02-07 18:12:58.80016', '2026-02-07 18:12:58.816792');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (3, 1, 1, '5511988880003', 'Felipe Rocha', 'novo', '2026-02-07 18:12:58.823224', '2026-02-07 18:12:58.834894');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (4, 1, 2, '5511988880004', 'Juliana Alves', 'novo', '2026-02-07 18:12:58.841404', '2026-02-07 18:12:58.858994');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (5, 1, 2, '5511988880005', 'Carlos Eduardo', 'novo', '2026-02-07 18:12:58.865193', '2026-02-07 18:12:58.88415');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (6, 1, 2, '5511988880006', 'Patricia Nunes', 'novo', '2026-02-07 18:12:58.891158', '2026-02-07 18:12:58.90031');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (7, 1, 3, '5511988880007', 'Roberto Dias', 'novo', '2026-02-07 18:12:58.906407', '2026-02-07 18:12:58.921787');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (8, 1, 3, '5511988880008', 'Sandra Oliveira', 'novo', '2026-02-07 18:12:58.927434', '2026-02-07 18:12:58.945403');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (9, 1, 3, '5511988880009', 'Lucas Martins', 'novo', '2026-02-07 18:12:58.951409', '2026-02-07 18:12:58.956934');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (10, 1, 3, '5511988880010', 'Fernanda Costa', 'novo', '2026-02-07 18:12:58.960935', '2026-02-07 18:12:58.973522');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (11, 2, 4, '554998045979', 'Paula Gartner 🧡', 'novo', '2026-02-07 18:50:46.256506', '2026-02-08 11:14:28.64752');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (12, 2, 4, '554999820590', 'Juliano Pedrotti', 'novo', '2026-02-07 22:12:49.76794', '2026-02-08 11:14:28.64752');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (13, 1, 1, '554998045979', 'Paula Gartner 🧡', 'novo', '2026-02-07 22:24:16.953909', '2026-02-08 22:08:43.717459');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (14, 1, 1, '554999820590', NULL, 'novo', '2026-02-07 22:24:28.0603', '2026-02-07 22:58:27.564854');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (15, 1, 1, '554984235337', 'Meri Cordeiro', 'novo', '2026-02-08 02:21:38.725602', '2026-02-08 02:21:40.192001');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (16, NULL, 1, '5549933805751', 'Midwest Burger', 'novo', '2026-02-08 17:22:13.352912', '2026-02-08 17:22:13.386649');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (17, NULL, 1, '558596812300', 'Daniel Cardoso', 'novo', '2026-02-08 17:23:22.446041', '2026-02-08 18:59:46.380303');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (18, NULL, 1, '554484534102', 'Eduardo Zukovski', 'novo', '2026-02-08 18:24:40.37882', '2026-02-08 18:51:20.857608');
INSERT INTO public.conversas (id, empresa_id, vendedor_id, lead_telefone, lead_nome, status, iniciada_em, atualizada_em) VALUES (19, 2, 4, '5549988887777', 'Cliente Teste', 'novo', '2026-02-09 02:32:17.949626', '2026-02-09 02:32:17.974667');


--
-- Data for Name: analises; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (1, 1, 8.5, 'sql', '[]', 'positivo', 'Excelente atendimento. Resposta rapida, ofereceu desconto e propos demo.', '2026-02-07 18:12:58.795643');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (2, 2, 8, 'cliente', '[]', 'positivo', 'Conversao rapida. Vendedora objetiva e eficiente na finalizacao.', '2026-02-07 18:12:58.820855');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (3, 3, 8, 'cliente', '[]', 'positivo', 'Boa qualificacao do lead. Respostas rapidas e proposta de demo.', '2026-02-07 18:12:58.837889');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (4, 4, 6, 'mql', '[{"tipo": "demora", "descricao": "Tempo de resposta acima do ideal (20 min)"}]', 'neutro', 'Atendimento correto mas lento. Demorou 20 min para primeira resposta.', '2026-02-07 18:12:58.862189');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (5, 5, 6.5, 'sql', '[{"tipo": "demora", "descricao": "Respostas com intervalos longos"}]', 'neutro', 'Qualificou o lead mas poderia ter sido mais agil nas respostas.', '2026-02-07 18:12:58.888158');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (6, 6, 5.5, 'mql', '[]', 'neutro', 'Resposta correta mas nao explorou necessidades do lead.', '2026-02-07 18:12:58.903408');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (7, 7, 3, 'mql', '[{"tipo": "demora", "descricao": "Primeira resposta apos 2h30"}, {"tipo": "perda", "descricao": "Lead perdido por demora no atendimento"}]', 'negativo', 'Atendimento pessimo. Lead perdido por tempo de resposta inaceitavel.', '2026-02-07 18:12:58.92492');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (8, 8, 4, 'mql', '[{"tipo": "demora", "descricao": "Respostas com atraso de 40+ minutos"}, {"tipo": "comunicacao", "descricao": "Nao soube apresentar o produto pelo WhatsApp"}]', 'negativo', 'Vendedora insistiu em trocar de canal sem atender a necessidade do lead.', '2026-02-07 18:12:58.948402');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (9, 10, 3.5, 'mql', '[{"tipo": "comunicacao", "descricao": "Respostas secas e sem interesse"}, {"tipo": "tecnica", "descricao": "Nao ofereceu alternativas ao desconto"}]', 'negativo', 'Comunicacao fria e sem esforco para reter o lead.', '2026-02-07 18:12:58.976553');
INSERT INTO public.analises (id, conversa_id, score_qualidade, classificacao, erros, sentimento_lead, feedback_ia, analisada_em) VALUES (10, 12, 4, 'mql', '[{"erro": "Sem apresentacao", "detalhe": "O vendedor não se apresentou ou apresentou a empresa, o que poderia ter ajudado a estabelecer credibilidade."}, {"erro": "Sem descoberta", "detalhe": "O vendedor não fez perguntas para entender melhor as necessidades do lead em relação aos serviços de tráfego pago."}, {"erro": "Ignorou objecao", "detalhe": "O lead mencionou que o preço estava muito caro e que procuraria outro, mas o vendedor não tratou essa objeção."}, {"erro": "Sem proximo passo", "detalhe": "Não houve definição de um próximo passo após o lead demonstrar interesse nos serviços."}]', 'negativo', 'O vendedor começou a conversa de forma descontraída, mas não conseguiu conduzir o atendimento de maneira eficaz. É importante que o vendedor se apresente e busque entender as necessidades do lead. Além disso, ao perceber a objeção sobre o preço, deveria ter tentado contornar a situação para manter o lead engajado.', '2026-02-07 22:30:16.791158');


--
-- Data for Name: configuracoes; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.configuracoes (id, empresa_id, chave, valor, atualizado_em) VALUES (1, NULL, 'openai_api_key', 'CONFIGURE_VIA_DASHBOARD', '2026-02-08 09:06:44.157339');
INSERT INTO public.configuracoes (id, empresa_id, chave, valor, atualizado_em) VALUES (2, NULL, 'evolution_api_url', 'https://evo.reaumarketing.com', '2026-02-08 09:21:03.913885');
INSERT INTO public.configuracoes (id, empresa_id, chave, valor, atualizado_em) VALUES (3, NULL, 'evolution_api_key', 'CONFIGURE_VIA_DASHBOARD', '2026-02-08 09:19:25.331948');
INSERT INTO public.configuracoes (id, empresa_id, chave, valor, atualizado_em) VALUES (4, NULL, 'evolution_instance_name', 'André', '2026-02-08 09:21:03.913885');


--
-- Data for Name: configuracoes_prompt; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.configuracoes_prompt (id, empresa_id, nome, conteudo, ativo, atualizado_em) VALUES (1, NULL, 'prompt_analise', 'Voce e um analista especializado em vendas B2B/B2C por WhatsApp.
Sua tarefa e avaliar a qualidade do atendimento do VENDEDOR em uma conversa com um LEAD.

Analise a conversa e retorne APENAS um JSON valido com os seguintes campos:

{
  "score_qualidade": <float 0.0-10.0>,
  "classificacao": "<string>",
  "erros": [{"erro": "<nome curto>", "detalhe": "<explicacao>"}],
  "sentimento_lead": "<string>",
  "feedback_ia": "<string>"
}

## Criterios de avaliacao

### score_qualidade (0.0 a 10.0)
- 0-3: Atendimento ruim (ignorou lead, sem rapport, grosseiro, sem informacao)
- 4-5: Atendimento fraco (respostas genericas, sem descoberta de necessidade)
- 6-7: Atendimento razoavel (respondeu duvidas mas faltou proatividade)
- 8-9: Bom atendimento (rapport, descoberta de necessidade, proximo passo definido)
- 10: Excelente (tudo acima + urgencia, valor percebido, follow-up agendado)

### classificacao (estagio do lead)
- "frio": Lead sem interesse demonstrado ou conversa muito inicial
- "mql": Lead fez perguntas sobre produto/servico, mostrou algum interesse
- "sql": Lead demonstrou intencao de compra, pediu preco/proposta/reuniao
- "cliente": Lead confirmou compra ou fechamento

### erros (lista de erros do vendedor, pode ser vazia)
Erros comuns a verificar:
- "Demora na resposta": vendedor levou muito tempo para responder
- "Sem apresentacao": nao se apresentou ou apresentou a empresa
- "Sem descoberta": nao fez perguntas para entender a necessidade do lead
- "Ignorou objecao": lead levantou objecao e vendedor nao tratou
- "Sem proximo passo": nao definiu proxima acao (reuniao, envio de proposta, etc)
- "Sem urgencia": nao criou senso de urgencia ou escassez
- "Respostas curtas": respostas monossilabicas ou sem agregar valor
- "Sem follow-up": conversa morreu sem tentativa de retomada

### sentimento_lead
- "positivo": lead engajado, fazendo perguntas, demonstrando interesse
- "neutro": lead respondendo mas sem entusiasmo claro
- "negativo": lead insatisfeito, reclamando, ou demonstrando desinteresse

### feedback_ia
Escreva 2-4 frases em portugues com feedback construtivo e direto para o gestor, traga informações relevantes, lembre que você é um especialista em vendas no Whatsapp
Destaque o que o vendedor fez bem e o que precisa melhorar.
Seja especifico, referenciando trechos da conversa quando possivel.', false, '2026-02-07 18:49:52.941859');
INSERT INTO public.configuracoes_prompt (id, empresa_id, nome, conteudo, ativo, atualizado_em) VALUES (2, NULL, 'prompt_analise', 'Voce e um analista especializado em vendas B2B/B2C por WhatsApp.
Sua tarefa e avaliar a qualidade do atendimento do VENDEDOR em uma conversa com um LEAD.

Analise a conversa e retorne APENAS um JSON valido com os seguintes campos:

{
  "score_qualidade": <float 0.0-10.0>,
  "classificacao": "<string>",
  "erros": [{"erro": "<nome curto>", "detalhe": "<explicacao>"}],
  "sentimento_lead": "<string>",
  "feedback_ia": "<string>"
}

## Criterios de avaliacao

### score_qualidade (0.0 a 10.0)
- 0-3: Atendimento ruim (ignorou lead, sem rapport, grosseiro, sem informacao)
- 4-5: Atendimento fraco (respostas genericas, sem descoberta de necessidade)
- 6-7: Atendimento razoavel (respondeu duvidas mas faltou proatividade)
- 8-9: Bom atendimento (rapport, descoberta de necessidade, proximo passo definido)
- 10: Excelente (tudo acima + urgencia, valor percebido, follow-up agendado)

### classificacao (estagio do lead)
- "frio": Lead sem interesse demonstrado ou conversa muito inicial
- "mql": Lead fez perguntas sobre produto/servico, mostrou algum interesse
- "sql": Lead demonstrou intencao de compra, pediu preco/proposta/reuniao
- "cliente": Lead confirmou compra ou fechamento

### erros (lista de erros do vendedor, pode ser vazia)
Erros comuns a verificar:
- "Demora na resposta": vendedor levou muito tempo para responder
- "Sem apresentacao": nao se apresentou ou apresentou a empresa
- "Sem descoberta": nao fez perguntas para entender a necessidade do lead
- "Ignorou objecao": lead levantou objecao e vendedor nao tratou
- "Sem proximo passo": nao definiu proxima acao (reuniao, envio de proposta, etc)
- "Sem urgencia": nao criou senso de urgencia ou escassez
- "Respostas curtas": respostas monossilabicas ou sem agregar valor
- "Sem follow-up": conversa morreu sem tentativa de retomada

### sentimento_lead
- "positivo": lead engajado, fazendo perguntas, demonstrando interesse
- "neutro": lead respondendo mas sem entusiasmo claro
- "negativo": lead insatisfeito, reclamando, ou demonstrando desinteresse

### feedback_ia
Escreva 2-4 frases em portugues com feedback construtivo e direto para o gestor.
Destaque o que o vendedor fez bem e o que precisa melhorar.
Seja especifico, referenciando trechos da conversa quando possivel.', true, '2026-02-07 18:51:41.723947');


--
-- Data for Name: instancias_evolution; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.instancias_evolution (id, empresa_id, nome_instancia, telefone, ativa, criada_em) VALUES (1, 1, 'agente-comercial', NULL, false, '2026-02-08 13:11:42');
INSERT INTO public.instancias_evolution (id, empresa_id, nome_instancia, telefone, ativa, criada_em) VALUES (2, 2, 'Andre', '5549991125253', true, '2026-02-08 10:20:30.168954');


--
-- Data for Name: mensagens; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (1, 1, 'lead', 'Oi, vi o anuncio do plano empresarial. Quanto custa?', 'texto', '2026-02-05 09:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (2, 1, 'vendedor', 'Bom dia Ricardo! Temos planos a partir de R$299/mes. Quantos colaboradores voce tem?', 'texto', '2026-02-05 09:03:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (3, 1, 'lead', 'Somos 15 pessoas. Tem desconto pra essa quantidade?', 'texto', '2026-02-05 09:05:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (4, 1, 'vendedor', 'Com certeza! Para 15 usuarios, consigo um plano de R$249/mes por usuario. Inclui suporte prioritario e treinamento.', 'texto', '2026-02-05 09:08:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (5, 1, 'lead', 'Interessante. Vou conversar com meu socio e retorno.', 'texto', '2026-02-05 09:12:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (6, 1, 'vendedor', 'Perfeito! Posso agendar uma demo online pra voces dois verem o sistema funcionando?', 'texto', '2026-02-05 09:14:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (7, 1, 'lead', 'Boa ideia, pode ser quinta as 15h?', 'texto', '2026-02-05 09:18:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (8, 1, 'vendedor', 'Agendado! Vou enviar o link por aqui. Qualquer duvida estou a disposicao.', 'texto', '2026-02-05 09:20:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (9, 2, 'lead', 'Boa tarde! Quero contratar o plano premium.', 'texto', '2026-02-06 14:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (10, 2, 'vendedor', 'Boa tarde Mariana! Otimo! O premium inclui acesso ilimitado, API e suporte 24h. Posso gerar o contrato?', 'texto', '2026-02-06 14:02:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (11, 2, 'lead', 'Sim, pode mandar. CNPJ: 12.345.678/0001-00', 'texto', '2026-02-06 14:05:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (12, 2, 'vendedor', 'Contrato enviado por email! Assim que assinar, libero o acesso em ate 1h.', 'texto', '2026-02-06 14:08:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (13, 2, 'lead', 'Assinei agora. Obrigada pela agilidade!', 'texto', '2026-02-06 14:30:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (14, 2, 'vendedor', 'Acesso liberado! Enviei as credenciais por email. Bem-vinda! 🎉', 'texto', '2026-02-06 14:35:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (15, 3, 'lead', 'Oi, estou avaliando solucoes de CRM. O de voces integra com WhatsApp?', 'texto', '2026-02-07 10:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (16, 3, 'vendedor', 'Oi Felipe! Sim, temos integracao nativa com WhatsApp Business. Quer que eu mostre como funciona?', 'texto', '2026-02-07 10:04:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (17, 3, 'lead', 'Quero sim. Tambem preciso saber sobre importacao de dados.', 'texto', '2026-02-07 10:10:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (18, 3, 'vendedor', 'Temos importacao via CSV e API REST. Posso agendar uma call pra te mostrar tudo ao vivo?', 'texto', '2026-02-07 10:13:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (19, 4, 'lead', 'Ola, gostaria de saber mais sobre o produto.', 'texto', '2026-02-05 10:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (20, 4, 'vendedor', 'Oi Juliana, tudo bem? Qual produto te interessou?', 'texto', '2026-02-05 10:20:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (21, 4, 'lead', 'O plano basico. Qual o valor?', 'texto', '2026-02-05 10:22:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (22, 4, 'vendedor', 'O basico sai por R$99/mes. Quer que eu envie mais detalhes?', 'texto', '2026-02-05 10:45:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (23, 4, 'lead', 'Pode enviar sim.', 'texto', '2026-02-05 10:48:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (24, 4, 'vendedor', 'Enviei no seu email. Qualquer duvida me chama.', 'texto', '2026-02-05 11:10:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (25, 5, 'lead', 'Vi no site que voces tem periodo de teste. Como funciona?', 'texto', '2026-02-06 11:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (26, 5, 'vendedor', 'Oi Carlos! Sim, oferecemos 14 dias gratis. Quer ativar?', 'texto', '2026-02-06 11:15:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (27, 5, 'lead', 'Quero. Mas preciso que funcione com meu ERP.', 'texto', '2026-02-06 11:18:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (28, 5, 'vendedor', 'Temos integracao com os principais ERPs. Qual voce usa?', 'texto', '2026-02-06 11:35:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (29, 5, 'lead', 'Uso o TOTVS.', 'texto', '2026-02-06 11:38:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (30, 5, 'vendedor', 'Temos sim! Vou te mandar o link pra criar a conta de teste.', 'texto', '2026-02-06 12:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (31, 6, 'lead', 'Boa tarde, aceita PIX?', 'texto', '2026-02-07 13:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (32, 6, 'vendedor', 'Oi Patricia! Aceitamos PIX, cartao e boleto.', 'texto', '2026-02-07 13:12:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (33, 6, 'lead', 'Ok, vou pensar. Obrigada.', 'texto', '2026-02-07 13:15:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (34, 7, 'lead', 'Oi, preciso de ajuda para escolher um plano.', 'texto', '2026-02-05 09:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (35, 7, 'vendedor', 'Oi', 'texto', '2026-02-05 11:30:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (36, 7, 'lead', 'Oi, ainda estou esperando...', 'texto', '2026-02-05 11:35:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (37, 7, 'vendedor', 'Desculpa a demora. Temos 3 planos. Qual seu orcamento?', 'texto', '2026-02-05 13:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (38, 7, 'lead', 'Esquece, ja fechei com outra empresa.', 'texto', '2026-02-05 13:05:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (39, 8, 'lead', 'Boa tarde, quero saber sobre o servico de consultoria.', 'texto', '2026-02-06 14:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (40, 8, 'vendedor', 'Oi, temos consultoria sim.', 'texto', '2026-02-06 15:10:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (41, 8, 'lead', 'Qual o valor e o que inclui?', 'texto', '2026-02-06 15:12:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (42, 8, 'vendedor', 'Depende do escopo. Me passa seu email que mando proposta.', 'texto', '2026-02-06 16:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (43, 8, 'lead', 'Prefiro resolver por aqui mesmo. Pode me dar uma estimativa?', 'texto', '2026-02-06 16:05:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (44, 8, 'vendedor', 'Nao tenho como dar por aqui. Preciso do email.', 'texto', '2026-02-06 16:45:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (45, 9, 'lead', 'Oi, alguem pode me ajudar? Tenho interesse no plano anual.', 'texto', '2026-02-07 09:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (46, 9, 'lead', 'Alo?? Tem alguem ai?', 'texto', '2026-02-07 11:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (47, 10, 'lead', 'Oi, vi o anuncio no Instagram. Tem desconto?', 'texto', '2026-02-05 15:00:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (48, 10, 'vendedor', 'Nao temos desconto no momento.', 'texto', '2026-02-05 16:30:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (49, 10, 'lead', 'Nem pra pagamento a vista?', 'texto', '2026-02-05 16:35:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (50, 10, 'vendedor', 'Nao.', 'texto', '2026-02-05 17:15:00');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (51, 11, 'lead', 'No mid amor', 'texto', '2026-02-07 18:50:49');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (52, 11, 'vendedor', 'Ta bom', 'texto', '2026-02-07 18:53:06');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (53, 12, 'vendedor', 'Oi', 'texto', '2026-02-07 22:12:51');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (54, 12, 'vendedor', 'Teste', 'texto', '2026-02-07 22:13:06');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (55, 12, 'lead', 'Opa', 'texto', '2026-02-07 22:14:53');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (56, 12, 'lead', 'Diga rei', 'texto', '2026-02-07 22:14:58');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (57, 12, 'vendedor', 'Só fazendo uns testes aqui kkkk', 'texto', '2026-02-07 22:16:58');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (58, 12, 'lead', 'Ataaa', 'texto', '2026-02-07 22:17:12');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (59, 12, 'lead', 'Mas me ligou', 'texto', '2026-02-07 22:17:15');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (60, 12, 'lead', 'Foi tu ou o teste? Kkkk', 'texto', '2026-02-07 22:17:21');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (61, 12, 'vendedor', 'Era pra tu responder a mensagem', 'texto', '2026-02-07 22:17:27');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (62, 12, 'lead', 'Ata', 'texto', '2026-02-07 22:17:32');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (63, 12, 'lead', 'Achei que o Claude tinha me ligado', 'texto', '2026-02-07 22:17:37');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (64, 12, 'lead', 'Aí seria loucura', 'texto', '2026-02-07 22:17:42');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (65, 12, 'vendedor', 'Calma lá kkkk', 'texto', '2026-02-07 22:18:03');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (66, 12, 'vendedor', 'Manda outra aí', 'texto', '2026-02-07 22:18:41');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (67, 12, 'vendedor', 'Deu pau aqui', 'texto', '2026-02-07 22:18:45');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (68, 12, 'vendedor', 'Alou', 'texto', '2026-02-07 22:20:08');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (69, 12, 'vendedor', 'Bom dia', 'texto', '2026-02-07 22:20:10');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (70, 12, 'vendedor', 'Opaaa', 'texto', '2026-02-07 22:21:19');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (71, 12, 'lead', 'Opaa', 'texto', '2026-02-07 22:21:22');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (72, 12, 'lead', 'Aloo', 'texto', '2026-02-07 22:21:23');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (73, 12, 'lead', 'Vai saber KKKKK', 'texto', '2026-02-07 22:21:29');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (74, 12, 'vendedor', 'Opaaa', 'texto', '2026-02-07 22:22:33');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (75, 11, 'lead', 'Cheguei já amor', 'texto', '2026-02-07 22:23:11');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (76, 12, 'lead', 'Aloo', 'texto', '2026-02-07 22:23:36');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (77, 13, 'vendedor', 'Beleza', 'texto', '2026-02-07 22:24:20');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (78, 14, 'vendedor', 'Krl', 'texto', '2026-02-07 22:24:31');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (79, 14, 'vendedor', 'Esse petista não consegue configurar', 'texto', '2026-02-07 22:24:32');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (80, 12, 'lead', 'Deve ser bahiano', 'texto', '2026-02-07 22:26:17');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (81, 12, 'lead', 'Certeza', 'texto', '2026-02-07 22:26:19');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (82, 12, 'lead', 'Alo', 'texto', '2026-02-07 22:26:36');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (83, 12, 'lead', 'Gostaria de saber mais sobre seus serviços', 'texto', '2026-02-07 22:27:05');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (84, 14, 'vendedor', 'Bom dia Juliano!', 'texto', '2026-02-07 22:27:13');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (85, 14, 'vendedor', 'Meu nome é André da ReAu Marketing, como posso te ajudar?', 'texto', '2026-02-07 22:27:38');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (86, 12, 'lead', 'Quero serviços de tráfego pago', 'texto', '2026-02-07 22:27:58');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (87, 14, 'vendedor', 'Perfeito, custa 5 mil', 'texto', '2026-02-07 22:28:06');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (88, 14, 'vendedor', 'Vamos fechar?', 'texto', '2026-02-07 22:28:10');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (89, 11, 'lead', 'Vou tomar banho', 'texto', '2026-02-07 22:28:54');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (90, 12, 'lead', 'Muito caro, vou procurar outro', 'texto', '2026-02-07 22:29:07');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (91, 14, 'vendedor', '[imagem]', 'imagem', '2026-02-07 22:32:25');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (92, 14, 'vendedor', 'tá saindo da jaula', 'texto', '2026-02-07 22:32:29');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (93, 13, 'vendedor', 'também vou', 'texto', '2026-02-07 22:32:49');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (94, 12, 'lead', 'Dahora ta', 'texto', '2026-02-07 22:36:25');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (95, 12, 'lead', 'Ele deu até uma solução', 'texto', '2026-02-07 22:36:44');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (96, 12, 'lead', 'MT massa', 'texto', '2026-02-07 22:36:46');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (97, 14, 'vendedor', 'Isso é a ponta do iceberg kkk', 'texto', '2026-02-07 22:38:16');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (98, 14, 'vendedor', 'Quero muito que essa merda funcione', 'texto', '2026-02-07 22:38:34');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (99, 12, 'lead', 'Mas vai dar boa irmão', 'texto', '2026-02-07 22:44:55');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (100, 12, 'lead', 'Só continuar', 'texto', '2026-02-07 22:44:58');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (101, 14, 'vendedor', 'Vai sim', 'texto', '2026-02-07 22:55:38');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (102, 14, 'vendedor', 'Ou, lembra que tu tem até amanhã pra deixar pronta a parada do GA4 das clínicas', 'texto', '2026-02-07 22:56:01');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (103, 14, 'vendedor', 'Combinamos isso lá na segunda', 'texto', '2026-02-07 22:56:07');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (104, 12, 'lead', 'Sim, não esqueci', 'texto', '2026-02-07 22:57:10');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (105, 14, 'vendedor', 'Beleza', 'texto', '2026-02-07 22:57:57');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (106, 11, 'lead', 'Pode subir já amor', 'texto', '2026-02-07 22:58:12');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (107, 14, 'vendedor', 'As certificações gratuitas do Google que comentei contigo aquele dia tu tirou?', 'texto', '2026-02-07 22:58:30');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (108, 13, 'vendedor', 'Indo', 'texto', '2026-02-07 22:59:53');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (109, 11, 'lead', 'Taa', 'texto', '2026-02-07 23:07:36');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (110, 11, 'lead', 'Só secar o cabelo ainda', 'texto', '2026-02-07 23:07:43');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (111, 12, 'lead', 'Pior que nao', 'texto', '2026-02-07 23:08:59');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (112, 12, 'lead', 'Nem lembrava', 'texto', '2026-02-07 23:09:01');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (113, 15, 'vendedor', 'Oi mãe', 'texto', '2026-02-07 23:18:32');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (114, 15, 'vendedor', 'Amanhã tem almoço pra eu e a Paula?', 'texto', '2026-02-07 23:18:39');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (115, 15, 'lead', 'Oi', 'texto', '2026-02-07 23:19:49');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (116, 15, 'lead', 'Sim sempre né', 'texto', '2026-02-07 23:20:01');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (117, 15, 'vendedor', 'Beleza', 'texto', '2026-02-07 23:20:14');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (118, 15, 'vendedor', 'Kkk', 'texto', '2026-02-07 23:20:15');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (119, 15, 'lead', 'Kkk', 'texto', '2026-02-07 23:20:28');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (120, 16, 'lead', '🚨ALERTA DE FOFURA + FOME🚨

Se você tava procurando uma desculpa pra pedir hambúrguer… ACHOU 😎🍔😂

A Martina tá chegando 👶
e as fraldas… bom… não se compram sozinhas 😅

Então hoje é assim:
👉 Comprou qualquer lanche = ganhou batata grátis 🍟
👉 E ainda ajuda a gente a garantir as fraldinhas da pequena que já já tá por aqui ❤️

Bora fazer essa bebê nascer já cheia de moral 😂

📲 Já monta teu pedido aqui e se livre da louça👇🏾
Https://midwestburger.pedir.menu', 'imagem', '2026-02-08 17:22:13');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (121, 17, 'vendedor', 'Opa', 'texto', '2026-02-08 17:23:22');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (122, 17, 'vendedor', 'Não entendi a parada lá no grupo', 'texto', '2026-02-08 17:23:30');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (123, 17, 'lead', '[audio]', 'audio', '2026-02-08 17:24:07');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (124, 17, 'vendedor', 'Mas não entendi pq excluir', 'texto', '2026-02-08 17:24:38');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (125, 17, 'lead', 'Acho q oq ele quis dizer é que ele não é o nosso público de interesse', 'texto', '2026-02-08 17:25:24');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (126, 17, 'lead', 'Então não deveria aparecer pra ele', 'texto', '2026-02-08 17:25:29');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (127, 17, 'vendedor', 'Ele viu um de nosso anúncios e entrou no nosso perfil, automaticamente caiu no nosso remarketing', 'texto', '2026-02-08 17:26:21');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (128, 17, 'vendedor', 'Teoricamente quem faz esse movimento é quem tem algum interesse no nosso produto/conteudo', 'texto', '2026-02-08 17:27:24');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (129, 17, 'vendedor', 'Quem faz esse tipo de movimento se encaixa no nosso público morno, na minha visão o que não faz sentido é excluir', 'texto', '2026-02-08 17:28:13');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (130, 17, 'vendedor', 'Estamos justamente querendo chegar nessa galera', 'texto', '2026-02-08 17:28:24');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (131, 17, 'lead', '[audio]', 'audio', '2026-02-08 17:28:44');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (132, 17, 'vendedor', '[audio]', 'audio', '2026-02-08 17:30:01');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (133, 17, 'vendedor', '[audio]', 'audio', '2026-02-08 17:30:29');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (134, 17, 'lead', 'Entendi Andrezão', 'texto', '2026-02-08 17:30:45');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (135, 17, 'lead', 'Faz sentido isso mesmo', 'texto', '2026-02-08 17:31:06');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (136, 17, 'vendedor', 'Maaas se ele tem algo pra resolver isso diz pra ele entrar em contato que eu compro uma mentoria kkkk', 'texto', '2026-02-08 17:31:11');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (137, 17, 'lead', 'Kkkkkkkkk', 'texto', '2026-02-08 17:31:21');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (138, 17, 'lead', '[audio]', 'audio', '2026-02-08 17:31:29');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (139, 17, 'vendedor', 'Kkkkkk', 'texto', '2026-02-08 17:31:48');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (140, 17, 'vendedor', 'Eu não sei se tem como, mas vou até dar uma pesquisa', 'texto', '2026-02-08 17:32:05');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (141, 17, 'vendedor', 'É que não faz muito sentido, não tem como ter esse controle', 'texto', '2026-02-08 17:32:26');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (142, 17, 'vendedor', '[audio]', 'audio', '2026-02-08 17:33:19');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (143, 18, 'lead', 'Andrezão', 'texto', '2026-02-08 18:24:40');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (144, 18, 'lead', 'Câmbio?', 'texto', '2026-02-08 18:24:43');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (145, 18, 'lead', 'Me tira uma dúvida', 'texto', '2026-02-08 18:24:47');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (146, 18, 'lead', 'Tem como impulsionar conteúdo em cola!?', 'texto', '2026-02-08 18:24:54');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (147, 18, 'lead', 'Collab?*', 'texto', '2026-02-08 18:25:04');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (148, 18, 'vendedor', 'Buenas', 'texto', '2026-02-08 18:34:59');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (149, 18, 'vendedor', 'Tem sim', 'texto', '2026-02-08 18:35:06');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (150, 18, 'lead', 'Tranquilo', 'texto', '2026-02-08 18:49:46');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (151, 18, 'lead', 'Então', 'texto', '2026-02-08 18:49:47');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (152, 18, 'lead', 'Queria tirar a dúvida contigo', 'texto', '2026-02-08 18:50:18');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (153, 18, 'lead', 'O Igor tá produzindo alguns conteúdos de topo de funil', 'texto', '2026-02-08 18:50:30');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (154, 18, 'lead', 'Pra MedScale', 'texto', '2026-02-08 18:50:36');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (155, 18, 'lead', 'Aí eu falo pra ele postar', 'texto', '2026-02-08 18:50:44');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (156, 18, 'lead', 'Em collab com o dele', 'texto', '2026-02-08 18:50:48');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (157, 18, 'lead', 'Ou só no perfil da MedScale?', 'texto', '2026-02-08 18:51:21');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (158, 17, 'lead', 'É com muita alegria que convidamos você para fazer parte desse dia tão especial para nós. Ficaremos muito felizes com a sua presença. Iremos celebrar juntos, ao lado de pessoas especiais e em um pôr do sol inesquecível. 

Em breve enviaremos o nosso site, onde estarão disponíveis mais informações sobre o casamento e dicas do local.

Por enquanto, reservem a data: 28 de Novembro de 2026. 

Nos vemos no Ceará ✈️☀️🏝️ 

Com carinho,
Larissa e Daniel', 'imagem', '2026-02-08 18:59:34');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (159, 17, 'lead', 'Andrezão, já coloca na agenda aí!', 'texto', '2026-02-08 18:59:46');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (160, 13, 'lead', 'Que rápido', 'texto', '2026-02-08 21:50:52');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (161, 13, 'lead', 'Mmkkkk', 'texto', '2026-02-08 21:50:55');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (162, 13, 'vendedor', 'Sim', 'texto', '2026-02-08 21:52:36');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (163, 13, 'vendedor', 'Só tomamos uma e meti o pé kkk', 'texto', '2026-02-08 21:52:45');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (164, 13, 'vendedor', 'Pai tá cansado', 'texto', '2026-02-08 21:52:49');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (165, 13, 'lead', 'Kkkkkkk', 'texto', '2026-02-08 22:08:44');
INSERT INTO public.mensagens (id, conversa_id, remetente, conteudo, tipo, enviada_em) VALUES (166, 19, 'lead', 'Oi, quero saber mais sobre os serviços de marketing de vocês', 'texto', '2024-02-08 13:46:40');


--
-- Data for Name: metricas_diarias; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (1, 1, '2026-02-05', 1, 150, 180, 0, 1, 0, 8.5, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (2, 2, '2026-02-05', 1, 1300, 1200, 1, 0, 0, 6, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (3, 3, '2026-02-05', 2, 5475, 7200, 2, 0, 0, 3.2, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (4, 1, '2026-02-06', 1, 200, 120, 0, 0, 1, 8, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (5, 2, '2026-02-06', 1, 1080, 900, 0, 1, 0, 6.5, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (6, 3, '2026-02-06', 1, 3160, 4200, 1, 0, 0, 4, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (7, 1, '2026-02-07', 1, 210, 240, 0, 0, 1, 8, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (8, 2, '2026-02-07', 1, 720, 720, 1, 0, 0, 5.5, 0);
INSERT INTO public.metricas_diarias (id, vendedor_id, data, total_atendimentos, tempo_medio_resposta_seg, tempo_primeira_resp_seg, total_mql, total_sql, total_conversoes, score_medio, leads_sem_resposta) VALUES (9, 3, '2026-02-07', 1, NULL, NULL, 0, 0, 0, NULL, 1);


--
-- Name: analises_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.analises_id_seq', 10, true);


--
-- Name: configuracoes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.configuracoes_id_seq', 4, true);


--
-- Name: configuracoes_prompt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.configuracoes_prompt_id_seq', 2, true);


--
-- Name: conversas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.conversas_id_seq', 19, true);


--
-- Name: empresas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresas_id_seq', 2, true);


--
-- Name: instancias_evolution_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.instancias_evolution_id_seq', 2, true);


--
-- Name: mensagens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.mensagens_id_seq', 166, true);


--
-- Name: metricas_diarias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.metricas_diarias_id_seq', 9, true);


--
-- Name: vendedores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vendedores_id_seq', 4, true);


--
-- PostgreSQL database dump complete
--

\unrestrict fdF8mKxqdvK1q1ZNSLN9FdT0dBeFUiuBIuRyN8Vhsp1s6iTT2kTTlUIlFlGHMoz

