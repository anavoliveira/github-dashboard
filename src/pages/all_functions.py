import streamlit as st
import os
from utils.forms import authentication, upload_files, tests_regressivos, get_test_parameters

BUCKET_NAME = os.getenv("BUCKET_NAME", "bucket-projects-987420003322")
PIPELINE_VERSIONS = os.getenv("PIPELINE_VERSIONS", ["v1.0", "v2.0"])
SDK_VERSIONS = os.getenv("SDK_VERSIONS", ["0.9.2", "0.11.1"])
S3_FILE_PATH = os.getenv("S3_FILE_PATH", "testesregressivos/examples")


def main():
    st.set_page_config(page_title="Testes Regressivos")
    st.title("Testes Regressivos")

    st.markdown("---")

    authentication()
    
    st.markdown("---")

    get_test_parameters()

    st.markdown("---")

    upload_files()

    # st.markdown("---")

    tests_regressivos()
    

if __name__ == "__main__":
    main()
