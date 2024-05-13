import streamlit as st
from utils import grocery_agent_tools
from utils.studio_style import apply_studio_style
from utils.studio_style import keyword_label
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.tools import tool
import logging

st.set_page_config(
    page_title="Grocery Assistant",
    page_icon="🛒",
)


assistant =None
recipe_retriever = None
product_retriever = None
tools = None
# Initialize the assistant object using session state
if "gc_assistant" not in st.session_state:
    st.session_state.gc_assistant = None
if "recipe_retriever" not in st.session_state:
    st.session_state.recipe_retriever = None
if "product_retriever" not in st.session_state:
    st.session_state.product_retriever = None
if "gc_tools" not in st.session_state:
    st.session_state.gc_tools = None
# Initialize shopping cart in session state
if "gc_shopping_cart" not in st.session_state:
    st.session_state.gc_shopping_cart = []

# Sidebar section
#st.sidebar.title("Shopping Cart")

result_label = 'Generated Description'
# Setup memory for contextual conversation
gc_msgs = StreamlitChatMessageHistory()
# dynamo = DynamoDBMemory(table_name="langchain-memory")
# memory = dynamo.get_memory(session_id = conversation_id, k=4 )
memory = ConversationBufferMemory(memory_key="chat_history", k=3, ai_prefix="Assistant", chat_memory=gc_msgs, return_messages=True)

def GetAnswers(query, tools, assistant):
    # answer = detect.detect_sentiment_pii(query)
    # if answer:
    #     return answer

    #print(f'tools: {tools}')
    # inference_config_titan = {
    #                         "maxTokenCount":3072,
    #                         "stopSequences":[],
    #                         "temperature":0,
    #                         "topP":0.9
    #                         }
    inference_config = {
                        "max_tokens_to_sample":4096,
                        "temperature":0,
                        "top_p":0.9,
                        "stop_sequences":['Human:']
                        }

    answer = assistant.grocery_conversation_bot(tools, query, modelId, inference_config, memory)

    return answer

@tool (return_direct=True)
def find_recipes(query: str) -> str:
    """
    Use this ONLY when user asks for finding recipes otherwise use 'find_products' tool.
    Return the output without processing further.
    """
    print('begin')
    docs = st.session_state.recipe_retriever.get_relevant_documents(query)
    markdown_list = ", ".join([f"{st.session_state.gc_assistant.get_name(doc.metadata['source'])}" for doc in docs])
    #print(f'recipies: {markdown_list}')
    res = f'Select the recipe you would like to explore further about {query}: \n\n {markdown_list}'

    return res

@tool(return_direct=True)
def add_products_to_cart(products: str) -> str:
    """
    Use it when the user asks for adding the products to shopping cart or buy products. For example `Can you add the products to cart?`
    """
    st.session_state.gc_shopping_cart.append(products)
    # st.sidebar.markdown(f"### Shopping cart:")
    # new_items =  "\n ".join([f"- {item}" for item in st.session_state.gc_shopping_cart])
    # st.sidebar.write(new_items)

    st.sidebar.success(f"Added '{products}' to the cart!")
    #st.session_state.logger.info(f'recipies: {markdown_list}')
    res = f'Added products {products} to cart'

    return res
    
@tool(return_direct=True)
def find_products(query: str) -> str:
    """
    Use it whenever the user enquires about specific products or asks for its availability. For example `Can you show me which onions I can buy?`
    """
    docs = st.session_state.product_retriever.get_relevant_documents(query)
    #print (f"doc metadata: {get_name(docs[0].metadata['source'])}")
    markdown_list = ", ".join([f"{st.session_state.gc_assistant.get_name(doc.metadata['source'])}" for doc in docs])

    #output =  f"I found these products about {query}: {markdown_list}"
    output =  f"{markdown_list}"
    return output

@tool
def recipe_selector(name: str) -> str:
    """
    Use this when the user selects a recipe.
    You will need to respond to the user telling what are the options once a recipe is selected.
    You can explain what are the ingredients of the recipe, show you the cooking instructions or suggest you which products to buy from the catalog!
    """
    return "Great choice! I can explain what are the ingredients of the recipe, show you the cooking instructions or suggest you which products to buy from the catalog!"

