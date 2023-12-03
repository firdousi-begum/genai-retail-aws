import streamlit as st
from utils import config

st.set_page_config(
    page_title="Generative AI for Retail",
    page_icon="🛒",
)

config.get_background()
config.getEnvCredentials()