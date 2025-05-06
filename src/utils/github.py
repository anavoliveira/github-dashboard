import ryo
import subprocess
import streamlit as st
import streamlit as st
import time
from utils.utils import get_tasks

def test_start():
    st.title("🚀 Execução de Testes Automáticos")
    progress_bar = st.progress(0)
    table_placeholder = st.empty()
    log_placeholder = st.empty()

    etapas_detectadas = []
    status_dict = {}
    etapa_ativa = None

    tasks = get_tasks()
    for task in tasks:
        process = subprocess.Popen(
            ["ryo", "task", task],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
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
