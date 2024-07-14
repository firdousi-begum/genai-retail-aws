import streamlit as st
import os, json
import re
import pandas as pd
from io import BytesIO
import base64
from utils import bedrock
from utils.studio_style import apply_studio_style
from utils.studio_style import keyword_label
import uuid
import logging
import requests
import pytz
from datetime import datetime

shopping_agent_id = os.environ.get("SHOPPING_AGENT_ID",'HZMODGWM3S')
support_agent_id = os.environ.get("SUPPORT_AGENT_ID",'TZKMQFNMOE')
agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID") 

agent_title = "🛍️AnyCompanyCommerce Shopping Agent"
# Define the options for the dropdown
agent_options = [
    {"label": "Shopping Agent", "value": shopping_agent_id},
    {"label": "Support Agent", "value": support_agent_id}
]

st.set_page_config(
    page_title=f"AnyCompanyCommerce Shopping Agent",
    page_icon="🛍️",
    layout='wide'
)


welcome_message = "Hello! Welcome to AnyCompanyCommerce. I'm your AI shopping assistant here to help you find products that match your needs and interests. How can I assist you today?"
welcome_suppport_message = "Hello! Welcome to AnyCompanyCommerce. How can I assist you today with any questions or concerns regarding our policies or services?"


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
    st.session_state.selected_product = None
    st.session_state.buy_product = None
    st.session_state.user_action = None
    st.session_state.shipping_details_provided = None
    st.session_state.answer = None

    # Get the current time in the user's timezone
    user_timezone = pytz.timezone("Europe/Stockholm")
    current_time = datetime.now(user_timezone)
    st.session_state.agent_session_state = {
        "promptSessionAttributes": {
            'firstName': 'John',
            'currentDate': str(current_time),
            'email': 'jonh.doe@xyz.com'
        },
        "sessionAttributes": {
            'email': 'jonh.doe@xyz.com'
        }
    }


@st.cache_resource(ttl=1800)
def fetch_random_users(count):
    url = f"https://n6x93z1ekf.execute-api.us-west-2.amazonaws.com/users/random?count=10"
    response = requests.get(url)
    if response.status_code == 200:
        users = response.json()
        return users
    else:
        return []

def get_product_details(product_id):
    url = f"https://n6x93z1ekf.execute-api.us-west-2.amazonaws.com/products/id/{product_id}"
    response = requests.get(url)
    if response.status_code == 200:
        product = response.json()
        return product
    else:
        return None

def GetAnswers(query, session_id, assistant, agent_id, agent_session_state):

    #answer= st.session_state.answer
    #if  st.session_state.answer is None:
    answer = assistant.invoke_agent(agent_id, agent_alias_id, session_id, agent_session_state, query)
    st.session_state.answer = answer

    return answer

def extract_email_and_body(trace):
    action_group_input = trace['invocationInput']['actionGroupInvocationInput']
    if action_group_input['apiPath'] == '/orders/{orderId}/sendEmail':
        request_body = action_group_input['requestBody']['content']['application/json']
        email = next((item['value'] for item in request_body if item['name'] == 'email'), None)
        email_body = next((item['value'] for item in request_body if item['name'] == 'emailBody'), None)
        return email, email_body
    return None, None

def reformat_product_output(response):
    products_match = re.search(r'<products>(.*?)</products>', response, re.DOTALL)
    related_products_match = re.search(r'<relatedProducts>(.*?)</relatedProducts>', response, re.DOTALL)

    products = None
    related_products = None
    
    if products_match:
        products_json = products_match.group(1)
        try:
            products = json.loads(products_json)
        except json.JSONDecodeError:
            st.error("Error parsing product data")
    
    if related_products_match:
        related_products_json = related_products_match.group(1)
        try:
            related_products = json.loads(related_products_json)
        except json.JSONDecodeError:
            st.error("Error parsing related product data")

    # Remove both <products> and <relatedProducts> tags and their contents from the response
    response = re.sub(r'<products>.*?</products>', '', response, flags=re.DOTALL)
    response = re.sub(r'<relatedProducts>.*?</relatedProducts>', '', response, flags=re.DOTALL)

    return response.strip(), products, related_products


def show_product(product):
    print('test button click')
    st.session_state.selected_product = product
    user_query = f'View details for **{product['product_name']}**'
    st.session_state.messages.append({"role": "user", "content": user_query})

def buy_product(product):
    print('test buy click')
    st.session_state.buy_product = product
    st.session_state.user_action = 'BUY_PRODUCT'
    user_query = f"Buy product : **{ product['name']}**"
    st.session_state.messages.append({"role": "user", "content": user_query})

def add_product(product):
    print('test add click')
    st.session_state.buy_product = product
    st.session_state.user_action = 'ADD_PRODUCT'
    user_query = f"Add product { product['name']} to order"
    st.session_state.messages.append({"role": "user", "content": user_query})

# The JSON object representing the shipping address structure
shipping_address_structure = {
    "email": "",
    "firstName": "",
    "lastName": "",
    "address": "",
    "city": "",
    "zipCode": "",
    "state": "",
    "country": ""
}

