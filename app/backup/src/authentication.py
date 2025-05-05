import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
import subprocess
from src.sts import get_client


DEFAULT_ROLE_ARN = os.getenv("ASSUME_ROLE_ARN", "arn:aws:iam::987420003322:role/streamlit-role")
SESSION_NAME = "streamlit"
REGION_NAME = os.getenv("REGION_NAME", "us-east-1")


def get_parameter_from_ssm(parameter_name):
    ssm_client = get_client('ssm')
    if ssm_client is None:
        return None

    try:
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ssm_client.exceptions.ParameterNotFound:
        st.error("Parâmetro não encontrado!")
    except (NoCredentialsError, PartialCredentialsError):
        st.error("Credenciais da AWS não encontradas.")
    except Exception as e:
        st.error(f"Erro ao acessar o Parameter Store: {e}")
    return None


def github_authentication(token):
    try:

        subprocess.run(
            ["gh", "auth", "login", "--with-token"],
            input=token,
            capture_output=True,
            text=True
        )

        subprocess.run( "gh auth status",
            input=token,
            capture_output=True,
            text=True
        )

        st.success("Autenticação realizada com sucesso")
    except Exception as e:
        st.error("Ocorreu um erro durante a autenticacao: {e}")      
