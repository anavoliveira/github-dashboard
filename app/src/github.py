import ryo
import subprocess
import streamlit as st
import streamlit as st
import time


import streamlit as st
import subprocess

def test_start():
    st.title("🚀 Execução de Testes Automáticos")
    progress_bar = st.progress(0)
    table_placeholder = st.empty()
    log_placeholder = st.empty()

    etapas_detectadas = []
    status_dict = {}
    etapa_ativa = None

    process = subprocess.Popen(
        ["ryo", "task", "task-clone"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    current_block = ""
    
    for line in process.stdout:
        line = line.strip()
        # Detecta início de nova etapa
        # if "Processando reposit" in line or "Run" in line or "Monitorando" in line:
        if "Run Commit" in line or "Run Approve Pull Request" in line or "Monitorando o workflow" in line or "Realizando o clone do repositorio" in line or "Iniciando a alteracao do parametro destroy" in line:
            etapa = line

            # 👉 Antes de iniciar nova etapa, fecha a anterior se ainda estava em andamento
            if etapa_ativa and status_dict.get(etapa_ativa) == "🔄 Em andamento":
                status_dict[etapa_ativa] = "✅ Sucesso"

            etapas_detectadas.append(etapa)
            status_dict[etapa] = "🔄 Em andamento"
            etapa_ativa = etapa  # Atualiza etapa atual
            atualizar_tabela_status(table_placeholder, status_dict)
            current_block = f"🔧 **{etapa}**\n"
        
        # Detecta sucesso
        elif "success" in line.lower():
            current_block += f"✅ {line}\n"
            if etapa_ativa:
                status_dict[etapa_ativa] = "✅ Sucesso"
                atualizar_tabela_status(table_placeholder, status_dict)
        
        # Detecta erro
        elif "erro" in line.lower() or "error" in line.lower() or "nÃ£o existe" in line.lower():
            current_block += f"❌ {line}\n"
            if etapa_ativa:
                status_dict[etapa_ativa] = "❌ Falhou"
                atualizar_tabela_status(table_placeholder, status_dict)

        else:
            current_block += line + "\n"

        log_placeholder.markdown(f"```bash\n{current_block}\n```")

        # Atualiza barra de progresso
        if etapas_detectadas:
            progresso = len([v for v in status_dict.values() if "Sucesso" in v or "Falhou" in v]) / max(1, len(etapas_detectadas))
            progress_bar.progress(min(progresso, 1.0))

    # 🚨 Após o loop, fecha a última etapa se ainda estava em andamento
    if etapa_ativa and status_dict.get(etapa_ativa) == "🔄 Em andamento":
        status_dict[etapa_ativa] = "✅ Sucesso"
        atualizar_tabela_status(table_placeholder, status_dict)

    # Finalização
    if all("✅" in v for v in status_dict.values()):
        st.success("🎉 Todos os testes foram concluídos com sucesso!")
        st.balloons()
    else:
        st.error("⚠️ Alguns testes falharam. Confira os logs acima.")

def atualizar_tabela_status(table_placeholder, status_dict):
    table_data = [{"Etapa": etapa, "Status": status} for etapa, status in status_dict.items()]
    table_placeholder.table(table_data)




## QUARTA FORMA
# def test_start():
#     st.title("🚀 Execução de Testes Automáticos")
#     progress_bar = st.progress(0)
#     table_placeholder = st.empty()
#     log_placeholder = st.empty()

#     etapas_detectadas = []
#     status_dict = {}

#     process = subprocess.Popen(
#         ["ryo", "task", "task-clone"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True,
#         bufsize=1
#     )

#     current_block = ""
#     total_etapas = 5  # Ajuste conforme seu fluxo real

#     for line in process.stdout:
#         line = line.strip()
#         # Detecta início de nova etapa
#         if "Processando reposit" in line or "Run" in line or "Monitorando" in line:
#             etapa = line
#             etapas_detectadas.append(etapa)
#             status_dict[etapa] = "🔄 Em andamento"
#             atualizar_tabela_status(table_placeholder, status_dict)
#             current_block = f"🔧 **{etapa}**\n"
        
#         # Detecta sucesso
#         elif "success" in line.lower():
#             current_block += f"✅ {line}\n"
#             if etapas_detectadas:
#                 status_dict[etapas_detectadas[-1]] = "✅ Sucesso"
#                 atualizar_tabela_status(table_placeholder, status_dict)
        
#         # Detecta erro
#         elif "erro" in line.lower() or "error" in line.lower():
#             current_block += f"❌ {line}\n"
#             if etapas_detectadas:
#                 status_dict[etapas_detectadas[-1]] = "❌ Falhou"
#                 atualizar_tabela_status(table_placeholder, status_dict)

#         else:
#             current_block += line + "\n"

#         log_placeholder.markdown(f"```bash\n{current_block}\n```")

#         # Atualiza barra de progresso conforme detecta etapas novas
#         if etapas_detectadas:
#             progresso = len([v for v in status_dict.values() if "Sucesso" in v or "Falhou" in v]) / total_etapas
#             progress_bar.progress(progresso)

#     # Finalização: checar se tudo deu certo
#     if all("✅" in v for v in status_dict.values()):
#         st.success("🎉 Todos os testes foram concluídos com sucesso!")
#         st.balloons()
#     else:
#         st.error("⚠️ Alguns testes falharam. Confira os logs acima.")

# def atualizar_tabela_status(table_placeholder, status_dict):
#     table_data = [{"Etapa": etapa, "Status": status} for etapa, status in status_dict.items()]
#     table_placeholder.table(table_data)



#TERCEIRA FORMA

# import subprocess
# import streamlit as st

# def test_start():
#     st.subheader("🚀 Execução dos testes")
#     log_placeholder = st.empty()

#     try:
#         process = subprocess.Popen(
#             ["ryo", "task", "task-clone"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             bufsize=1
#         )

#         logs = ""
#         current_block = ""

#         for line in process.stdout:
#             logs += line
#             # Exemplo: destaca início de uma nova seção
#             if "Processando reposit" in line:
#                 if current_block:
#                     log_placeholder.markdown(f"```bash\n{current_block}\n```")
#                 current_block = f"🔧 **{line.strip()}**\n"
#             elif "success" in line.lower():
#                 current_block += f"✅ {line}"
#             elif "erro" in line.lower() or "error" in line.lower():
#                 current_block += f"❌ {line}"
#             else:
#                 current_block += line

#             # Para atualizar sem empilhar muito rápido
#             log_placeholder.markdown(f"```bash\n{current_block}\n```")

#         process.stdout.close()
#         return_code = process.wait()

#         if return_code == 0:
#             st.success("✅ Processo finalizado com sucesso.")
#         else:
#             st.error(f"⚠️ Processo terminou com erro (código {return_code}).")

#     except Exception as e:
#         st.error(f"Ocorreu um erro durante a execução: {e}")



# SEGUNDA FORMA
# import subprocess
# import streamlit as st

# def test_start():
#     st.subheader("Execução dos testes")
#     log_placeholder = st.empty()

#     try:
#         # Use Popen para capturar a saída em tempo real
#         process = subprocess.Popen(
#             ["ryo", "task", "task-clone"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             bufsize=1  # Linha a linha
#         )

#         logs = ""

#         # Lê a saída linha por linha enquanto o processo roda
#         for line in process.stdout:
#             logs += line
#             log_placeholder.text(logs)  # Atualiza o placeholder

#         process.stdout.close()
#         return_code = process.wait()

#         if return_code == 0:
#             st.success("Processo finalizado com sucesso.")
#         else:
#             st.error(f"Processo terminou com erro (código {return_code}).")

#         # Aqui você poderia salvar o 'logs' para arquivo também

#     except Exception as e:
#         st.error(f"Ocorreu um erro durante a execução: {e}")



#PRIMEIRA FORMA
# log_placeholder = st.empty()

# def my_long_process():
#     for i in range(10):
#         log_placeholder.write(f"Step {i+1}/10 em andamento...")
#         time.sleep(2)
#     log_placeholder.write("✅ Finalizado!")

# if st.button("Iniciar Processo"):
#     my_long_process()

# def test_start():
#     st.subheader("Eexecucao dos testes")
#     try:
#         process = subprocess.run(
#             # "ryo --version",
#             "ryo task task-clone",
#             capture_output=True,
#             text=True
#         )
#         output = process.stdout
#         st.success(f"Autenticação realizada com sucesso, {output}")
#         # st.success("Login realizado com sucesso!")
#         # st.session_state.step = "params"
#         # st.rerun()
#     except Exception as e:
#         st.error("Ocorreu um erro durante a autenticacao: {e}")     