def submit_callback():
    form_data = {
        "Email": st.session_state.email,
        "First Name": st.session_state.first_name,
        "Last Name": st.session_state.last_name,
        "Address": st.session_state.address,
        "City": st.session_state.city,
        "Zip Code": st.session_state.zip_code,
        "State": st.session_state.state,
        "Country": st.session_state.country
    }

    # Format the form data as a string with key-value pairs, using HTML <br> tags for line breaks
    formatted_data = "<br>".join(f"{key}: {value}" for key, value in form_data.items())
    
    formatted_details = f"""
        Shipping address details: <br>
        {formatted_data}
        """

    st.session_state.messages.append({"role": "user", "content": formatted_details})
    st.session_state.shipping_details_provided = form_data

def create_shipping_form():
    with st.form("shipping_address_form"):
        st.write("## Shipping Address")
        
        # Email in a single column
        st.text_input("Email", key="email", value=st.session_state.get('email', 'john.doe@xyz.com'))
        
        # Create two columns for the form
        col1, col2 = st.columns(2)
        
        # First Name and Last Name in the same row
        with col1:
            st.text_input("First Name", key="first_name", value=st.session_state.get('first_name', 'John'))
        with col2:
            st.text_input("Last Name", key="last_name", value=st.session_state.get('last_name', 'Doe'))
        
        # Address in a single column
        st.text_input("Address", key="address", value=st.session_state.get('address', 'ABC X street'))
        
        # City and Zip Code in the same row
        with col1:
            st.text_input("City", key="city", value=st.session_state.get('city', 'Stockholm'))
        with col2:
            st.text_input("Zip Code", key="zip_code", value=st.session_state.get('zip_code', '336647'))
        
        # State and Country in the same row
        with col1:
            st.text_input("State", key="state", value=st.session_state.get('state', 'Stockholm'))
        with col2:
            st.text_input("Country", key="country", value=st.session_state.get('country', 'Sweden'))
        
    
        # Center the submit button and give it a custom width
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.form_submit_button("Submit", on_click=submit_callback,  use_container_width=True)
    

