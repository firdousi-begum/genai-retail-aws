# utils/studio_style.py
import base64
import streamlit as st

def keyword_label(text):
    if 'Model' in text:
        return keyword_label_model(text)
    return f'<div class="keyword-label">{text}</div>'

def keyword_label_model(text):
    return f'<div class="keyword-label-model">{text}</div>'

def sentiment_label(sentiment, text):
    sentiment_lower = sentiment.lower()  # Convert to lowercase for case-insensitive matching
    if sentiment_lower == "positive":
        return f'<div class="sentiment-label-positive">{text}</div>'
    elif sentiment_lower == "negative":
        return f'<div class="sentiment-label-negative">{text}</div>'
    elif sentiment_lower == "mixed" or sentiment_lower == "neutral":
        return f'<div class="sentiment-label-mixed">{text}</div>'
    else:
        return f'<div class="sentiment-label-positive">{text}</div>'  # Default color if sentiment is not recognized

def apply_studio_style():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300&display=swap');

            body {
                font-family: 'Open Sans', sans-serif;
                margin: 0;
                padding: 0;
                color: #333;
                background-color: #f7f7f7;
            }

            .keyword-label {
                background-color: RGB(102, 0, 51); /* Blue background color */
                color: #fff; /* White text color */
                box-shadow: -5px -5px 10px rgba(0, 0, 0,0.5);
                border-radius: 5px;
                padding: 5px 10px;
                display: inline-block;
                margin-right: 10px;
                margin-top: 10px;
                font-size: 15px;
            }

            .keyword-label-model {
                background-color: RGB(135, 53, 5); /* Blue background color */
                color: #fff; /* White text color */
                box-shadow: -5px -5px 10px rgba(0, 0, 0,0.5);
                border-radius: 5px;
                padding: 5px 10px;
                display: inline-block;
                margin-right: 10px;
                margin-top: 10px;
                font-size: 15px;
            }

            .sentiment-label-positive  {
                background-color: RGB(0, 128, 0); /* Blue background color */
                color: #fff; /* White text color */
                #box-shadow: -2px -2px 3px rgba(0, 0, 0,0.5);
                border-radius: 10px;
                min-width: 100px;
                padding: 2px 5px;
                display: inline-block;
                margin-right: 5px;
                margin-top: 2px;
                margin-bottom: 5px;
                text-align: center;
                font-size: 90%;
            }

            .sentiment-label-negative  {
                background-color: RGB(200, 0, 67); /* Blue background color */
                color: #fff; /* White text color */
                #box-shadow: -2px -2px 3px rgba(0, 0, 0,0.5);
                border-radius: 10px;
                min-width: 100px;
                padding: 2px 5px;
                display: inline-block;
                margin-right: 5px;
                margin-top: 2px;
                margin-bottom: 5px;
                text-align: center;
                font-size: 90%;
            }

            .sentiment-label-mixed  {
                background-color: RGB(184, 136, 0); /* Blue background color */
                color: #fff; /* White text color */
                #box-shadow: -2px -2px 3px rgba(0, 0, 0,0.5);
                border-radius: 10px;
                min-width: 100px;
                padding: 2px 5px;
                display: inline-block;
                margin-right: 5px;
                margin-top: 2px;
                margin-bottom: 5px;
                text-align: center;
                font-size: 90%;
            }


            .output-text {
                #background-color: rgb(47,63,47); 
                #background-color: rgb(73,23,81); 
                background-color: rgb(36,34,67);
                color: #ffff; /* White text color */
                border-radius: 5px;
                # box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.5);
                # box-shadow: inset 0px 10px 20px 2px rgba(0, 0, 0, 0.25);
                box-shadow: -5px -5px 15px rgba(0, 0, 0,0.5),
                inset 0px 10px 20px 2px rgba(0, 0, 0, 0.25);
                padding: 5px 10px;
                display: inline-block;
                margin-right: 10px;
                margin-top: 10px;
                font-size: 15px;
                font-family: Arial, Helvetica, sans-serif;
            }

            .output-text-omit:hover{
                transform: translateY(5px);
                box-shadow: inset 0px 10px 20px 2px rgba(0, 0, 0, 0.25);
            }

            .custom-title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }

            .description-box {
                background-color: #fff;
                border-radius: 5px;
                padding: 20px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }

            .input-label {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }

            .text-input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                margin-bottom: 15px;
            }

            .text-area {
                width: 100%;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                resize: vertical;
                height: 150px;
                margin-bottom: 20px;
            }

            .generate-button {
                background-color: #007bff;
                color: #fff;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }

            .generated-description {
                margin-top: 20px;
                padding: 20px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_img_as_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


@st.cache_data  
def get_background():
    bg_img = get_img_as_base64("images/bg.png")
    logo = get_img_as_base64("images/logo.png")

    page_bg_img = f"""
    <style>
    .imglogo {{
    width: 100%;
    height: auto; 
    content:
    }}
    .stApp {{
    background-image: url("data:image/png;base64,{bg_img}");
    background-size: cover;
    }}

    [data-testid="stHeader"] {{
    background-color: rgba(0, 0, 0, 0);
    }}

   [data-testid="stHeader"]{{
    # background-image: url("data:image/png;base64,{logo}");
    # background-repeat: no-repeat;
    # background-size: 100% 100%;  
    # background-position: 50% 0%;
    background: url("data:image/png;base64,{logo}") 6% center/138px no-repeat, linear-gradient(to right, rgb(36,34,67) 40%,rgb(76,19,138) 70%, rgb(205,54,117));
    display: flex;
    align-items: center;
    justify-content: center;
    }}

    [data-testid="stSidebar"] {{
    #background-color: rgba(0, 0, 0, 0);
    # background-image: url("data:image/png;base64,{logo}"), url("data:image/png;base64,{bg_img}");
    # background-position: center 30px, center center;
    # background-repeat: no-repeat, no-repeat;
    # background-image: url("data:image/png;base64,{logo}");
    # background-position: center 30px;
    # background-repeat: no-repeat;
    # background-size: 138px;
    # position:relative;
      
    }}

    [data-testid="stSidebarNav"] {{
    background-image: url("data:image/png;base64,{logo}");
    background-position: center 30px;
    background-repeat: no-repeat;
    background-size: 138px;
    # position:relative;
      
    }}

    [data-testid="baseButton-secondary"] {{
    box-shadow: inset 0px -5px 5px 0px rgba(0, 0, 0, 0.5);
    background: linear-gradient(to bottom, rgb(143, 10, 86) ,rgb(168, 45, 97), rgb(143, 10, 86));

    }}

    [data-testid="baseButton-secondary"]:active {{
    transform: translateY(1px);
    #background-color: #230930;
    box-shadow: inset 0px 10px 20px 2px rgba(0, 0, 0, 0.25);
    }}

    [data-testid="stImage"] {{
    box-shadow: -5px -10px 10px rgba(0, 0, 0,0.5);
    border-radius: 5px;
    }}

    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)
