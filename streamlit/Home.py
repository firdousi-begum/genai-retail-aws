import streamlit as st
from utils import studio_style, config

st.set_page_config(
    page_title="Generative AI for Retail",
    page_icon="🛒",
)

studio_style.apply_app_styling()
config.getEnvCredentials()