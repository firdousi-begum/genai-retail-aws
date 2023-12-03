import streamlit as st
from langchain import PromptTemplate
from utils.studio_style import apply_studio_style
from utils.studio_style import keyword_label
from utils import langchain
from utils import bedrock
from utils import config
from datetime import datetime
import pandas as pd
import logging

st.set_page_config(
    page_title="Summarize Product Reviews",
    page_icon="🛒",
)
st.cache_data.clear()
config.get_background()

# Read the CSV file
@st.cache_data
def load_data():
    data = pd.read_csv("./data/amazon_vfl_reviews.csv")
    return data

# Your content and interactive elements for the Summarize Product Reviews page

def generate_review_summary (product_reviews, product_name):
    
    if product_reviews is None:
        return
    
    product_reviews = f"""Product Name:{product_name}\n
    Reviews: {product_reviews}
    """
    map_prompt = """
    Write a concise summary of the following product reviews:
    "{text}"
    CONCISE SUMMARY:
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])

    combine_prompt = """
    Write a concise summary of the following product reviews for the product delimited by triple backquotes. 
    ```{text}```

    Return overall sentiment of the product reviews in separate section 'SENTIMENT' after thie concise summary.
    Return important keywords from the product reviews in separate section 'KEYWORDS' after the 'SENTIMENT'.
    
    <outputFormat>
    **SUMMARY:** Concise summary of the product reviews \n\n

    **SENTIMENT:** overall sentiment for the summary: POSITIVE, NEGATIVE or MIXED \n\n\n\n
    **KEYWORDS:** extract important keywords from the summary
    </outputFormat>
   

    """
    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])
    #modelId = 'amazon.titan-tg1-large'
    # inference_config = {
    #                         "maxTokenCount":3072,
    #                         "stopSequences":[],
    #                         "temperature":0,
    #                         "topP":0.9
    #                         }
    modelId = 'anthropic.claude-instant-v1'
    inference_config = {
                                "max_tokens_to_sample":4096,
                                "temperature":0.5,
                                "top_k":250,
                                "top_p":0.5,
                                "stop_sequences":[]
                        }
    #print(f'Reviews:{product_reviews}')
    summary = langchain.summarize_long_text(product_reviews, st.session_state.sm_assistant.boto3_bedrock, modelId, inference_config, map_prompt, combine_prompt)
    return summary

def style_figure_text(text):
    return f'<div style="font-style:italic; font-size: 0.875em; text-align:center">{text}</div>'

def load_demo():
    # Dropdown to select a product
    selected_product = st.selectbox("Select Product for summarizing reviews:", [None] + list(unique_products), index=0)

    if selected_product is not None:
        # Filter data for the selected product
        selected_data = data[data['name'] == selected_product]

        # Sort data by date in descending order
        selected_data = selected_data.sort_values(by='date', ascending=False)

        # Function to load reviews for the selected product
        def load_reviews(product_name):
            filtered_data = selected_data[selected_data['name'] == product_name]
            unique_reviews = filtered_data.drop_duplicates(subset='review')
            return unique_reviews[['date', 'rating', 'review']]
            #return selected_data[selected_data['name'] == product_name][['date', 'rating', 'review']]

        # Load reviews for the selected product
        reviews_df = load_reviews(selected_product)

        # Display reviews in a scrollable container
        if not reviews_df.empty:
            # Show "Summarize Reviews" button
            if st.button("Summarize Reviews"):
                with st.spinner("Summarizing reviews..."):
                    # Concatenate reviews
                    combine_prompt = """
                    Write a concise summary of the following product reviews.
                    Return overall sentiment of the product reviews.
                    SUMMARY:
                    SENTIMENT:
                    """
                    product_reviews = "\n".join(reviews_df['review'])
                    product_reviews = combine_prompt + product_reviews
                    summary = generate_review_summary(product_reviews, selected_product)
                    st.subheader(f"Summarized Review")
                    #styled_summary = f'<div style="color: #c3ed9d;">{summary}</div>'
                    styled_summary = f'<div class="output-text">{summary}</div>'
                    st.markdown(styled_summary, unsafe_allow_html=True)

            st.markdown("#### Product Reviews")
            for _, row in reviews_df.iterrows():
                st.write(f"Date: {row['date']}")
                st.write(f"Rating: {row['rating']}")
                st.write(f"Review: {row['review']}")
                st.write("-" * 10)

        else:
            st.warning("No reviews available for the selected product.")
    else:
        st.info("Select a product to view its reviews.")

@st.cache_data
def load_arch():
    st.write()

    st.image('data/architecture/reviews_1.png')
    st.markdown(
        '''
        When we work with large documents, we can face some challenges as the input text might not fit into the model context length, or the model hallucinates with large documents, or, out of memory errors, etc.

        To solve those problems, we are going to show an architecture that is based on the concept of chunking and chaining prompts. This architecture is leveraging [LangChain](https://python.langchain.com/docs/get_started/introduction.html) which is a popular framework for developing applications powered by language models.
        '''
    )
    st.image('data/architecture/reviews_2.png')
    st.markdown(
        '''
        In this architecture:

        1. A large document (or a giant file appending small ones) is loaded
        2. Langchain utility is used to split it into multiple smaller chunks (chunking)
        3. First chunk is sent to the model; Model returns the corresponding summary
        4. Langchain gets next chunk and appends it to the returned summary and sends the combined text as a new request to the model; the process repeats until all chunks are processed
        5. In the end, you have final summary based on entire content.

        '''
    )
    st.markdown(
        '''
        **LangChain** `load_summarize_chain` provides three ways of summarization:
        1. `stuff` puts all the chunks into one prompt. Thus, this would hit the maximum limit of tokens.
        2. `map_reduce` summarizes each chunk on it's own in a "map" step, combines the summary, and summarizes the combined summary into a final summary in "reduce" step. If the combined summary is too large, it would raise error.

        '''
    )

    st.markdown(style_figure_text('Figure Ref: <a href="https://python.langchain.com/docs/use_cases/summarization">LangChain Summarization Stuff & Map Reduce</a>')
                , unsafe_allow_html=True)
    st.image('data/architecture/summarization_lang_stuff_mapreduce.png')
    
    st.markdown('3. `refine` summarizes the first chunk, and then summarizes the second chunk with the first summary. The same process repeats until all chunks are summarized.')
    st.markdown(style_figure_text('Figure Ref: <a href="https://python.langchain.com/docs/modules/chains/document/refine">LangChain Refine Chain</a>')
                , unsafe_allow_html=True)
    st.image('data/architecture/summarization_lang_stuff_refine.png')

def main():
    with demo:
        load_demo()
    
    with arch:
        load_arch()

@st.cache_resource
def configure_logging():
    print("init logger")
    logger = logging.getLogger('retail_genai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    st.session_state.logger = logger
    return logger

if __name__ == "__main__":
    st.title("Summarize Product Reviews")
    #modelId = 'amazon.titan-tg1-xlarge'
    #modelId = 'anthropic.claude-v1'
    modelId = 'anthropic.claude-instant-v1'
    data = load_data()

    # Get unique product names
    unique_products = data['name'].unique()

    keywords = [f'Model Id: {modelId}','Amazon Bedrock API', 'Langchain']
    formatted_labels = [keyword_label(keyword) for keyword in keywords]
    st.write(' '.join(formatted_labels), unsafe_allow_html=True)
    apply_studio_style()

    # Add a description for this specific use case
    st.markdown(
        '''
        #### Use Case: 
        ###### Efficiently tackle the challenges of handling extensive product reviews with advanced summarization technique. 
        You can access the dataset used for this demo on Kaggle using the following link:
        [Indian Products on Amazon](https://www.kaggle.com/datasets/nehaprabhavalkar/indian-products-on-amazon?resource=download)

        1. **Product**: Select a product to summarize reviews for.
        2. **Summarize Reviews**: Get Summary of reviews for the product. It will both summarize long product reviews, tell the sentiment & extract important keywords.

        This architecture effective in summarizing diverse types of content, including call transcripts, meeting notes, books, articles, blog posts, and other relevant textual content. Whether you're dealing with customer feedback, evaluating product sentiment, or conducting in-depth analysis, our summarization technique can enhance your insights and decision-making processes.
        '''
    )

    demo, arch,  = st.tabs(["Demo", "Architecture"])

    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
    
    if "sm_assistant" not in st.session_state:
        st.session_state.sm_assistant = bedrock.BedrockAssistant(modelId, st.session_state.logger)
    main()