@tool
def get_recipe_detail(name: str) -> str:
    """
    Use it to find more information for a specific recipe, such as the ingredients or the cooking steps.
    Use this to find what are the ingredients for a recipe or the cooking steps.

    Would you like me to show you the suggested products from the catalogue?
    """
    try:
        print(f'in method: {st.session_state.gc_assistant.recipes_detail}')
        details = st.session_state.gc_assistant.recipes_detail[name]
        #print('details: '+ details)
        return details
    except KeyError:
        return "Could not find the details for this recipe"
    
@tool
def get_product_detail(name: str) -> str:
    """
    Use it when user asks for more information for a specific product, such as the size, weight, nutrition, benefits or description.
    """
    try:
        print(f'in method: {st.session_state.gc_assistant.products_detail}')
        details = st.session_state.gc_assistant.products_detail[name.lower()]
        #print('details: '+ details)
        return details
    except KeyError:
        return "Could not find the details for this product"

@tool(return_direct=True)
def get_suggested_products_for_recipe(recipe_name: str) -> str:
    """"Use this only if the user would like find certain products connected to a specific recipe to buy.
     For example 'Can you give me the products I can buy for the lasagne?'"
    """
    try:
        # recipe_to_product_mapping = {
        #     "./recipes/lasagne.txt": [
        #         "./products/angus_beef_lean_mince.txt",
        #         "./products/large_onions.txt",
        #         "./products/classic_carrots.txt",
        #         "./products/classic_tomatoes.txt",
        #     ]
        # }
        recipe_name = recipe_name.replace("_", " ")
        recipe_to_product_mapping = {
            "traditional lasagne": "angus beef lean mince, large onions, classic carrots, classic tomatoes",
            "vegetarian lasagne": "spinach, soya chunk, large onions, classic carrots, classic tomatoes",
            "chicken scallopini with asparagus": "onion, chicken, celery, asparagus, vinegar, cherry vine tomatoes",
            "steak and peanut salad": "steak, peanut, large onions, classic carrots, classic tomatoes"
        }
        output = f"These are some suggested ingredients for your recipe: \n\n {str(recipe_to_product_mapping[recipe_name.lower()])}"
        #output = f"{str(recipe_to_product_mapping[recipe_name])}"
        return output
    except KeyError:
        return "Could not find ingredients for this recipe"

@st.cache_resource(ttl=1800)
def getAgent():
    assistant = grocery_agent_tools.GroceryAssistant(modelId, st.session_state.logger)
    
    tools = [
                find_recipes,
                add_products_to_cart,
                find_products,
                get_product_detail,
                get_recipe_detail,
                get_suggested_products_for_recipe,
                #recipe_selector,
            ]
    return assistant, tools

@st.cache_resource
def get_retriever():
    assistant = st.session_state.gc_assistant
    recipe_retriever = assistant.create_retriever(top_k_results=2, dir_path="./data/grocery-bot/recipies/*")
    product_retriever = assistant.create_retriever(top_k_results=3, dir_path="./data/grocery-bot/products/*")
    return recipe_retriever, product_retriever

def load_demo():
    if len(gc_msgs.messages) == 0 or st.sidebar.button("Clear message history"):
        #print('clear')
        gc_msgs.clear()
        #getAgent.clear()
        st.session_state.gc_assistant = None
        st.session_state.gc_shopping_cart = []
        gc_msgs.add_ai_message(f"How can I help you?")

    avatars = {"human": "user", "ai": "assistant"}
    for msg in gc_msgs.messages:
        st.chat_message(avatars[msg.type]).write(msg.content)
        
    if user_query := st.chat_input(placeholder="Ask me anything!"):
        st.chat_message("user").write(user_query)
        #if st.session_state.gc_assistant is None:  # Check if assistant is uninitialized
        assistant,  tools = getAgent()
        if assistant:
            st.session_state.gc_assistant = assistant  # Store the assistant in session state
            st.session_state.gc_tools = tools
            if st.session_state.product_retriever is None or st.session_state.recipe_retriever is None:
                st.session_state.recipe_retriever, st.session_state.product_retriever = get_retriever()
             

        with st.chat_message("assistant"):
            response = GetAnswers(user_query, st.session_state.gc_tools, st.session_state.gc_assistant)
            st.markdown(response)

    if st.session_state.gc_shopping_cart is not None and len(st.session_state.gc_shopping_cart) >0:
        st.sidebar.markdown(f"### Shopping cart:")
        new_items =  "\n ".join([f"- {item}" for item in st.session_state.gc_shopping_cart])
        st.sidebar.write(new_items)

