import streamlit as st
import os
from utils.s3 import upload_file_to_s3
from utils.authentication import get_parameter_from_ssm, github_authentication
from utils.utils import is_valid_selection, distribuir_testes, generate_config_file, validate_files
from utils.github import test_start
import streamlit as st

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
                # Campo principal
                parameter_name = st.text_input(
                    "",
                    placeholder="Digite o nome do parâmetro no Parameter Store",
                    label_visibility="collapsed"
                )

                # Campos adicionais: Usuário e E-mail
                github_user = st.text_input("Usuário do GitHub")
                github_email = st.text_input("E-mail do GitHub")

                # Botão por último
                submitted = st.form_submit_button(
                    "Enviar",
                    use_container_width=True
                )

                if submitted and parameter_name:
                    token = get_parameter_from_ssm(parameter_name)
                    if token:
                        github_authentication(token, github_user, github_email)
                        st.session_state["github_info"] = {
                            "user": github_user,
                            "email": github_email
                        }
                        st.success(f"Usuário salvo: {github_user}, E-mail salvo: {github_email}")

        else:
            with st.form(key="token_form"):
                # Campo principal
                token_value = st.text_input(
                    "",
                    placeholder="Digite o token",
                    label_visibility="collapsed"
                )

                # Campos adicionais: Usuário e E-mail
                github_user = st.text_input("Usuário do GitHub")
                github_email = st.text_input("E-mail do GitHub")

                # Botão por último
                submitted = st.form_submit_button(
                    "Enviar",
                    use_container_width=True
                )

                if submitted and token_value:
                    github_authentication(token_value, github_user, github_email)
                    st.session_state["github_info"] = {
                        "user": github_user,
                        "email": github_email
                    }
                    st.success(f"Usuário salvo: {github_user}, E-mail salvo: {github_email}")


def upload_files():
    with st.form(key="file_upload_form"):
        st.session_state.uploaded_files = []

        version = st.text_input("Versão", "v1.0") 
        # sdk_version = st.text_input("Versão", "v1.0") 
        sdk_version = "0.9.2"
        file_type = st.selectbox("Tipo de Arquivo", ["config.yml", "workflows"])
        uploaded_files = st.file_uploader("Escolha os arquivos", type=[ "yml"], accept_multiple_files=True)
        
        submitted = st.form_submit_button("Enviar", use_container_width=True)

        if submitted and uploaded_files:
            for uploaded_file in uploaded_files:
                if file_type == "config.yml":
                    s3_file_key = f"{version}/{sdk_version}/{uploaded_file.name}"
                else:
                    s3_file_key = f"{version}/.github/workflows/{uploaded_file.name}"
                upload_file_to_s3(uploaded_file, BUCKET_NAME, F"{S3_FILE_PATH}/{s3_file_key}")


def get_test_parameters():
    valid_options = ["analytics", "feature", "develop", "homol"]
    valid_combinations = [
        ["analytics", "develop", "homol"],
        ["analytics", "develop"],
        ["feature", "develop", "homol"],
        ["feature", "develop"],
        ["develop", "homol"],
        ["homol"],
        ["develop"],
        ["feature"],
        ["analytics"],
    ]
    destroy_valid_options = [["create"], ["delete"], ["create", "delete"]]
    
    with st.form(key="task_form"):
        repos_input = st.text_area("Lista de Repositórios (um por linha)")

        pipeline_versions_input = st.multiselect("Versões da esteira",
            PIPELINE_VERSIONS
        )
        
        sdk_versions_input = st.multiselect("Versões do sdk",
            SDK_VERSIONS
        )
        
        selected_environments = st.multiselect(
            "Ambientes de Execução Desejados",
            valid_options
        )

        account_numbers = {}
        account_numbers["analytics"] = st.text_input(
            "Número da conta de analytics",
            value="123456789012"
        )
        account_numbers["develop"] = st.text_input(
            "Número da conta de develop",
            value="987654321098"
        )
        account_numbers["homol"] = st.text_input(
            "Número da conta de homol",
            value="112233445566"
        )


        fluxos = st.multiselect(
            "Fluxos",
            ["create", "delete"]
        )
    
        branch_name = st.text_input("Nome da Branch Incial dos testes", "analytics")

        submitted = st.form_submit_button("Enviar", use_container_width=True)

        if submitted:
            repos_list = [repo.strip() for repo in repos_input.strip().split("\n") if repo.strip()]
            pipeline_versions_list = [versions for versions in pipeline_versions_input if versions]
            sdk_versions_list = [sdk_versions for sdk_versions in sdk_versions_input if sdk_versions]
    
            if is_valid_selection(selected_environments, valid_combinations):
                for combo in valid_combinations:
                    if set(selected_environments) == set(combo):
                        ordered_environments = combo  
                        break
                for option in destroy_valid_options:
                    if set(fluxos) == set(option):
                        ordered_destroy = option  
                        break
                
                resultado = distribuir_testes(repos_list, pipeline_versions_list, sdk_versions_list)

                parameters = {
                    "repositorios": repos_list,
                    "pipeline_versions": pipeline_versions_list,
                    "sdk_versions": sdk_versions_list,
                    "org_name": "itau-corp",
                    "branch": branch_name,
                    "destroy_list": ordered_destroy,
                    "environments": ordered_environments,
                    "resultado": resultado,
                    "aws_account": account_numbers
                }

                generate_config_file(parameters, repos_list)   
                validate_files(parameters)
                if st.session_state.get("params_ok"):
                    st.session_state.step = "tests"
                else:
                    st.session_state.step = "upload_files"
                #st.rerun()
            else: 
                error_message = """
                Combinação inválida! Os valores possíveis são:\n
                - 'analytics' \n
                - 'analytics', 'develop' \n
                - 'analytics', 'develop', 'homol' \n
                - 'feature' \n
                - 'feature', 'develop'\n
                - 'feature', 'develop', 'homol' \n
                - 'develop' \n
                - 'develop', 'homol' \n
                - 'homol' \n
                Por favor, escolha uma das opções válidas.\n
                """
                st.error(error_message)
                 

def tests_regressivos():
    with st.container():
        # st.markdown("### ✅ Checklist final")
        # st.markdown(f"""
        # - ✅ Parâmetros definidos
        # - ✅ Arquivos verificados ({len(st.session_state.get('missing_files', {}))} faltando)
        # - ✅ Ambiente autenticado
        # """)

        custom_button = """
        <style>
        div.stButton > button:first-child {
            font-size: 18px;
            padding: 0.5rem 0;;
            width: 100%;
            border-radius: 8px;
        }
        </style>
        """
        st.markdown(custom_button, unsafe_allow_html=True)

        if st.button("🚀 Iniciar os Testes"):
            test_start()
