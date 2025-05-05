import streamlit as st
import time

# Inicializa a etapa atual se não existir
if "step" not in st.session_state:
    st.session_state.step = "start"

# Função fake para login
def login_form():
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            # Aqui você colocaria a autenticação real
            if username and password:
                st.success("Login realizado com sucesso!")
                st.session_state.step = "params"
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

# Função fake para parâmetros
def parametros_form():
    with st.form("params_form"):
        param1 = st.text_input("Parâmetro 1")
        param2 = st.text_input("Parâmetro 2")
        submitted = st.form_submit_button("Submeter Testes")
        if submitted:
            if param1 and param2:
                st.session_state.parametros = {"param1": param1, "param2": param2}
                st.session_state.step = "running"
                st.rerun()
            else:
                st.error("Preencha todos os parâmetros.")

# Função fake para execução dos testes
def executar_testes():
    st.info("Verificando parâmetros...")
    time.sleep(1)
    st.success("Parâmetros verificados.")

    st.info("Verificando arquivos necessários...")
    time.sleep(1)
    st.success("Todos os arquivos estão presentes.")

    st.info("Criando arquivo config.yml...")
    time.sleep(1)
    st.success("Arquivo config.yml criado e salvo.")

    st.info("Iniciando testes...")
    progress = st.progress(0)
    for i in range(1, 101):
        time.sleep(0.02)
        progress.progress(i)
    st.success("Todos os testes foram concluídos com sucesso ✅")

# === Flow control ===

st.title("🔧 Plataforma de Testes")

if st.session_state.step == "start":
    st.write("Clique no botão abaixo para iniciar os testes.")
    if st.button("Iniciar Testes"):
        st.session_state.step = "login"
        st.rerun()  # 👈 ESSENCIAL PARA RERUN

elif st.session_state.step == "login":
    st.subheader("🔑 Login Necessário")
    login_form()

elif st.session_state.step == "params":
    st.subheader("📝 Configurar Parâmetros")
    parametros_form()

elif st.session_state.step == "running":
    st.subheader("🚀 Execução dos Testes")
    executar_testes()

# Opcional: botão de reset
st.sidebar.button("🔄 Reiniciar", on_click=lambda: st.session_state.clear())
