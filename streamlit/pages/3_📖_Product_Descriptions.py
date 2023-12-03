import streamlit as st
from utils.studio_style import apply_studio_style
from utils.studio_style import keyword_label
from utils import bedrock, config
import logging

st.set_page_config(
    page_title="Generate Product Descriptions",
    page_icon="🛒",
)

config.get_background()

def generate_description(product_name, product_features, persona = None):
    
    persona_prompt = ''
    if persona is not None and persona != 'None' and persona != '':
        print(f'persona: {persona}')
        persona_prompt = f" and personalize it to persona charateristics: {persona}"

    # create the prompt
    prompt_data = f"""Product: {product_name} \
    Features: {product_features} \
    Create a detailed product description for the product listed above, {persona_prompt} \
    , the product description must \
    use at least two of the listed features.\
    """

    # inference_config_titan = {
    #                             "maxTokenCount":3072,
    #                             "stopSequences":[],
    #                             "temperature":0,
    #                             "topP":0.9
    #                             }

    inference_config = {
                        "max_tokens_to_sample":4096,
                        "temperature":0,
                        "top_p":0.9,
                        "stop_sequences":[]
                        }
    
    description = st.session_state.pd_assistant.get_text(prompt_data, modelId, inference_config)
    return description

def load_demo():
    usecase, output = st.columns([1,1])
    
    with usecase:
        st.markdown(" #### Generate Description")
        # Create input elements
        product_name = st.text_input("Enter the name of the Product:", value="Sunglasses")
        example_features = "- Polarized lenses for enhanced clarity\n- Stylish and lightweight design\n- UV protection for eye safety\n- Adjustable nose pads for a comfortable fit\n- Comes with a protective case and cleaning cloth"
        product_features = st.text_area("Describe the features of the product:", value=example_features,  height=150)

        # Show persona dropdown and "Personalize Description" button
        personas = {
            "None": "",
            "Adventure Enthusiast": "Active, outdoor lover, seeks thrill",
            "Tech-Savvy": "Tech-savvy, early adopter, gadget lover",
            "Fashionista": "Fashion-forward, trendsetter, stylish",
            "Health-Conscious": "Health-conscious, wellness advocate",
            "Traveler": "Traveler, wanderlust, culture seeker"
        }
        result_label = 'Generated Description'
        selected_persona = st.selectbox("Select Persona for personalization:", list(personas.keys()), index=0)  # "None" selected by default
        persona_characteristics = ''
        if selected_persona != "None":
            st.session_state.generated_description=''
            persona_characteristics = personas[selected_persona]
            characteristics_html = f'<span style="color: #00FFFF;">{persona_characteristics}</span>'
            st.write(f"**Characteristics of {selected_persona}:**")
            st.markdown(characteristics_html, unsafe_allow_html=True)
        
        # Generate Description button
        if st.button("Generate Description"):
            with output:
                with st.spinner("Generating description..."):
                    # Process the input and generate description
                    result = generate_description(product_name, product_features, persona_characteristics)
                    
                    # Store the result in session_state
                    st.session_state.generated_description = result
                    if selected_persona != "None":
                        result_label = f'Personalized Description for {selected_persona}'
                    
                    st.markdown(f" #### {result_label}")
                    #styled_description = f'<div style="color: #62A871;">{st.session_state.generated_description}</div>'
                    styled_description = f'<div class="output-text">{st.session_state.generated_description}</div>'
                    st.markdown(styled_description, unsafe_allow_html=True)
     

    # Display the generated description if available
    #if hasattr(st.session_state, 'generated_description'):
        # st.markdown(f" #### {result_label}")
        # #styled_description = f'<div style="color: #62A871;">{st.session_state.generated_description}</div>'
        # styled_description = f'<div class="output-text">{st.session_state.generated_description}</div>'
        # st.markdown(styled_description, unsafe_allow_html=True)
        # #st.write(st.session_state.generated_description)

@st.cache_data
def load_arch():
    st.image('data/architecture/description_1.png')
    st.markdown(
        '''
        In this architecture:

        1. Prompt specifies instruction on how to generate product description
        2. Product Name and Product Features are added to the model's context to steer output
        3. OPTIONAL Persona is added to context for personalizing the generated description
        4. Amazon Bedrock API with the right LLM model is invoked to get the desired output

        '''
    )

def main():
    demo, arch,  = st.tabs(["Demo", "Architecture"])
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
    st.title("Generate Product Descriptions")
    # modelId = 'amazon.titan-tg1-xlarge'
    modelId = 'anthropic.claude-instant-v1'

    keywords = [f'Model Id: {modelId}','Amazon Bedrock API']
    formatted_labels = [keyword_label(keyword) for keyword in keywords]
    st.write(' '.join(formatted_labels), unsafe_allow_html=True)
    apply_studio_style()

       # Add a description for this specific use case
    st.markdown(
        '''
        #### Use case:
        ###### Effortlessly enhance your retail marketing strategy by crafting compelling product descriptions for improved customer engagement.

        1. **Product Name**: Input the name of your product.
        2. **Key Features**: Describe the product's features.
        3. **Persona (optional)**: Select a persona to tailor the description. Understand how the product aligns with different customer characteristics
        4. **Generate Description**: Obtain professionally written description with at least two of mentioned features.

        ''')  
    
    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
    
    if "pd_assistant" not in st.session_state:
        st.session_state.pd_assistant = bedrock.BedrockAssistant(modelId, st.session_state.logger)
    main()