@st.cache_data
def load_arch():
    st.image('data/architecture/grocery_assistant_1.png')
    st.markdown(
        '''
        In this architecture:

        1. Prompt is the user query about finding recipes and products.
        2. Recipe Details and Product Details are added to the model's context to steer output.
        3. RAG (Retrieval Augmented Generation) mechanism is used to retrieve relavant recipe and related products for adding to the context.
        4. Amazon Bedrock API with the right LLM model is invoked to get the desired output.

        '''
    )
    st.write("\n\n")
    st.image('data/architecture/grocery_assistant_2.png')
    st.markdown(
        '''
        For RAG:

        1. Recipe and product details are embedded to vector using Amazon Titan Embeddings model.
        2. Resultant vectors are stored in FAISS vector database.
        3. When user queries for finding products to buy for a specific recipe, the recipe ingredients are embedded to vector and searched against products vector in FAISS. 
        4. The resultant products from vector search is then returned to user.
        5. Similar mechanism is used to find products based on diet preference.

        '''
    )

    st.write("\n\n")

    st.markdown(
        '''

        For giving additional capabilities to GroceryBot such as 'Ordering Products', we needt to give access to more tools:

        1. For that we will use a pattern or framework called ReAct (Reasoning & Action) together with Langchain
        2. The ReAct framework could enable large language models to interact with multiple external tools to obtain additional information that results in more accurate and fact-based responses and Langchain provides Off-the-shelf chains, components & abstractions make it easy to get started. 
        3. We add more tools to our GroceryBot such as "Add to Cart" API to help ordering products.

        '''
    )

    st.write("\n\n")
    st.image('data/architecture/grocery_assistant_3.png')
    st.markdown(
        '''

        When user asks for 'Adding products to cart':
        1. the GroceryBot Thinks & Plan if it needs to use a tool and what tool to serve the request.
        2. The Action step allows the model to interface with tool and obtain information from external sources such as knowledge bases or environments or just an API call.
        3. The output is Observed, and this loop for thinking, planning and action continues until GroceryBot has all the information needed to fulfill user request.
        4. The GroceryBot also maintains a short-term conversation memory with LangChain during the chat so that the user don't have to repeat themselves.
        5. The products are added to cart and final confirmation is then returned to the user.

        '''
    )

def main():
    with st.expander("Architecture"):
        load_arch()
    load_demo()
    

@st.cache_resource
def configure_logging():
    print("init logger")
    logger = logging.getLogger('retail_genai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    st.session_state.logger = logger
    return logger

if __name__ == "__main__":
        
    st.title("🥕Grocery-Bot Assistant")
    
    #modelId = 'amazon.titan-tg1-large'
    modelId = 'anthropic.claude-instant-v1'

    keywords = [f'Model Id: {modelId}','Amazon Bedrock','Langchain', 'ReAct', 'Vector Store: FAISS']
    formatted_labels = [keyword_label(keyword) for keyword in keywords]
    st.write(' '.join(formatted_labels), unsafe_allow_html=True)
    apply_studio_style()

    # Add a description for this specific use case
    st.markdown(
        '''
        #### Use case:
        ###### Welcome to the **Grocery Assistant**, your guide to planning and preparing a delicious dinner with ease. Imagine you are a valued customer of Cymbal Grocery, your favorite grocery store. You have a craving for a special dish, like lasagne, but you're not sure where to start or what ingredients you need. That's where our new conversational bot, GroceryBot, comes in!

        **GroceryBot** is here to assist you at every step of your dinner journey:

        1. **Suggesting a Recipe**: Simply tell GroceryBot the dish you'd like to cook, and it will recommend a delicious recipe for you to try. Try 'salad' or 'lasagne'

        2. **Getting Ingredients and Cooking Instructions**: Once you've chosen a recipe, GroceryBot will provide you with a list of ingredients and clear cooking instructions.

        3. **Suggesting Products**: GroceryBot will suggest products that you might want to buy for the chosen recipe, ensuring you have everything you need to cook your meal. Ask 'Help me find products to buy for the recipe'

        4. **Buying Products**: GroceryBot can also help you order products. Ask 'Add the products to my cart'

        5. **Finding New Products for Dinner**: In addition to your chosen recipe, GroceryBot can help you discover new and exciting products that would complement your dinner experience. Ask 'Do you have chocolate cake?'


        ''')  
    if "logger" not in st.session_state:
        st.session_state.logger = configure_logging()
    main()