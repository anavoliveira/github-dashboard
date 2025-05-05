import streamlit as st
import os
from src.s3 import upload_file_to_s3
from src.authentication import get_parameter_from_ssm, github_authentication
from src.utils import get_test_parameters
from src.github import test_start
import streamlit as st
import time

BUCKET_NAME = os.getenv("BUCKET_NAME", "bucket-projects-987420003322")
PIPELINE_VERSIONS = os.getenv("PIPELINE_VERSIONS", ["v1.0", "v2.0"])
SDK_VERSIONS = os.getenv("SDK_VERSIONS", ["0.9.2", "0.11.1"])
S3_FILE_PATH = os.getenv("S3_FILE_PATH", "testesregressivos/examples")


def authentication():
    with st.container():
        auth_type = st.radio(
            "",
            ["Parâmetro SSM", "Token"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if auth_type == "Parâmetro SSM":
            with st.form(key="ssm_form"):
                col1, col2 = st.columns([3, 1]) 
                with col1:
                    parameter_name = st.text_input(
                        "",
                        placeholder="Digite o nome do parâmetro no Parameter Store",
                        label_visibility="collapsed"
                    )
                with col2:
                    submitted = st.form_submit_button(
                        "Buscar",
                        use_container_width=True 
                    )
                    
                if submitted and parameter_name:
                    token = get_parameter_from_ssm(parameter_name)
                    if token:
                        github_authentication(token)
        else:
            with st.form(key="token_form"):
                col1, col2 = st.columns([3, 1])  
                with col1:
                    token_value = st.text_input(
                        "",
                        placeholder="Digite o token",
                        label_visibility="collapsed"
                    )
                with col2:
                    submitted = st.form_submit_button(
                        "Salvar",
                        use_container_width=True  
                    )
                    
                if submitted and token_value:
                    github_authentication(token_value)


def upload_files():
    with st.form(key="file_upload_form"):
        st.session_state.uploaded_files = []

        version = st.text_input("Versão", "v1.0") 
        # sdk_version = st.text_input("Versão", "v1.0") 
        sdk_version = "0.9.2"
        file_type = st.selectbox("Tipo de Arquivo", ["config.yml", "workflows"])
        uploaded_files = st.file_uploader("Escolha os arquivos", type=[ "yml"], accept_multiple_files=True)
        
        submitted = st.form_submit_button("Salvar")

        if submitted and uploaded_files:
            for uploaded_file in uploaded_files:
                if file_type == "config.yml":
                    s3_file_key = f"{version}/{sdk_version}/{uploaded_file.name}"
                else:
                    s3_file_key = f"{version}/.github/workflows/{uploaded_file.name}"
                upload_file_to_s3(uploaded_file, BUCKET_NAME, F"{S3_FILE_PATH}/{s3_file_key}")
                        
            st.session_state.uploaded_files = []


def tests_regressivos():
    get_test_parameters()
    test_start()

## ADICIONAIS
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


def main():
    st.set_page_config(page_title="Plataforma de Testes")

    # === Flow control ===
    if "step" not in st.session_state:
        st.session_state.step = "start"

    st.title("🔧 Plataforma de Testes")

    if st.session_state.step == "start":
        st.write("Clique no botão abaixo para iniciar os testes.")
        if st.button("Iniciar Testes"):
            # st.session_state.step = "login"
            st.session_state.step = "tests"
            st.rerun() 

    elif st.session_state.step == "login":
        st.subheader("🔑 Autenticação")
        authentication()

    elif st.session_state.step == "params":
        st.subheader("📝 Configuração dos testes")
        get_test_parameters()

    elif st.session_state.step == "tests":
        st.subheader("🚀 Execução dos Testes")
        test_start()
        # executar_testes()

    elif st.session_state.step == "upload_files":
        st.subheader("🚀 Upload de arquivos")
        upload_files()

    elif st.session_state.step == "tests_start":
        st.subheader("🚀 Upload de arquivos")
        test_start()
    
    st.sidebar.button("🔄 Reiniciar", on_click=lambda: st.session_state.clear())

    

    # st.markdown("---")

    # authentication()
    
    # st.markdown("---")

    # upload_files()

    # st.markdown("---")

    # tests_regressivos()
    

if __name__ == "__main__":
    main()
