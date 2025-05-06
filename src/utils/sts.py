import streamlit as st
import boto3
import os


DEFAULT_ROLE_ARN = os.getenv("ASSUME_ROLE_ARN", "arn:aws:iam::987420003322:role/streamlit-role")
SESSION_NAME = "streamlit"
REGION_NAME = os.getenv("REGION_NAME", "us-east-1")


def get_client(service_name, role_arn=DEFAULT_ROLE_ARN, session_name=SESSION_NAME, region_name=REGION_NAME):
    try:
        if role_arn:
            sts_client = boto3.client('sts')
            response = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name
            )
            credentials = response['Credentials']
            return boto3.client(
                service_name,
                region_name=region_name,
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
            )
        else:
            return boto3.client(service_name, region_name=region_name)
    except Exception as e:
        st.error(f"Erro ao criar o client AWS: {e}")
        return None
