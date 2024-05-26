import streamlit as st
import os, json
from utils import bedrock
from utils.studio_style import apply_studio_style
from utils.studio_style import keyword_label
import uuid
import logging
import requests


st.set_page_config(
    page_title="AnyCompanyCommerce Shopping Agent",
    page_icon="🛍️",
)

agent_id = os.environ.get("BEDROCK_AGENT_ID",'2FGGBCRSFU')
agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID") 

welcome_message = "Hello! Welcome to AnyCompanyCommerce. I'm your AI shopping assistant here to help you find products that match your needs and interests. How can I assist you today?"

@st.cache_resource(ttl=1800)
def getAgentAssistant():
    assistant = bedrock.BedrockAssistant(modelId, st.session_state.logger)
    return assistant

def init_state():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.trace = {}
    st.session_state.email_confirmation=''
    st.session_state.agent_assistant = getAgentAssistant()
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})

@st.cache_resource(ttl=1800)
def fetch_random_users(count):
    url = f"https://n6x93z1ekf.execute-api.us-west-2.amazonaws.com/users/random?count=10"
    response = requests.get(url)
    if response.status_code == 200:
        users = response.json()
        return users
    else:
        return []

def GetAnswers(query, session_id, assistant):

    answer = assistant.invoke_agent(agent_id, agent_alias_id, session_id, query)

    return answer

def extract_email_and_body(trace):
    action_group_input = trace['invocationInput']['actionGroupInvocationInput']
    if action_group_input['apiPath'] == '/orders/{orderId}/sendEmail':
        request_body = action_group_input['requestBody']['content']['application/json']
        email = next((item['value'] for item in request_body if item['name'] == 'email'), None)
        email_body = next((item['value'] for item in request_body if item['name'] == 'emailBody'), None)
        return email, email_body
    return None, None

def load_demo():
    
    chat_container = st.container(height=350)
    
    for message in st.session_state.messages:
        # with st.chat_message(message["role"]):
        chat_container.chat_message(message["role"]).markdown(message["content"])

    user_query = st.chat_input(placeholder="Ask me anything!")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})

        # with st.chat_message("user"):
        chat_container.chat_message("user").write(user_query)
        
        with chat_container.chat_message("assistant"):
            # Add a spinner to show loading state
            with st.spinner('...'):
                response = GetAnswers(user_query, st.session_state.session_id, st.session_state.agent_assistant)
                st.markdown( response["output_text"])

                st.session_state.messages.append({"role": "assistant", "content": response["output_text"]})
                st.session_state.trace = response["trace"]


def load_trace():
    trace_type_headers = {
    "preProcessingTrace": "Pre-Processing",
    "orchestrationTrace": "Orchestration",
    "postProcessingTrace": "Post-Processing"
    }
    trace_info_types = ["invocationInput", "modelInvocationInput", "modelInvocationOutput", "observation", "rationale"]

    st.subheader("Trace")

    # Show each trace types in separate sections
    for trace_type in trace_type_headers:
        st.write(trace_type_headers[trace_type])

        # Organize traces by step similar to how it is shown in the Bedrock console
        if trace_type in st.session_state.trace:
            trace_steps = {}
            for trace in st.session_state.trace[trace_type]:
                # Each trace type and step may have different information for the end-to-end flow
                for trace_info_type in trace_info_types:
                    if trace_info_type in trace:
                        trace_id = trace[trace_info_type]["traceId"]
                        if trace_id not in trace_steps:
                            trace_steps[trace_id] = [trace]
                        else:
                            trace_steps[trace_id].append(trace)
                        break

            # Show trace steps in JSON similar to the Bedrock console
            for step_num, trace_id in enumerate(trace_steps.keys(), start=1):
                with st.expander("Trace Step " + str(step_num), expanded=False):
                    for trace in trace_steps[trace_id]:
                        trace_str = json.dumps(trace, indent=2)
                        st.code(trace_str, language="json", line_numbers=trace_str.count("\n"))
                        # st.json(trace_str)
                        
                        if 'invocationInput' in trace and 'actionGroupInvocationInput' in trace['invocationInput']:
                            email, email_body = extract_email_and_body(trace)
                            if email and email_body:
                                print("Email body:", email_body)
                                st.session_state.email_confirmation = email_body
                              
        else:
            st.text("None")

def main():
    # Initialize the messages and assistant object using session state
    if "messages" not in st.session_state or "agent_assistant" not in st.session_state:
        init_state()

    # with st.expander("Architecture"):
    #     load_arch()
        
    col1, col2,  = st.columns([2,1])
    with col1:
        st.write(f"Session ID: {st.session_state.session_id}")

    with col2:
        if st.button("Clear message history"):
            init_state()

    chat_demo, trace,  = st.tabs(["Assistant", "Trace"])
    with chat_demo:
        load_demo()
    with trace:
        load_trace()
    
    users_data = fetch_random_users(10)

    # Create a list of user options
    user_options = [""] + [f"AGE: {user['age']}, GENDER: {user['gender']}, PERSONA: {user['persona']}, DISCOUNT: {user['discount_persona']}" for user in users_data]

    # # Add a dropdown to select a user
    # selected_user = st.selectbox('Select a persona:', user_options)

    # # Display the selected user's information
    # if selected_user:
    #     selected_user_data = next((user for user in users_data if f"{user['first_name']} {user['last_name']} ({user['age']}, {user['gender']}, {user['persona']}, {user['discount_persona']})" == selected_user), None)


    if st.session_state.email_confirmation:
        st.write(st.session_state.email_confirmation)



@st.cache_resource
def configure_logging():
    print("init logger")
    logger = logging.getLogger('retail_genai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    st.session_state.logger = logger
    return logger

if __name__ == "__main__":
        
    st.title("🛍️AnyCompanyCommerce Shopping Agent")
    
    modelId = 'anthropic.claude-instant-v1'

    keywords = [f'Amazon Bedrock Agent: Anthropic Claude Sonnet', 'OpenSearch Serverless']
    formatted_labels = [keyword_label(keyword) for keyword in keywords]
    st.write(' '.join(formatted_labels), unsafe_allow_html=True)
    apply_studio_style()

    # # Add a description for this specific use case
    # st.markdown(
    #     '''
    #     #### Agent Information:
    #     ###### Welcome to the **Grocery Assistant**, your guide to planning and preparing a delicious dinner with ease. Imagine you are a valued customer of Cymbal Grocery, your favorite grocery store. You have a craving for a special dish, like lasagne, but you're not sure where to start or what ingredients you need. That's where our new conversational bot, GroceryBot, comes in!

    #     **GroceryBot** is here to assist you at every step of your dinner journey:

    #     1. **Suggesting a Recipe**: Simply tell GroceryBot the dish you'd like to cook, and it will recommend a delicious recipe for you to try. Try 'salad' or 'lasagne'

    #     2. **Getting Ingredients and Cooking Instructions**: Once you've chosen a recipe, GroceryBot will provide you with a list of ingredients and clear cooking instructions.

    #     3. **Suggesting Products**: GroceryBot will suggest products that you might want to buy for the chosen recipe, ensuring you have everything you need to cook your meal. Ask 'Help me find products to buy for the recipe'

    #     4. **Buying Products**: GroceryBot can also help you order products. Ask 'Add the products to my cart'

    #     5. **Finding New Products for Dinner**: In addition to your chosen recipe, GroceryBot can help you discover new and exciting products that would complement your dinner experience. Ask 'Do you have chocolate cake?'


    #     ''')  
    
    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
    main()