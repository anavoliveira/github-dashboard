import streamlit as st
import yaml
import json
from itertools import product
from src.s3 import download_files
import os


PIPELINE_VERSIONS = os.getenv("PIPELINE_VERSIONS", ["v1.0", "v2.0"])
SDK_VERSIONS = os.getenv("SDK_VERSIONS", ["0.9.2", "0.11.1"])


def generate_task(base_steps, possible_steps, parameters, pipeline_version, sdk_version):
    
    steps = base_steps

    for destroy_value in parameters["destroy_list"]:
        
        steps.append(possible_steps["destroy"].copy())
        steps.append(possible_steps["commit"].copy())

        for step_name in parameters["environments"]:
            steps.append(possible_steps[step_name].copy())
            
            if step_name in ['analytics', 'feature'] and "develop" in parameters["environments"]:
               steps.append(possible_steps['approve_pr_to_delevop'].copy())

            if step_name in ['develop'] and "homol" in parameters["environments"]:
                steps.append(possible_steps['approve_pr_to_release'].copy())
        
        steps = put_values(steps, parameters,destroy_value, pipeline_version, sdk_version)
    
    return steps


def is_valid_selection(selection, valid_combinations):
    selection_set = set(selection)
    return any(selection_set == set(combo) and len(selection) == len(combo) for combo in valid_combinations)


def put_values(json_data, parameters, destroy_value, pipeline_version, sdk_version):

    substituicoes = {
        "{pipeline_version}": pipeline_version,
        "{sdk_version}": sdk_version,
        "{destroy_value}": destroy_value,
        "{branch_inicial}": parameters["branch"],
        "{branch_name}":parameters["branch"]
    }
    json_data = json.dumps(json_data)

    for chave, valor in substituicoes.items():
        json_data = json_data.replace(chave, valor)
    data = json.loads(json_data)

    return data


def distribuir_testes(repos, pipeline_versions, sdk_versions):
    combinacoes = list(product(pipeline_versions, sdk_versions))
    num_repos = len(repos)
    distribuicao = {repo: [] for repo in repos}
    
    for idx, combinacao in enumerate(combinacoes):
        repo = repos[idx % num_repos]
        distribuicao[repo].append(combinacao)
    
    return distribuicao     


def generate_config_file(parameters, repositorios):
    with open('config-example.json', 'r') as file:
        config_base = json.load(file)

    base_steps = config_base['tasks']['base_task']['steps']
    possible_steps = config_base['possible_steps']

    config_data = {
        "tasks": {}
    }

    for repo, testes in parameters["resultado"].items():
        for teste in testes:
            pipeline_version=teste[0]
            sdk_version=teste[1]
            task = generate_task(base_steps, possible_steps, parameters, pipeline_version, sdk_version)
            config_data["tasks"][f"{pipeline_version}-{sdk_version}"] = {}
            config_data["tasks"][f"{pipeline_version}-{sdk_version}"]["repository"] = repo
            config_data["tasks"][f"{pipeline_version}-{sdk_version}"]["steps"] = task


    with open('generated-config.yml', 'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False, allow_unicode=True)
    st.success("Arquivo de configuração criado com sucesso")


def get_test_parameters():
    st.subheader("Testes")
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

        fluxos = st.multiselect(
            "Fluxos",
            ["create", "delete"]
        )
    
        branch_name = st.text_input("Nome da Branch Incial dos testes", "analytics")

        submitted = st.form_submit_button("Enviar")

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
                    "resultado": resultado
                }

                generate_config_file(parameters, repos_list)   
                download_files(parameters)

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
 