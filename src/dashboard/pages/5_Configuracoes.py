"""Dashboard - Página 5: Configurações (OpenAI, Evolution API, Instâncias, Prompt IA) — multi-tenant."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st  # noqa: E402
import httpx  # noqa: E402
import base64  # noqa: E402

from src.dashboard.utils import get_db, validar_token_empresa  # noqa: E402
from src.dashboard.theme import aplicar_tema, render_sidebar, render_page_header, render_footer  # noqa: E402
from src.database.connection import criar_tabelas  # noqa: E402
from src.database.queries import (  # noqa: E402
    salvar_configuracao,
    buscar_prompt_ativo,
    salvar_prompt,
    listar_instancias_empresa,
    criar_instancia_evolution,
    atualizar_instancia,
    desativar_instancia,
)
from src.analysis.prompts import SYSTEM_PROMPT  # noqa: E402
from src.config import settings  # noqa: E402
from src.config_manager import get_config  # noqa: E402

criar_tabelas()

# --- Tema e autenticação ---
aplicar_tema()
empresa_id, empresa_nome = validar_token_empresa()
render_sidebar(empresa_nome)
render_page_header("Configurações", "Chaves de API, instâncias e prompt IA")

tab_openai, tab_evolution, tab_instancias, tab_prompt, tab_geral = st.tabs(
    ["OpenAI", "Evolution API", "Instâncias WhatsApp", "Prompt IA", "Geral"]
)

# =============================================================================
# Aba OpenAI
# =============================================================================
with tab_openai:
    st.subheader("Chave da API OpenAI")

    chave_atual = get_config("openai_api_key", empresa_id=empresa_id, default="")
    if chave_atual:
        mascarada = f"sk-...{chave_atual[-4:]}"
        st.success(f"Chave configurada: `{mascarada}`")
    else:
        st.warning("Nenhuma chave configurada. A análise de conversas não funcionará.")

    nova_chave = st.text_input("Nova API Key", type="password", key="openai_key_input")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Chave", type="primary", key="save_openai"):
            if not nova_chave.strip():
                st.error("Informe uma chave.")
            else:
                with get_db() as db:
                    salvar_configuracao(db, "openai_api_key", nova_chave.strip(), empresa_id=empresa_id)
                st.success("Chave salva!")
                st.rerun()
    with col2:
        if st.button("Testar Conexão", key="test_openai"):
            chave_teste = nova_chave.strip() or chave_atual
            if not chave_teste:
                st.error("Nenhuma chave para testar.")
            else:
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=chave_teste)
                    client.models.list()
                    st.success("Conexão OK!")
                except Exception as e:
                    st.error(f"Falha: {e}")


# =============================================================================
# Aba Evolution API (configs globais da API)
# =============================================================================
with tab_evolution:
    st.subheader("Configurações da Evolution API")

    evo_url = get_config("evolution_api_url", empresa_id=empresa_id, default="http://localhost:8080")
    evo_key = get_config("evolution_api_key", empresa_id=empresa_id, default="")

    nova_url = st.text_input("API URL", value=evo_url, key="evo_url_input")
    nova_evo_key = st.text_input("API Key", value=evo_key, type="password", key="evo_key_input")

    if st.button("Salvar Configurações", type="primary", key="save_evolution"):
        url_limpa = nova_url.strip().rstrip("/")
        if url_limpa.endswith("/manager"):
            url_limpa = url_limpa[:-8]
        with get_db() as db:
            salvar_configuracao(db, "evolution_api_url", url_limpa, empresa_id=empresa_id)
            salvar_configuracao(db, "evolution_api_key", nova_evo_key.strip(), empresa_id=empresa_id)
        st.success("Configurações salvas!")
        st.rerun()

    st.divider()
    st.subheader("Diagnóstico")

    if st.button("Testar Conexão", key="test_evolution"):
        url_teste = nova_url.strip() or evo_url
        key_teste = nova_evo_key.strip() or evo_key
        if not url_teste or not key_teste:
            st.error("URL e API Key são necessários.")
        else:
            try:
                r = httpx.get(
                    f"{url_teste}/instance/fetchInstances",
                    headers={"apikey": key_teste},
                    timeout=10,
                )
                r.raise_for_status()
                instancias = r.json()
                st.success(f"Conexão OK! {len(instancias)} instância(s) encontrada(s).")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    st.error("API Key inválida (401 Unauthorized).")
                else:
                    st.error(f"Erro HTTP {e.response.status_code}: {e}")
            except Exception as e:
                st.error(f"Falha na conexão: {e}")


# =============================================================================
# Aba Instâncias WhatsApp (por empresa)
# =============================================================================
with tab_instancias:
    st.subheader("Instâncias WhatsApp da Empresa")

    evo_url = get_config("evolution_api_url", empresa_id=empresa_id, default="http://localhost:8080")
    evo_key = get_config("evolution_api_key", empresa_id=empresa_id, default="")

    with get_db() as db:
        instancias = listar_instancias_empresa(db, empresa_id)
        instancias_data = [
            {"id": i.id, "nome": i.nome_instancia, "telefone": i.telefone, "ativa": i.ativa}
            for i in instancias
        ]

    if not instancias_data:
        st.info("Nenhuma instância cadastrada.")
    else:
        for inst in instancias_data:
            with st.expander(f"{inst['nome']} {'(ativa)' if inst['ativa'] else '(inativa)'}"):
                st.text(f"Telefone: {inst['telefone'] or 'não definido'}")

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("Status", key=f"status_{inst['id']}"):
                        if not evo_url or not evo_key:
                            st.error("Configure a Evolution API primeiro.")
                        else:
                            try:
                                r = httpx.get(
                                    f"{evo_url}/instance/connectionState/{inst['nome']}",
                                    headers={"apikey": evo_key},
                                    timeout=10,
                                )
                                r.raise_for_status()
                                dados = r.json()
                                estado = dados.get("instance", {}).get("state", "desconhecido")
                                if estado == "open":
                                    st.success(f"Conectada ({estado})")
                                else:
                                    st.warning(f"Estado: {estado}")
                            except Exception as e:
                                st.error(f"Erro: {e}")
                with c2:
                    if st.button("QR Code", key=f"qr_{inst['id']}"):
                        if not evo_url or not evo_key:
                            st.error("Configure a Evolution API primeiro.")
                        else:
                            try:
                                r = httpx.get(
                                    f"{evo_url}/instance/connect/{inst['nome']}",
                                    headers={"apikey": evo_key},
                                    timeout=15,
                                )
                                r.raise_for_status()
                                dados = r.json()
                                qr_base64 = dados.get("base64", "")
                                if qr_base64:
                                    if "," in qr_base64:
                                        qr_base64 = qr_base64.split(",", 1)[1]
                                    img_bytes = base64.b64decode(qr_base64)
                                    st.image(img_bytes, caption="Escaneie com WhatsApp", width=300)
                                else:
                                    st.info("Nenhum QR retornado. Instância já pode estar conectada.")
                            except Exception as e:
                                st.error(f"Erro ao gerar QR: {e}")
                with c3:
                    if st.button("Webhook", key=f"wh_{inst['id']}"):
                        if not evo_url or not evo_key:
                            st.error("Configure a Evolution API primeiro.")
                        elif not settings.webhook_url or not settings.webhook_secret:
                            st.error("WEBHOOK_URL ou WEBHOOK_SECRET não definidos no ambiente.")
                        else:
                            try:
                                r = httpx.post(
                                    f"{evo_url}/webhook/set/{inst['nome']}",
                                    headers={"apikey": evo_key, "Content-Type": "application/json"},
                                    json={
                                        "webhook": {
                                            "url": settings.webhook_url,
                                            "enabled": True,
                                            "headers": {"apikey": settings.webhook_secret},
                                            "events": ["MESSAGES_UPSERT"],
                                        }
                                    },
                                    timeout=10,
                                )
                                r.raise_for_status()
                                st.success("Webhook configurado!")
                            except Exception as e:
                                st.error(f"Erro ao configurar webhook: {e}")

                st.divider()
                st.caption("Editar instância")
                novo_nome_inst = st.text_input(
                    "Nome da instância", value=inst['nome'], key=f"edit_nome_{inst['id']}"
                )
                novo_tel_inst = st.text_input(
                    "Telefone", value=inst['telefone'] or "", key=f"edit_tel_{inst['id']}"
                )
                col_save, col_rm = st.columns(2)
                with col_save:
                    if st.button("Salvar alterações", key=f"save_{inst['id']}"):
                        with get_db() as db:
                            atualizar_instancia(
                                db, inst['id'], empresa_id,
                                novo_nome_inst.strip() or None,
                                novo_tel_inst.strip() or None,
                            )
                        st.success("Instância atualizada!")
                        st.rerun()
                with col_rm:
                    if st.button("Remover instância", key=f"rm_{inst['id']}"):
                        # 1. Deletar no Evolution API
                        if evo_url and evo_key:
                            try:
                                r = httpx.delete(
                                    f"{evo_url}/instance/delete/{inst['nome']}",
                                    headers={"apikey": evo_key},
                                    timeout=10,
                                )
                                r.raise_for_status()
                            except httpx.HTTPStatusError as e:
                                if e.response.status_code != 404:
                                    st.warning(f"Aviso: erro ao remover do Evolution ({e.response.status_code})")
                            except Exception:
                                st.warning("Aviso: não foi possível remover do Evolution.")
                        # 2. Desativar no banco
                        with get_db() as db:
                            desativar_instancia(db, inst['id'], empresa_id)
                        st.success(f"Instância '{inst['nome']}' removida!")
                        st.rerun()

    st.divider()
    st.subheader("Adicionar Instância")

    novo_nome = st.text_input("Nome da nova instância", key="nova_inst_nome")
    novo_tel = st.text_input("Telefone (opcional)", key="nova_inst_tel")

    if st.button("Criar Instância", type="primary", key="criar_instancia"):
        nome_inst = novo_nome.strip()
        tel_inst = novo_tel.strip() or None

        if not nome_inst:
            st.error("Informe o nome da instância.")
        elif not evo_url or not evo_key:
            st.error("Configure a Evolution API primeiro (aba Evolution API).")
        else:
            # 1. Criar instância na Evolution API (ou detectar que já existe)
            ja_existe = False
            try:
                r = httpx.post(
                    f"{evo_url}/instance/create",
                    headers={"apikey": evo_key, "Content-Type": "application/json"},
                    json={
                        "instanceName": nome_inst,
                        "integration": "WHATSAPP-BAILEYS",
                        "qrcode": True,
                    },
                    timeout=15,
                )
                r.raise_for_status()
                evo_data = r.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403 and "already in use" in e.response.text:
                    st.info(f"Instância '{nome_inst}' já existe no Evolution. Registrando e configurando webhook...")
                    evo_data = {}
                    ja_existe = True
                else:
                    st.error(f"Erro ao criar instância no Evolution (HTTP {e.response.status_code}): {e.response.text}")
                    evo_data = None
            except Exception as e:
                st.error(f"Erro ao criar instância no Evolution: {e}")
                evo_data = None

            if evo_data is not None:
                # 2. Configurar webhook automaticamente
                webhook_ok = False
                if settings.webhook_url and settings.webhook_secret:
                    try:
                        r = httpx.post(
                            f"{evo_url}/webhook/set/{nome_inst}",
                            headers={"apikey": evo_key, "Content-Type": "application/json"},
                            json={
                                "webhook": {
                                    "url": settings.webhook_url,
                                    "enabled": True,
                                    "headers": {"apikey": settings.webhook_secret},
                                    "events": ["MESSAGES_UPSERT"],
                                }
                            },
                            timeout=10,
                        )
                        r.raise_for_status()
                        webhook_ok = True
                    except Exception as e:
                        st.warning(f"Instância criada, mas erro ao configurar webhook: {e}")
                else:
                    st.warning("WEBHOOK_URL ou WEBHOOK_SECRET não definidos. Configure o webhook manualmente.")

                # 3. Salvar no banco
                with get_db() as db:
                    try:
                        criar_instancia_evolution(db, empresa_id, nome_inst, tel_inst)
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco: {e}")

                if webhook_ok:
                    st.success(f"Instância '{nome_inst}' criada com webhook configurado!")
                else:
                    st.success(f"Instância '{nome_inst}' criada! Use o botão Webhook para configurar.")

                # 4. Mostrar QR Code para conexão
                qr = evo_data.get("qrcode", {})
                qr_base64 = qr.get("base64", "") if isinstance(qr, dict) else ""
                if qr_base64:
                    if "," in qr_base64:
                        qr_base64 = qr_base64.split(",", 1)[1]
                    img_bytes = base64.b64decode(qr_base64)
                    st.image(img_bytes, caption="Escaneie com WhatsApp para conectar", width=300)
                else:
                    st.info("Use o botão 'QR Code' na instância para conectar.")


# =============================================================================
# Aba Prompt IA
# =============================================================================
with tab_prompt:
    st.subheader("Prompt de Análise IA")
    st.caption(
        "Edite o system prompt usado pela IA para analisar conversas. "
        "Mudanças são aplicadas imediatamente nas próximas análises."
    )

    with get_db() as db:
        config_ativa = buscar_prompt_ativo(db, empresa_id=empresa_id)

    prompt_atual = config_ativa.conteudo if config_ativa else SYSTEM_PROMPT
    is_customizado = config_ativa is not None

    if is_customizado:
        st.info("Usando prompt customizado (salvo no banco).")
    else:
        st.info("Usando prompt padrão do sistema.")

    prompt_editado = st.text_area("System Prompt", value=prompt_atual, height=400, key="prompt_ta")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar Prompt", type="primary", key="save_prompt"):
            if not prompt_editado.strip():
                st.error("O prompt não pode estar vazio.")
            elif prompt_editado.strip() == prompt_atual.strip():
                st.warning("Nenhuma alteração detectada.")
            else:
                with get_db() as db:
                    salvar_prompt(db, prompt_editado.strip(), empresa_id=empresa_id)
                st.success("Prompt salvo com sucesso!")
                st.rerun()
    with col2:
        if st.button("Restaurar Padrão", key="restore_prompt"):
            if not is_customizado:
                st.warning("Já está usando o prompt padrão.")
            else:
                with get_db() as db:
                    salvar_prompt(db, SYSTEM_PROMPT, empresa_id=empresa_id)
                st.success("Prompt padrão restaurado!")
                st.rerun()


# =============================================================================
# Aba Geral (gestor_telefone, horario_relatorio)
# =============================================================================
with tab_geral:
    st.subheader("Configurações Gerais")

    gestor_tel = get_config("gestor_telefone", empresa_id=empresa_id, default="")
    horario = get_config("horario_relatorio", empresa_id=empresa_id, default="20:00")

    novo_gestor = st.text_input("Telefone do Gestor (recebe relatório)", value=gestor_tel, key="gestor_tel")
    novo_horario = st.text_input("Horário do Relatório (HH:MM)", value=horario, key="horario_rel")

    if st.button("Salvar", type="primary", key="save_geral"):
        with get_db() as db:
            if novo_gestor.strip():
                salvar_configuracao(db, "gestor_telefone", novo_gestor.strip(), empresa_id=empresa_id)
            if novo_horario.strip():
                salvar_configuracao(db, "horario_relatorio", novo_horario.strip(), empresa_id=empresa_id)
        st.success("Configurações salvas!")
        st.rerun()

render_footer()