def load_demo():

    chat_container = st.container(height=450)
    
    for message in st.session_state.messages:
        # with st.chat_message(message["role"]):
        chat_container.chat_message(message["role"]).markdown(message["content"], unsafe_allow_html=True)
    
    user_query = st.chat_input(placeholder="Ask me anything!")
    if user_query:
        st.session_state.selected_product = None
        st.session_state.buy_product = None
        st.session_state.messages.append({"role": "user", "content": user_query})

        # with st.chat_message("user"):
        chat_container.chat_message("user").write(user_query)
        
        with chat_container.chat_message("assistant"):
            # Add a spinner to show loading state
            with st.spinner('...'):
                response = GetAnswers(user_query, st.session_state.session_id, st.session_state.agent_assistant, agent_option["value"], st.session_state.agent_session_state)
                print(response["output_text"])

                #formatted_response, products = reformat_product_output(response["output_text"])
                formatted_response, products, related_products = reformat_product_output(response["output_text"])
                st.markdown(formatted_response, unsafe_allow_html=True)
                if products:
                    # Add a separator
                    st.markdown("---")
                    # Display the products as a list
                    st.write("Suggested Products:")
                    products_history= f""" """
                    for i, product in enumerate(products, 1):
                        products_history += f"""
                        | <img src="{product["image_url"]}" width="100" alt="{product["product_name"]}"> | {i}. **{product["product_name"]}** | Price: ${product["price"]} |
                        """

                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(product['image_url'])
                        with col2:
                            st.write(f"{i}. {product['product_name']}")
                            st.write(f"${product['price']}")
                            st.button(f"View Details", key=f"show_{product['product_id']}", on_click=show_product, args=(product,))
                
                if related_products:
                    # Add a separator
                    st.markdown("---")
                    # Display the products as a list
                    st.write("Products you might like:")
                    related_products_history= f""" """
                    for i, product in enumerate(related_products, 1):
                        related_products_history += f"""
                        | <img src="{product["image_url"]}" width="100" alt="{product["product_name"]}"> | {i}. **{product["product_name"]}** | Price: ${product["price"]} |
                        """

                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(product['image_url'])
                        with col2:
                            st.write(f"{i}. {product['product_name']}")
                            st.write(f"${product['price']}")
                            st.button(f"View Details", key=f"show_{product['product_id']}", on_click=show_product, args=(product,))


                #st.markdown( response["output_text"])
                #st.session_state.messages.append({"role": "assistant", "content": response["output_text"]})

                st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                if products:
                    st.session_state.messages.append({"role": "assistant", "content": products_history})
                if related_products:
                    st.session_state.messages.append({"role": "assistant", "content": related_products_history})

                st.session_state.trace = response["trace"]

    if st.session_state.buy_product:
        product_to_buy = st.session_state.buy_product
        if st.session_state.user_action == 'BUY_PRODUCT':
            query = f"I want to buy product { product_to_buy['name']}"
        else:
            query = f"I want to add product { product_to_buy['name']} to the order"
        
        if st.session_state.shipping_details_provided is not None:
            data = st.session_state.shipping_details_provided
            query+= f"""

                <shipping_address>
                {json.dumps(data, indent=2)}
                </shipping_address>
            """

        with chat_container.chat_message("assistant"):
            # Add a spinner to show loading state
            with st.spinner('...'):
                if st.session_state.shipping_details_provided is None:
                    st.markdown("Please provide your shipping address details:")
                    # Use a container with custom width for the form
                    with st.container():
                        _, col, _ = st.columns([1, 2, 1])  # This creates a centered column
                        with col:
                            create_shipping_form()
                else:
                    st.session_state.buy_product = None
                    response = GetAnswers(f"{query} with id {product_to_buy['id']}", st.session_state.session_id, st.session_state.agent_assistant, agent_option["value"], st.session_state.agent_session_state)
                    print(response["output_text"])
                    st.markdown(response["output_text"])
                    st.session_state.messages.append({"role": "assistant", "content": response["output_text"]})

    # Display selected product details
    if st.session_state.selected_product:
        product_id = st.session_state.selected_product['product_id']
        with chat_container.chat_message("assistant"):  
            with st.spinner('...'):
                st.session_state.selected_product = None
                product = get_product_details(product_id)

                print(product)

                if product: 
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.image(product['image'], width=500)
                        st.write(f"<small>{product['description']}</small>", unsafe_allow_html=True)
                    with col2:
                        st.write(f"#### {product['name']}")
                        st.write(f"<small>Category: {product['category'].capitalize()} | Style: {product['style'].capitalize()}</small>", unsafe_allow_html=True)
                        st.write(f"${product['price']:.2f}")
                        if 'promoted' in product and product['promoted'] == "True":
                            st.write("🔥 **Promoted Item**")
                        if product['current_stock'] > 0:
                            col1, col2 = st.columns(2)
                            with col1:
                                 st.button("Buy Now", key=f"buy_{product['id']}", on_click=buy_product, args=(product,))
                            # with col2:
                            #      st.button("Add to Order", key=f"add_{product['id']}", on_click=add_product, args=(product,))
                           
                            # if st.button("Buy Now", key=f"buy_{product['id']}"):
                            #     st.success(f"{product['name']} added to cart!")
                        else:
                            st.write("**Out of Stock**")
                        st.write(f"<small>Current Stock: {product['current_stock']} units</small>", unsafe_allow_html=True)


                    if product['aliases']:
                        st.write("<small>**Also known as:** " + ", ".join(product['aliases']) + "</small>", unsafe_allow_html=True)
                    
                    # Add exploration to message history
                    selected_content = f"""
                    <img src="{product['image']}" width="300" alt="{product['name']}"> 

                    #### {product['name']}

                    Category: {product['category'].capitalize()} | Style: {product['style'].capitalize()}  
                    {'🔥 **Promoted Item**' if 'promoted' in product and product['promoted'] == "True" else ''}

                    Price: ${product['price']:.2f}

                    Current Stock: {product['current_stock']} units

                    Description: 
                    {product['description']}
                    """
                    if product['aliases']:
                        selected_content += f"\n\n**Also known as:** {', '.join(product['aliases'])}"
                    
                    st.session_state.messages.append({"role": "assistant", "content": selected_content})
                else:
                    error = 'Apologies, there seems to be temporary issues in getting product details at the moment. Please try again later.'
                    st.session_state.messages.append({"role": "assistant", "content": error})
            


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

def load_session():
    st.write(f"Session ID: {st.session_state.session_id}")
    if st.session_state.agent_session_state:
        st.json(st.session_state.agent_session_state)

def main():
    # Initialize the messages and assistant object using session state
    if "messages" not in st.session_state or "agent_assistant" not in st.session_state:
        init_state()

    # with st.expander("Architecture"):
    #     load_arch()
        
    # col1, col2,  = st.columns([2,1])
    # with col1:
    #     st.write(f"Session ID: {st.session_state.session_id}")

    # with col2:
    #     if st.button("Clear message history"):
    #         init_state()

    chat_demo, session, trace,  = st.tabs(["Assistant", "Session", "Trace"])
    with session:
        load_session()
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
    

agent_option = st.sidebar.selectbox("Select an agent", agent_options, format_func=lambda option: option["label"])
if agent_option['label'] == "Support Agent":
    agent_title = "👩‍💼AnyCompanyCommerce Support Agent"
    welcome_message = welcome_suppport_message


@st.cache_resource
def configure_logging():
    print("init logger")
    logger = logging.getLogger('retail_genai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    st.session_state.logger = logger
    return logger

if __name__ == "__main__":
        
    st.title(agent_title)
    
    modelId = 'anthropic.claude-instant-v1'

    keywords = [f'Amazon Bedrock Agent: Anthropic Claude Sonnet', 'OpenSearch Serverless']
    formatted_labels = [keyword_label(keyword) for keyword in keywords]
    col1, col2,  = st.columns([2,1])
    with col1:
        st.write(' '.join(formatted_labels), unsafe_allow_html=True)

    with col2:
        if st.button("Clear message history"):
            init_state()

    apply_studio_style()

    
    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
    main()