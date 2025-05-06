import streamlit as st
import yaml
import json
from itertools import product
from utils.s3 import download_files, validate_files
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
            
            # if step_name in ['analytics', 'develop', 'hom'] :
            #    steps.append(put_values(possible_steps['start_step_function'].copy()), parameters["project_name", parameters["aws_account"]["step_name"]])

            if step_name in ['analytics', 'feature'] and "develop" in parameters["environments"]:
               steps.append(possible_steps['approve_pr_to_delevop'].copy())

            if step_name in ['develop'] and "homol" in parameters["environments"]:
                steps.append(possible_steps['approve_pr_to_release'].copy())
        
        steps = put_values(steps, parameters, destroy_value, pipeline_version, sdk_version)
    
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


    with open('config.yml', 'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False, allow_unicode=True)
    st.success("Arquivo de configuração criado com sucesso")

def get_tasks():
    with open('config.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    all_tasks = []

    for task_name, task_content in data.get("tasks", {}).items():
        all_tasks.append(task_name)

    st.write(all_tasks)
    return all_tasks


def gerar_nome_projeto(repo_nome):
    if "infra-" in repo_nome:
        parte_projeto = repo_nome.split("infra-")[-1]
    elif "app-" in repo_nome:
        parte_projeto = repo_nome.split("app-")[-1]
    else:
        parte_projeto = repo_nome 
    
    return f"iulotus-{parte_projeto.upper()}"

