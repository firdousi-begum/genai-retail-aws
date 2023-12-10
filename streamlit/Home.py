import streamlit as st
from utils import config
from utils.studio_style import get_background

st.set_page_config(
    page_title="Generative AI for Retail",
    page_icon="🛒",
)

get_background()
config.getEnvCredentials()