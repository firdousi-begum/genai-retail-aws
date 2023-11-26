import streamlit as st
from utils import config
import utils.authenticate as auth

st.set_page_config(
    page_title="Generative AI for Retail",
    page_icon="🛒",
)

config.getEnvCredentials()

auth.check_login()