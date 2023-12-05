import json
import boto3
import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import base64
import uuid
import os
from utils import bedrock, stability
from stability_sdk.api import GenerationRequest, GenerationResponse, TextPrompt
from PIL import Image
from typing import Union
from utils.products import prompts_data_idea, adapter_data
from utils.studio_style import apply_studio_style
from utils.studio_style import keyword_label
from utils import config
import io
import base64
import logging
# End SDXL imports

st.set_page_config(page_title="Product Ideator", page_icon="high_brightness")
config.get_background()

if "st1_assistant" not in st.session_state:
    st.session_state.st1_assistant = None
if "bedrock_assistant" not in st.session_state:
    st.session_state.bedrock_assistant = None
if 'image' not in st.session_state:
    st.session_state.image = None
if 'text_model_id' not in st.session_state:
    st.session_state.text_model_id = ''

endpointName ='sdxl-jumpstart-1-2023-08-30-23-25-11-865'

#languages = ['English', 'Spanish', 'German', 'Portugese', 'Korean', 'Star Trek - Klingon', 'Star Trek - Ferengi', 'Italian', 'French', 'Japanese', 'Mandarin', 'Tamil', 'Hindi', 'Telugu', 'Kannada', 'Arabic', 'Hebrew']
languages = ['English', 'Spanish', 'German', 'Portugese', 'Irish', 'Korean', 'Swedish', 'Norwegian', 'Danish', 'Icelandic', 'Finnish', 'Star Trek - Klingon', 'Star Trek - Ferengi', 'Italian', 'French', 'Japanese', 'Mandarin', 'Tamil', 'Hindi', 'Telugu', 'Kannada', 'Arabic', 'Hebrew']


# Create tabs
prompts, params = st.sidebar.tabs(["Prompts", "Parameters"])


# List of generation types
generation_types = ["TEXT_IMAGE", "ADAPTER"]

providers = ['Amazon Bedrock API', 'Amazon SageMaker JumpStart']
models = {
    "Amazon Bedrock API": [
    "stability.stable-diffusion-xl-v1",
    "amazon.titan-image-generator-v1",
    
    ],
    "Amazon SageMaker JumpStart": [
        "sdxl-jumpstart-1-2023-08-30-23-25-11-865",
        "huggingface-pytorch-inference-2023-11-12-17-36-53-941"
    ]
}

negative_prompt = "ugly, tiling, poorly drawn hands, out of frame, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low quality, bad art, beginner, windy, amateur, distorted"


