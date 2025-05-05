import streamlit as st
import boto3
import os
from pathlib import Path
from src.sts import get_client


BUCKET_NAME = os.getenv("BUCKET_NAME", "bucket-projects-987420003322")
S3_FILE_PATH = os.getenv("S3_FILE_PATH", "testesregressivos/examples")
TEMP_DIR = Path("temp")


def upload_file_to_s3(uploaded_file, bucket_name, s3_file_key):
    s3_client = get_client('s3')
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_file_key,
            Body=uploaded_file.getvalue()
        )
        st.success(f"Arquivo {uploaded_file.name} foi enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar o arquivo {uploaded_file.name}: {e}")


def download_file(s3_client, bucket, s3_key, local_path):
    try:
        s3_client.head_object(Bucket=bucket, Key=s3_key)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        s3_client.download_file(bucket, s3_key, str(local_path))
        st.success(f"Arquivo baixado para: {local_path}")
        return True
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            st.warning(f"{s3_key} NÃO existe no bucket.")
        else:
            st.error(f"Erro ao acessar {s3_key}: {e}")
    except Exception as e:
        st.error(f"Erro inesperado ao baixar {s3_key}: {e}")
    return False


def download_files(parameters):
    s3_client = get_client('s3')
    expected_workflows = len(parameters["environments"])
    workflows_downloaded = 0

    for repo, testes in parameters["resultado"].items():
        for pipeline_version, sdk_version in testes:
            config_key = f"{S3_FILE_PATH}/{pipeline_version}/{sdk_version}/config.yml"
            workflows_prefix = f"{S3_FILE_PATH}/{pipeline_version}/.github/workflows/"

            local_config_path = TEMP_DIR / config_key
            download_file(s3_client, BUCKET_NAME, config_key, local_config_path)

            try:
                response = s3_client.list_objects_v2(
                    Bucket=BUCKET_NAME,
                    Prefix=workflows_prefix
                )

                if 'Contents' not in response:
                    st.warning(f"Nenhum arquivo encontrado em {workflows_prefix}")
                    continue

                for obj in response['Contents']:
                    s3_key = obj['Key']
                    if s3_key.endswith('/'):
                        continue 

                    local_workflow_path = TEMP_DIR / s3_key
                    if download_file(s3_client, BUCKET_NAME, s3_key, local_workflow_path):
                        workflows_downloaded += 1

            except Exception as e:
                st.error(f"Erro ao listar ou baixar workflows de {workflows_prefix}: {e}")

    if workflows_downloaded < expected_workflows:
        st.warning(
            f"Foram baixados {workflows_downloaded}/{expected_workflows} workflows. "
            f"Pode haver arquivos faltando."
        )
    else:
        st.success(f"Todos os workflows ({workflows_downloaded}) foram baixados com sucesso.")
