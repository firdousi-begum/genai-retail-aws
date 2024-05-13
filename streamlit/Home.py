import streamlit as st
from utils import config
from utils.studio_style import get_background

st.set_page_config(
    page_title="Generative AI for Retail",
    page_icon="🛒",
)

st.title("Welcome to Generative AI for Retail")

# Add an introduction or description for the app's home page
st.markdown("This app showcases various generative AI use cases for the retail industry.")

# Home Page Markdown
home_page_markdown = """

## Use Cases

### Product Reviews Summarization 🌟
Efficiently handle extensive product reviews using advanced summarization techniques. Get concise summaries and sentiment analysis to gain insights from customer feedback.
[Learn More](Product_Reviews)

### Product Descriptions Generation 📖
Effortlessly enhance your retail marketing strategy by crafting compelling and personalized product descriptions for improved customer engagement.
[Learn More](Product_Descriptions)

### Grocery Assistant 🥕
Welcome to the **Grocery Assistant**, your guide to planning and preparing a delicious dinner with ease. Create shopping cart, get recipe suggestions, and receive product recommendations.
[Learn More](Grocery_Assistant)

"""

# Render the home page
st.markdown(home_page_markdown)

get_background()
config.getEnvCredentials()