def encode_image(image_path: str, resize: bool = True, thumbnail : bool = True) -> Union[str, None]:
    try:
        if resize:
            image = Image.open(image_path)
            image = image.convert("RGB")
            # Get the original width and height
            original_width, original_height = image.size
            #image = image.resize((512, 512))
            # Calculate the new width and height that are multiples of 64
            new_width = original_width - (original_width % 64)
            new_height = original_height - (original_height % 64)

            # Calculate the new pixel count
            new_pixel_count = new_width * new_height

            # Check if the new pixel count exceeds the maximum allowed
            if new_pixel_count > 1048576:
                # Reduce the width and height while maintaining the aspect ratio
                aspect_ratio = original_width / original_height
                new_height = int((1048576 / aspect_ratio) ** 0.5)
                new_width = int(aspect_ratio * new_height)

                # Ensure the new width and height are multiples of 64
                new_width = new_width - (new_width % 64)
                new_height = new_height - (new_height % 64)

            # Resize the image to the new height while preserving the aspect ratio
            image = image.resize((new_width, new_height), Image.LANCZOS)

            # Save the resized image temporarily
            image_resized_path = "image_base_resized.png"
            image.save(image_resized_path)

            if thumbnail:
                # Create a thumbnail without specifying a fixed size to maintain aspect ratio
                image.thumbnail((new_width // 3, new_height // 3), Image.LANCZOS)
                st.image(image)

            # Read and encode the resized image
            with open(image_resized_path, "rb") as image_file:
                img_byte_array = image_file.read()
                base64_str = base64.b64encode(img_byte_array).decode("utf-8")
                return base64_str
        else:
            # Read and encode the original image
            with open(image_path, "rb") as image_file:
                img_byte_array = image_file.read()
                base64_str = base64.b64encode(img_byte_array).decode("utf-8")
                return base64_str
    except Exception as e:
        #print(f"Failed to encode image {image_path} as a base64 string.")
        print(e)
        return None


def generateImages(query):
    generation_params = GenerationRequest(text_prompts=[TextPrompt(text=query), TextPrompt(text=negative_prompt, weight=-1)],
                                             style_preset="digital-art",
                                             seed = 1885337276,
                                             steps=70,
                                             cfg_scale=10,
                                             width=1024,
                                             height= 1024
                                             )
    if st.session_state.mode == 'Amazon Bedrock API':
        return st.session_state.bedrock_assistant.generate_image(st.session_state.modelId
                                           ,generation_params
                                           ,generation_type = st.session_state.generation_type
                                           , negative_prompt= negative_prompt)
    else:
        return st.session_state.st1_assistant.generate(generation_params,endpoint_name= st.session_state.modelId)


def sdxl_decode_and_show(model_response: GenerationResponse) -> None:
    """
    Decodes and displays an image from SDXL output

    Args:
        model_response (GenerationResponse): The response object from the deployed SDXL model.

    Returns:
        None
    """
    #print(model_response)
    for idx, artifact in enumerate(model_response, start=1):
        #st.write(f"Generated Image {idx}:")
        image = artifact.base64
        image_data = base64.b64decode(image.encode())
        image = Image.open(io.BytesIO(image_data))

    return image




def parse_im_response(query_im_response):
    response_dict = json.loads(query_im_response['Body'].read())
    return response_dict['generated_images'], response_dict['prompt']


def call_bedrock_titan(prompt_text, max_token_count=1024, temperature=1, top_p=1, stop_sequences=[]):
    model_id = "amazon.titan-tg1-large"
    st.session_state.text_model_id =model_id

    body_string = "{\"inputText\":\"" + f"{prompt_text}" +\
                    "\",\"textGenerationConfig\":{" +\
                    "\"maxTokenCount\":" + f"{max_token_count}" +\
                    ",\"temperature\":" + f"{temperature}" +\
                    ",\"topP\":" + f"{top_p}" +\
                    ",\"stopSequences\":" + f"{stop_sequences}" +\
                    "}}"
    body = bytes(body_string, 'utf-8')
    result_text = st.session_state.bedrock_assistant.get_text_t(body, model_id)

    return result_text


def call_bedrock_claude_2(prompt_text, max_tokens_to_sample=1024, temperature=1, top_k=250, top_p=1):
    model_id = "anthropic.claude-v2"
    st.session_state.text_model_id = model_id

    body = {
        "prompt": "Human:"+prompt_text+"\n\nAssistant:",
        "max_tokens_to_sample": max_tokens_to_sample
    }
    body_string = json.dumps(body)
    body = bytes(body_string, 'utf-8')

    result_text = st.session_state.bedrock_assistant.get_text_t(body, model_id)

def call_bedrock_claude_1(prompt_text, max_tokens_to_sample=1024, temperature=1, top_k=250, top_p=1):
    model_id = "anthropic.claude-v1"
    print('hello CLAUDE 1')
    st.session_state.text_model_id = model_id

    body = {
        "prompt": "Human:"+prompt_text+"\n\nAssistant:",
        "max_tokens_to_sample": max_tokens_to_sample
    }
    body_string = json.dumps(body)
    body = bytes(body_string, 'utf-8')

    result_text = st.session_state.bedrock_assistant.get_text_t(body, model_id)

def call_bedrock_claude_2_1(prompt_text, max_tokens_to_sample=1024, temperature=1, top_k=250, top_p=1):
    model_id = "anthropic.claude-v2:1"
    print('hello CLAUDE 2.1')
    st.session_state.text_model_id = model_id

    body = {
        "prompt": "Human:"+prompt_text+"\n\nAssistant:",
        "max_tokens_to_sample": max_tokens_to_sample
    }
    body_string = json.dumps(body)
    body = bytes(body_string, 'utf-8')

    result_text = st.session_state.bedrock_assistant.get_text_t(body, model_id)
    
   
    # response = bedrock.invoke_model(
    #     modelId = model_id,
    #     contentType = "application/json",
    #     accept = "application/json",
    #     body = body)
    # response_lines = response['body'].readlines()
    # json_str = response_lines[0].decode('utf-8')
    # json_obj = json.loads(json_str)
    # result_text = json_obj['completion']
    return result_text


def call_bedrock_jurassic(prompt_text, max_token_count=1024, temperature=1, top_p=1, stop_sequences=[]):
    model_id = "ai21.j2-jumbo-instruct"

    st.session_state.text_model_id = model_id

    body_string = "{\"prompt\":\"" + f"{prompt_text}" + "\"" +\
                    ",\"maxTokens\":" + f"{max_token_count}" +\
                    ",\"temperature\":"  + f"{temperature}" +\
                    ",\"topP\":" + f"{top_p}" +\
                    ",\"stopSequences\":" + f"{stop_sequences}" +\
                    ",\"countPenalty\":{\"scale\":0}" +\
                    ",\"presencePenalty\":{\"scale\":0}" +\
                    ",\"frequencyPenalty\":{\"scale\":0}" +\
                    "}"    
    body = bytes(body_string, 'utf-8')
    
    result_text = st.session_state.bedrock_assistant.get_text_t(body, model_id)
    
   
    # response = bedrock.invoke_model(
    #     modelId = model_id,
    #     contentType = "application/json",
    #     accept = "application/json",
    #     body = body)
    # response_lines = response['body'].readlines()
    # json_str = response_lines[0].decode('utf-8')
    # json_obj = json.loads(json_str)
    # result_text = json_obj['completions'][0]['data']['text']
    return result_text


text_models = {
    "bedrock titan" : call_bedrock_titan,
    "bedrock claude 2" : call_bedrock_claude_2,
    "bedrock claude instant 1" : call_bedrock_claude_2,
    "bedrock claude 2.1" : call_bedrock_claude_2_1,
    "bedrock claude" : call_bedrock_claude_1,
    "bedrock jurassic-2" : call_bedrock_jurassic
}



def GetAnswers(query, industry):
    # pii_list = []
    # #sentiment = comprehend.detect_sentiment(Text=query, LanguageCode='en')['Sentiment']
    # resp_pii = comprehend.detect_pii_entities(Text=query, LanguageCode='en')
    # for pii in resp_pii['Entities']:
    #     if pii['Type'] not in ['NAME', 'AGE', 'ADDRESS','DATE_TIME']:
    #         pii_list.append(pii['Type'])
    # if len(pii_list) > 0:
    #     answer = "I am sorry but I found PII entities " + str(pii_list) + " in your query. Please remove PII entities and try again."
    #     return answer
    query_type = ''
    
    if query == "cancel":
        answer = 'It was well interacting with you. Thanks for your time.'
        return answer
    else:
        # Call the Stability model to get the image for our query, save it in S3 and build a response card
        #response = query_im_endpoint("Detailed image of " + query+" in " + industry.lower())
        #timg, prmpt = parse_im_response(response)
        #generated_image_decoded = BytesIO(base64.b64decode(timg[0].encode()))
        #generated_image_rgb = Image.open(generated_image_decoded).convert("RGB")
        #img_url_new = save_image(generated_image_rgb, prmpt)
       
        sd_query = "Generate a detailed image of " + query+" in " + industry.lower() 

        image = generateImages(sd_query)[0]
        st.session_state.image = image
        # Save the image temporarily
        image_path = "image_generated.jpeg"
        image.save(image_path)
        #st.image(img_url_new)
        st.write("**Example image for your product idea**: \n")
        st.image(st.session_state.image)
        generated_text = ''
        answer=''
        prompt_text = 'Create a product description in '+st.session_state.language+' in 200 words for '+ query.strip("query:")
        func = text_models[st.session_state.text_model.lower()]
        answer = func(prompt_text)
        answer = answer.replace("$","\$")   
        return answer    

def adaptImage(
    img_str,
    prompt: str,
    seed: int = 0,
    num_inference_steps: int = 30,
    adapter_conditioning_scale: float = 0.9,
    adapter_conditioning_factor: float = 1.0,
    guidance_scale: float = 7.5):
        negative_prompts = "ugly, tiling, poorly drawn hands, out of frame, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low quality, bad art, beginner, windy, amateur, distorted"
        output = st.session_state.st1_assistant.adapt(
                                                     img_str,
                                                     prompt,
                                                     negative_prompts,
                                                     seed, 
                                                     num_inference_steps, 
                                                     adapter_conditioning_scale,
                                                     adapter_conditioning_factor, 
                                                     guidance_scale,
                                                     endpoint_name = st.session_state.modelId)
        output.save('adapted_image.png')
        return output                  

def getAgent():
    modelId = st.session_state.modelId
    assistant = stability.StabilityAssistant(models['Amazon SageMaker JumpStart'][0])
    b_assistant = bedrock.BedrockAssistant(modelId,st.session_state.logger)
    return assistant, b_assistant

def load_sidebar():
    prompts.header("Product ideator")
    selected_generation_type = prompts.selectbox("Select Generation Type", generation_types, key="generation_type" )

    mode_index = 0
    model_index = 0
    if selected_generation_type == "ADAPTER":
        mode_index = providers.index('Amazon SageMaker JumpStart')
        model_index = models['Amazon SageMaker JumpStart'].index('huggingface-pytorch-inference-2023-11-12-17-36-53-941')
    
    mode_type = prompts.selectbox("Select Image Generator", providers, index=mode_index, key="mode")
    modelIds = [item for item in models[mode_type]]
    model = prompts.selectbox("Select Image Model", modelIds, index =model_index, key="modelId")

    keywords = [f'Model: {st.session_state.modelId}',f'{st.session_state.mode}']
    formatted_labels = [keyword_label(keyword) for keyword in keywords]
    st.write(' '.join(formatted_labels), unsafe_allow_html=True)
    apply_studio_style()

    prompts.markdown("### Make your pick")
    idea = ''
    industry = ''
    industry = prompts.selectbox(
        'Select an industry',
        ('Retail', 'Fashion', 'Manufacturing', 'Technology', 'Transport'), key='industry')
    if st.session_state.generation_type == "TEXT_IMAGE":
        st.write("**Instructions:** \n - Type a product idea prompt \n - You will see an image, a product description, and press release generated for your product idea")

        product_idea =''
        if industry and industry != "NONE":
            prompt_titles = [item["Prompt Title"] for item in prompts_data_idea[industry]]
            product_idea = prompts.selectbox("Select an example Product", prompt_titles, key="prompt_title")


        fms = ['Bedrock Claude Instant 1','Bedrock Claude 2.1','Bedrock Claude','Bedrock Claude 2','Bedrock Jurassic-2']
        default_model = fms.index('Bedrock Claude 2.1')
        text_model = prompts.selectbox(
            'Select a Text FM',
            options=fms, index=default_model, key="text_model")
        
        for prompt in prompts_data_idea[industry]:
            if prompt["Prompt Title"] == product_idea:
                product_html = f'#### <span style="color: #00FFFF;"> Product Idea: {product_idea}</span>'
                st.markdown(product_html, unsafe_allow_html=True)
                selected_prompt = prompt
                idea = selected_prompt['Prompt']
        input_text = st.text_area('**What is your product idea?**', key='prod_text', value=idea)
        default_lang_ix = languages.index('English')
        language = st.selectbox(
            '**Select an output language.** Only Alpha and Beta quadrant languages supported. For new requests, please contact C-3PO',
            options=languages, index=default_lang_ix, key ="language")
        key_phrases = ''

    elif st.session_state.generation_type == "ADAPTER":
        st.write("**Instructions:** \n - Upload your image \n - Type a prompt to adapt it to new color or design, you will see your idea come to life.")

        product_idea =''
        if industry and industry != "NONE":
            prompt_titles = [item["Prompt Title"] for item in adapter_data[industry]]
            product_idea = prompts.selectbox("Select an example Product", prompt_titles, key="prompt_title")

        image = ''
        
        init_image = st.file_uploader("Upload Initial Image", type=["jpg", "jpeg", "png"])
        if init_image is None:
            for prompt in adapter_data[industry]:
                if prompt["Prompt Title"] == product_idea:
                    product_html = f'#### <span style="color: #00FFFF;"> Product Idea: {product_idea}</span>'
                    st.markdown(product_html, unsafe_allow_html=True)
                    selected_prompt = prompt
                    idea = selected_prompt['Prompt']
                    image = encode_image(selected_prompt['Image_Source'])
                    st.session_state.init_image = image

        
        if init_image is not None:
            image = encode_image(init_image)
            st.session_state.init_image = image

        input_text = st.text_area('**What is your product idea?**', key='prod_text', value=idea)



    
def main():
    # Streamlit app layout
    
    st.markdown("# Take your product idea to the next level")

    load_sidebar()
                    
  
    if st.session_state.st1_assistant is None or st.session_state.bedrock_assistant is None:
        st.session_state.st1_assistant, st.session_state.bedrock_assistant = getAgent()

  

    # Generate button
    if st.button("Ideate"):
        st.session_state.image=''
        if st.session_state.prod_text != '' and st.session_state.generation_type == "TEXT_IMAGE":
            with st.spinner("Generating Product Idea..."):
                result = GetAnswers(st.session_state.prod_text, st.session_state.industry)

            result = result.replace("$","\$")
            tab1, tab2, tab3, tab4 = st.tabs(["Product description", "Internal memo", "Press release", "Social Media Ad"])
            #c1, c2 = st.columns(2)
            with tab1:
                st.write("**Description for your product idea**")
                st.write(result)
            with tab2:
                st.write("**Internal memo for your product idea**")
                prompt_text = 'Generate an internal memo announcing the launch decision in '+st.session_state.language+' for '+ st.session_state.prod_text.strip("query:")
                func = text_models[st.session_state.text_model.lower()]
                answer = func(prompt_text)
                answer = answer.replace("$","\$") 
                st.write(answer)
            with tab3:
                st.write("**Press release for your product idea**")
                prompt_text = 'Generate a press release and some FAQs to help understand the product better in '+st.session_state.language+' for '+ st.session_state.prod_text.strip("query:")
                func = text_models[st.session_state.text_model.lower()]
                answer = func(prompt_text)
                answer = answer.replace("$","\$") 
                st.write(answer)
            with tab4:
                st.write("**Social Media Ad for your product idea**")
                prompt_text = 'Generate a catchy trendy social media ad in '+st.session_state.language+' for '+ st.session_state.prod_text.strip("query:")
                func = text_models[st.session_state.text_model.lower()]
                answer = func(prompt_text)
                answer = answer.replace("$","\$") 
                st.write(answer)
                #st.balloons()       
        elif st.session_state.generation_type == "ADAPTER":
            with st.spinner("Generating Product Idea..."):
                st.image(
                    adaptImage( st.session_state.init_image,st.session_state.prod_text)
                )
                # if st.session_state.image is not None:
                #     # if st.button("Adapt"):
                #     #     with st.spinner("Adapting Product Idea..."):
                #     #         st.image(
                #     #             adaptImage( encode_image("image_generated.jpeg", True, False),st.session_state.prod_text)
                #     #         )

                #     st.write("**Example image for your product idea**: \n")
                #     st.image(st.session_state.image)
       
            


@st.cache_resource
def configure_logging():
    print("init logger")
    logger = logging.getLogger('retail_genai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    st.session_state.logger = logger
    return logger

if __name__ == "__main__":
    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
    main()
        