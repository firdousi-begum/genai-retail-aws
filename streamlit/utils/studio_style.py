# utils/studio_style.py

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
                background-color: rgb(42,20,64); 
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
