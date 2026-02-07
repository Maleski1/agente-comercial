"""Seed de dados de teste para o dashboard.

Popula o banco com 3 vendedores, ~10 conversas, mensagens realistas,
analises com scores variados, e calcula metricas via engine existente.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Garantir que o projeto esteja no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.connection import SessionLocal, criar_tabelas
from src.database.models import Analise, Conversa, Mensagem, MetricaDiaria, Vendedor
from src.database.queries import (
    buscar_ou_criar_conversa,
    criar_vendedor,
    salvar_analise,
    salvar_mensagem,
)
from src.metrics.calculator import calcular_metricas


def limpar_banco(db):
    """Remove todos os dados existentes para seed limpo."""
    db.query(MetricaDiaria).delete()
    db.query(Analise).delete()
    db.query(Mensagem).delete()
    db.query(Conversa).delete()
    db.query(Vendedor).delete()
    db.commit()
    print("  Banco limpo.")

# === Helpers ===

hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
ontem = hoje - timedelta(days=1)
anteontem = hoje - timedelta(days=2)


def ts(base: datetime, hora: int, minuto: int = 0) -> datetime:
    """Cria timestamp a partir de data base + hora:minuto."""
    return base.replace(hour=hora, minute=minuto)


# === Dados dos Vendedores ===

VENDEDORES = [
    {"nome": "Ana Silva", "telefone": "5511999990001"},
    {"nome": "Bruno Costa", "telefone": "5511999990002"},
    {"nome": "Carla Souza", "telefone": "5511999990003"},
]

# === Conversas e Mensagens ===
# Formato: (conv_key, messages_list, analise_data)
# conv_key = (vendedor_index, lead_telefone, lead_nome, data_base)
# messages_list = [(remetente, conteudo, hora, minuto)]
# analise_data = (score, classificacao, erros, sentimento, feedback) ou None

CONVERSAS = [
    # --- Ana (idx=0) - Vendedora top, score alto ---

    # Ana - anteontem - conversa com lead interessado em plano empresarial
    (
        (0, "5511988880001", "Ricardo Mendes", anteontem),
        [
            ("lead", "Oi, vi o anuncio do plano empresarial. Quanto custa?", 9, 0),
            ("vendedor", "Bom dia Ricardo! Temos planos a partir de R$299/mes. Quantos colaboradores voce tem?", 9, 3),
            ("lead", "Somos 15 pessoas. Tem desconto pra essa quantidade?", 9, 5),
            ("vendedor", "Com certeza! Para 15 usuarios, consigo um plano de R$249/mes por usuario. Inclui suporte prioritario e treinamento.", 9, 8),
            ("lead", "Interessante. Vou conversar com meu socio e retorno.", 9, 12),
            ("vendedor", "Perfeito! Posso agendar uma demo online pra voces dois verem o sistema funcionando?", 9, 14),
            ("lead", "Boa ideia, pode ser quinta as 15h?", 9, 18),
            ("vendedor", "Agendado! Vou enviar o link por aqui. Qualquer duvida estou a disposicao.", 9, 20),
        ],
        (8.5, "sql", [], "positivo", "Excelente atendimento. Resposta rapida, ofereceu desconto e propos demo."),
    ),

    # Ana - ontem - conversa com lead que virou cliente
    (
        (0, "5511988880002", "Mariana Lima", ontem),
        [
            ("lead", "Boa tarde! Quero contratar o plano premium.", 14, 0),
            ("vendedor", "Boa tarde Mariana! Otimo! O premium inclui acesso ilimitado, API e suporte 24h. Posso gerar o contrato?", 14, 2),
            ("lead", "Sim, pode mandar. CNPJ: 12.345.678/0001-00", 14, 5),
            ("vendedor", "Contrato enviado por email! Assim que assinar, libero o acesso em ate 1h.", 14, 8),
            ("lead", "Assinei agora. Obrigada pela agilidade!", 14, 30),
            ("vendedor", "Acesso liberado! Enviei as credenciais por email. Bem-vinda! 🎉", 14, 35),
        ],
        (8.0, "cliente", [], "positivo", "Conversao rapida. Vendedora objetiva e eficiente na finalizacao."),
    ),

    # Ana - hoje - conversa em andamento
    (
        (0, "5511988880003", "Felipe Rocha", hoje),
        [
            ("lead", "Oi, estou avaliando solucoes de CRM. O de voces integra com WhatsApp?", 10, 0),
            ("vendedor", "Oi Felipe! Sim, temos integracao nativa com WhatsApp Business. Quer que eu mostre como funciona?", 10, 4),
            ("lead", "Quero sim. Tambem preciso saber sobre importacao de dados.", 10, 10),
            ("vendedor", "Temos importacao via CSV e API REST. Posso agendar uma call pra te mostrar tudo ao vivo?", 10, 13),
        ],
        (8.0, "cliente", [], "positivo", "Boa qualificacao do lead. Respostas rapidas e proposta de demo."),
    ),

    # --- Bruno (idx=1) - Vendedor mediano, score medio ---

    # Bruno - anteontem - conversa ok mas sem urgencia
    (
        (1, "5511988880004", "Juliana Alves", anteontem),
        [
            ("lead", "Ola, gostaria de saber mais sobre o produto.", 10, 0),
            ("vendedor", "Oi Juliana, tudo bem? Qual produto te interessou?", 10, 20),
            ("lead", "O plano basico. Qual o valor?", 10, 22),
            ("vendedor", "O basico sai por R$99/mes. Quer que eu envie mais detalhes?", 10, 45),
            ("lead", "Pode enviar sim.", 10, 48),
            ("vendedor", "Enviei no seu email. Qualquer duvida me chama.", 11, 10),
        ],
        (6.0, "mql", [{"tipo": "demora", "descricao": "Tempo de resposta acima do ideal (20 min)"}], "neutro", "Atendimento correto mas lento. Demorou 20 min para primeira resposta."),
    ),

    # Bruno - ontem - conversa com qualificacao parcial
    (
        (1, "5511988880005", "Carlos Eduardo", ontem),
        [
            ("lead", "Vi no site que voces tem periodo de teste. Como funciona?", 11, 0),
            ("vendedor", "Oi Carlos! Sim, oferecemos 14 dias gratis. Quer ativar?", 11, 15),
            ("lead", "Quero. Mas preciso que funcione com meu ERP.", 11, 18),
            ("vendedor", "Temos integracao com os principais ERPs. Qual voce usa?", 11, 35),
            ("lead", "Uso o TOTVS.", 11, 38),
            ("vendedor", "Temos sim! Vou te mandar o link pra criar a conta de teste.", 12, 0),
        ],
        (6.5, "sql", [{"tipo": "demora", "descricao": "Respostas com intervalos longos"}], "neutro", "Qualificou o lead mas poderia ter sido mais agil nas respostas."),
    ),

    # Bruno - hoje - conversa rapida
    (
        (1, "5511988880006", "Patricia Nunes", hoje),
        [
            ("lead", "Boa tarde, aceita PIX?", 13, 0),
            ("vendedor", "Oi Patricia! Aceitamos PIX, cartao e boleto.", 13, 12),
            ("lead", "Ok, vou pensar. Obrigada.", 13, 15),
        ],
        (5.5, "mql", [], "neutro", "Resposta correta mas nao explorou necessidades do lead."),
    ),

    # --- Carla (idx=2) - Vendedora com score baixo ---

    # Carla - anteontem - atendimento ruim, demorado
    (
        (2, "5511988880007", "Roberto Dias", anteontem),
        [
            ("lead", "Oi, preciso de ajuda para escolher um plano.", 9, 0),
            ("vendedor", "Oi", 11, 30),
            ("lead", "Oi, ainda estou esperando...", 11, 35),
            ("vendedor", "Desculpa a demora. Temos 3 planos. Qual seu orcamento?", 13, 0),
            ("lead", "Esquece, ja fechei com outra empresa.", 13, 5),
        ],
        (3.0, "mql", [
            {"tipo": "demora", "descricao": "Primeira resposta apos 2h30"},
            {"tipo": "perda", "descricao": "Lead perdido por demora no atendimento"},
        ], "negativo", "Atendimento pessimo. Lead perdido por tempo de resposta inaceitavel."),
    ),

    # Carla - ontem - atendimento sem profundidade
    (
        (2, "5511988880008", "Sandra Oliveira", ontem),
        [
            ("lead", "Boa tarde, quero saber sobre o servico de consultoria.", 14, 0),
            ("vendedor", "Oi, temos consultoria sim.", 15, 10),
            ("lead", "Qual o valor e o que inclui?", 15, 12),
            ("vendedor", "Depende do escopo. Me passa seu email que mando proposta.", 16, 0),
            ("lead", "Prefiro resolver por aqui mesmo. Pode me dar uma estimativa?", 16, 5),
            ("vendedor", "Nao tenho como dar por aqui. Preciso do email.", 16, 45),
        ],
        (4.0, "mql", [
            {"tipo": "demora", "descricao": "Respostas com atraso de 40+ minutos"},
            {"tipo": "comunicacao", "descricao": "Nao soube apresentar o produto pelo WhatsApp"},
        ], "negativo", "Vendedora insistiu em trocar de canal sem atender a necessidade do lead."),
    ),

    # Carla - hoje - lead sem resposta (gera alerta)
    (
        (2, "5511988880009", "Lucas Martins", hoje),
        [
            ("lead", "Oi, alguem pode me ajudar? Tenho interesse no plano anual.", 9, 0),
            ("lead", "Alo?? Tem alguem ai?", 11, 0),
        ],
        None,  # Sem analise - lead ignorado
    ),

    # Carla - anteontem - mais uma conversa fraca (garante media baixa)
    (
        (2, "5511988880010", "Fernanda Costa", anteontem),
        [
            ("lead", "Oi, vi o anuncio no Instagram. Tem desconto?", 15, 0),
            ("vendedor", "Nao temos desconto no momento.", 16, 30),
            ("lead", "Nem pra pagamento a vista?", 16, 35),
            ("vendedor", "Nao.", 17, 15),
        ],
        (3.5, "mql", [
            {"tipo": "comunicacao", "descricao": "Respostas secas e sem interesse"},
            {"tipo": "tecnica", "descricao": "Nao ofereceu alternativas ao desconto"},
        ], "negativo", "Comunicacao fria e sem esforco para reter o lead."),
    ),
]


def seed():
    """Pipeline principal de seed."""
    criar_tabelas()
    db = SessionLocal()

    try:
        # 0. Limpar dados existentes
        limpar_banco(db)

        # 1. Criar vendedores
        vendedores = []
        for v in VENDEDORES:
            vendedor = criar_vendedor(db, v["nome"], v["telefone"])
            vendedores.append(vendedor)
            print(f"  Vendedor: {vendedor.nome} (id={vendedor.id})")

        # 2. Criar conversas com mensagens e analises
        for entry in CONVERSAS:
            conv_key, mensagens, analise_data = entry
            v_idx, lead_tel, lead_nome, data_base = conv_key

            vendedor = vendedores[v_idx]
            conversa = buscar_ou_criar_conversa(db, vendedor.id, lead_tel, lead_nome)
            print(f"  Conversa: {vendedor.nome} <-> {lead_nome} (id={conversa.id})")

            for remetente, conteudo, hora, minuto in mensagens:
                salvar_mensagem(
                    db, conversa.id, remetente, conteudo,
                    enviada_em=ts(data_base, hora, minuto),
                )

            if analise_data:
                score, classif, erros, sentimento, feedback = analise_data
                salvar_analise(db, conversa.id, score, classif, erros, sentimento, feedback)

        # 3. Calcular metricas para cada dia
        dias = [
            anteontem.strftime("%Y-%m-%d"),
            ontem.strftime("%Y-%m-%d"),
            hoje.strftime("%Y-%m-%d"),
        ]
        for dia in dias:
            resultados = calcular_metricas(db, dia)
            total = sum(r["total_atendimentos"] for r in resultados)
            print(f"  Metricas {dia}: {total} atendimentos")

        # 4. Resumo
        print(f"\nSeed concluido!")
        print(f"  {len(vendedores)} vendedores")
        print(f"  {len(CONVERSAS)} conversas")
        print(f"  {len(dias)} dias de metricas")

    finally:
        db.close()


if __name__ == "__main__":
    print("Populando banco com dados de teste...\n")
    seed()
