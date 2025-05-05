import streamlit as st
import os
from src.principals import upload_files

BUCKET_NAME = os.getenv("BUCKET_NAME", "bucket-projects-987420003322")
PIPELINE_VERSIONS = os.getenv("PIPELINE_VERSIONS", ["v1.0", "v2.0"])
SDK_VERSIONS = os.getenv("SDK_VERSIONS", ["0.9.2", "0.11.1"])
S3_FILE_PATH = os.getenv("S3_FILE_PATH", "testesregressivos/examples")


st.set_page_config(page_title="Testes Regressivos")
st.title("Upload de arquivos")

st.markdown("---")

upload_files()


    
