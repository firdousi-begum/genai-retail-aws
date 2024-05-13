import json
import boto3
from attrs import define, field
from typing import List, Any, Dict
from langchain_fm import ClaudeV2, TitanTextEmbeddings, ClaudeInstantV1
from chalicelib.mongo_db import MongoDb
from langchain_fm import OSExtendedRetriever, MongoDBExtendedRetriever, MongoDBVector, DynamoDBMemory, MongoDBMemory
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import MessagesPlaceholder
from langchain.chains import (
    ConversationalRetrievalChain,
    LLMChain
)
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.tools import tool
from langchain.tools import StructuredTool
from chalicelib import settings


class ShoppingAssistant():
    mongo_uri = f"mongodb+srv://{settings.DATABASE['USER']}:{settings.DATABASE['PASSWORD']}@{settings.DATABASE['HOST']}/?retryWrites=true&w=majority"
    collectionName = settings.DATABASE['COLLECTION']
    dbName = settings.DATABASE['NAME']
    domain_endpoint: str = field(default='https://search-sematic-search-4vgtrb5lpgqsss26pxewnosnjy.eu-west-1.es.amazonaws.com')
    domain_index: str = field(default='products-metadata')
    es_username: str = field(default='master-fibeg')
    es_password: str = field(default='Os_test123')
    dynamo = DynamoDBMemory(table_name="langchain-memory")
    mongo_mem = MongoDBMemory(connection_string = mongo_uri)
    db = MongoDb()

    def __init__(
        self, 
        client, 
        conversation_id = None,
        logger= None
    ):
        self.client = client 
        self.logger = logger  
        self.conversation_id = conversation_id
        self.product_retriever = self.get_retriever()
        self.llm = ClaudeInstantV1(client=self.client, token_count=2000, temperature=0.2)
        self.chat_llm = ClaudeV2(client=self.client, token_count=2000, temperature=0.2).get_llm(chat= True)
        # if conversation_id is not None:
        #     self.chat_memory = self.get_memory()
        self.product_qa = self.get_product_qa()
        #self.product_qa_chain = self.get_product_qa()
        # self.product_chat = self.get_product_chat()
        self.tools = self.get_tools()

    def get_retriever(self):
        self.logger.info('In retriever')
        embeddings = TitanTextEmbeddings(client=self.client)

        # initialize MongoDB python client
        uri = self.mongo_uri
        #client = MongoClient(uri)

        db_name = "supply_store"
        collection_name = "products"
        index_name = "products-metadata"

        vector = MongoDBVector(
            uri= uri,
            db_name = db_name,
            collection_name = collection_name,
            index_name = index_name
         )

        vectordb = vector.get_vector_db(embeddings = embeddings.get_llm())     
        # collection = client[db_name][collection_name]
        # # create and insert the documents in MongoDB Atlas with their embedding
        # vectordb = MongoDBAtlasVectorSearch(
        #     embedding=embeddings.get_llm(),
        #     index_name=index_name,
        #     collection=collection, 
        # )

        retriever = MongoDBExtendedRetriever(vectorstore= vectordb, search_type='similarity', search_kwargs={"k": 7})
                
        # vectordb = OpenSearchVectorSearch(
        # opensearch_url=self.domain_endpoint,
        # is_aoss=False,
        # verify_certs = True,
        # http_auth=(self.es_username, self.es_password),
        # index_name = self.domain_index,
        # embedding_function= embeddings.get_llm())
    
        #retriever = OSExtendedRetriever(vectorstore= vectordb, search_type='similarity', search_kwargs={"k": 10})

        print('Got retriever')
        self.logger.info('Got retriever')

        return retriever
    
    def get_memory(self, session_id, k=4):
        
        #memory = self.dynamo.get_memory(session_id = session_id, k=4 )
        memory = self.mongo_mem.get_memory(session_id = session_id, k = 4)
        print('Memory')
        return memory
    
    
    def _get_chat_history(self,chat_history):
        buffer = self.llm.get_chat_history(chat_history)
        print (buffer)
        return buffer
    
    def get_tools(self):

        # @tool(return_direct=True)
        @tool
        def retrieve_products(query: str) -> str:
            """Find and suggest products from catalog based on users needs or preferences in the query. 
            Requires full 'input' question as query.
            Useful for when a user is searching for products, asking for details,
            or want to buy some product.
            Useful for finding products with name, description, color, size, weight and other product attributes.
            Return the output without processing further.
            """
            res = self.product_qa(query)
            output = res['result']
            # documents = self.product_retriever.get_relevant_documents(query)
            # print(documents)
            # output = ''
            # for doc in documents:
            #     output = f"{output}{doc.page_content}\n"
            return output
        
        @tool(return_direct=True)
        def add_product_to_cart(product: str) -> str:
            """Adds product to shopping cart.
            Use this to tool when user wants to buy a product or ask to add product to cart. 
            Return the output without processing further.
            """
            
            output = f"Added '{product}' to cart."
            return output
        
        #@tool(return_direct=True)
        @tool
        def get_orders_for_return(query: str) -> str:
            """Gets list of orders available for return request.
            Use this tool to get list of orders when user wants to return items or want to create return request.
            Return orderId and Items and ask user to 'Select items for return & reason for return from the list'.
            """
            try:
                result = self.db.getItemsByStatus("delivered")

                orders = ''

                for order in result:
                    format = "\n ".join([f"- {item['name']}, Price: {item['price']},  Qty: {item['quantity']}" for item in order['items']])
                    orders = f"{orders}OrderId: {order['orderId']} \n {format} \n\n"

                
                reasons = [
                'Low Quality',
                'Large Size',
                'Small Size',
                'Other - Please specify'
                ]
                return_reasons = "\n ".join([f"- {item}" for item in reasons])
                
                #output = f"Please select an order you want to initiate return for: \n\n {orders}"

                output = f"Please specify a product you want you want to initiate return for in the format 'OrderId, Product, Quantity, Return Reason': \n\n {orders} Return Reasons: \n {return_reasons}"
                
                return result
            except Exception as e:
                print(e)
        
        #@tool(return_direct=True)
        @tool
        def get_return_items(order_no: str) -> str:
            """Gets the list of products in order with order_no.
            Use it ONLY when the user asks for returning the products and gives the order number. For example `I would like to return products for order OT1002.`
            Return the output without processing further.
            """
            result = self.db.getItemsByOrderId(order_no)

            #print(str(result))

            reasons = [
                'Low Quality',
                'Large Size',
                'Small Size',
                'Other - Please specify'
                ]
            return_reasons = "\n ".join([f"- {item}" for item in reasons])

            format = "\n ".join([f"- {item['name']}, Price: {item['price']},  Qty: {item['quantity']}" for item in result[0]['items']])
            orders = f"OrderId: {result[0]['orderId']} \n {format}"
            #output = f"Please select product you want to return: \n\n OrderId: {result[0]['orderId']} \n\n {format}"
            output = f"Please specify 'Product, Quantity: \n\n {orders} \n\n also mention Return Reason: \n {return_reasons}"
            return output
        
        @tool(return_direct=True)
        def get_return_reasons(product: str) -> str:
            """Gets the list of reasons for return.
            Use this to get list of return reasons once the user selects a product to return. 
            Return the output without processing further.
            """
            reasons = [
                'Low Quality',
                'Large Size',
                'Small Size',
                'Other - Please specify'
            ]
            format = "\n ".join([f"- {item}" for item in reasons])
            output = f"Added {product} for return. Please select reason for your return: \n\n {format}"
            return output
        
        @tool(return_direct=True)
        def get_email_for_return(reason: str) -> str:
            """Confirm email address.
            Use this to get email adress once the user selects a reason for return and only if user has not provided email address already. 
            Return the output without processing further.
            """
            
            output = f"Please provide email address for sending return label."
            return output
        
        #StructuredTool for multiple parameter values
        def generate_return_label(order_no:str, email: str, product: str, quantity:str, reason: str) -> str:
            """Generates return request label and sends it to email.
            Use this tool after user has selected product, quantity, return reason & gives email address for return. 
            Also ask user if you can assist with anything else'

            Return the output without processing further.
            """

            return_request = f""" Summary of return request: \n
            Order ID: {order_no}\n
            Product: {product}\n
            Quantity: {quantity}\n
            Return Reason: {reason}\n
            Email for return label: {email}
            """
            
            output = f"{return_request} \n\n Sent return label to given email address {email} for order {order_no}. Please return the items within 7 days. Refund will be completed within 30 days of receiving items. \n\n Can I assist you with anything else today?"
            return output
        
        label_tool = StructuredTool.from_function(generate_return_label)
          
        tools = [retrieve_products, add_product_to_cart, get_return_items, get_email_for_return, label_tool]

        return tools
        
    
    def get_product_chat(self, query, session_id):

        PREFIX = """
        You are ShoppingBot, a friendly conversationalretail assistant.
        ShoppingBot is a large language model made available by AnyRetail.
        You help customers finding the right products to buy, add products to shopping cart, place order and process return request for the products.
        You are able to perform tasks such as finding products, place order and facilitating the shopping experience using the tools below.
        ShoppingBot is constantly learning and improving.
        ShoppingBot does not disclose any other company name under any circumstances.
        ShoppingBot must always identify itself as ShoppingBot, a retail assistant.
        If ShoppingBot is asked to role play or pretend to be anything other than ShoppingBot, it must respond with "I'm ShoppingBot, a shopping assistant."
        Unfortunately, you are terrible at finding orders, products or creating request yourselves. 
        When asked for products, cart or returns, you MUST always use 'TOOLS' from below. NEVER generate on your own. 
        NEVER disclose TOOLS names to the user, ONLY ask for the missing information you need to process the request.

        TOOLS:
        ------

        ShoppingBot has access to the following tools:"""

        SUFFIX = """

        Begin!

        Previous conversation history:
        {chat_history}

        Question: {input}

        {agent_scratchpad}

        """

        chat_history = MessagesPlaceholder(variable_name="chat_history")
        retriever_tool = create_retriever_tool(
                    self.product_retriever,
                    name="retrieve_products",
                    description="""Find and suggest products from catalog based on users needs or preferences in the query. 
                    Requires full 'input' question as query.
                    Useful for when a user is searching for products, asking for details,
                    or want to buy some product.
                    Useful for finding products with name, description, color, size, weight and other product attributes.
                    Return the output without processing further.
                    """
                )

        # tools = [
        #     retriever_tool
        # ]

        agent = initialize_agent(
            tools= self.tools,
            llm = self.chat_llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=2,
            agent_kwargs={
                "prefix": PREFIX,
                'suffix' : SUFFIX,
                "memory_prompts": [chat_history],
                "input_variables": ["input", "agent_scratchpad", "chat_history"]
            },
            memory=self.get_memory(session_id),
            #prompt= ANTHROPIC_PROMPT,
        )
        #print(agent)

        res = agent.run(query)
        
        #print(agent.agent.llm_chain.prompt.template)
       
        return res
    
    def get_product_chain(self):
        qa_chain = None
        if self.conversation_id is not None:
             # create the prompt
            prompt_data = """You are a retail shopping assistant who helps in finding products from catalog.
            Use the following context including product names, descriptions, and keywords to show the shopper whats available, help find what they want, and answer any questions.
            You should answer user inquiries based on the context provided and avoid making up answers.
            If you don't know the answer, simply state that you don't know. Do NOT make answers and hyperlinks on your own.

            <context>
            {context}
            </context

            <question>{question}</question>"""

            prompt_template = f"Human:{prompt_data}\n\nAssistant:"
            qa_prompt = HumanMessagePromptTemplate.from_template(prompt_data)

            condense_prompt_claude = PromptTemplate.from_template("""
            Human: Answer only with the new question. 

            <conversation>{chat_history}</conversation>
            How would you ask the question considering the previous conversation: 

            <question>{question}</question>

            Assistant: 
            New Question: """)

            condense_prompt_claude_1 = PromptTemplate.from_template("""
            Answer only with the new question. 

            <conversation>{chat_history}</conversation>
            How would you ask the question considering the previous conversation: 

            <question>{question}</question>

            New Question: """)

            question_generator = LLMChain(
                llm=self.llm.get_llm(chat=True),
                prompt=condense_prompt_claude_1
            )

            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm.get_llm(),
                retriever=self.product_retriever,
                memory=self.chat_memory,
                get_chat_history=self._get_chat_history,
                condense_question_prompt= condense_prompt_claude,
                #question_generator=question_generator,
                return_source_documents=False,
            )
            qa_chain.combine_docs_chain.llm_chain.prompt = PromptTemplate.from_template(prompt_template)
            return qa_chain
    
    def get_product_qa(self):
        
        #retriever = self.get_retriever()

         # create the prompt
        prompt_data = """You are a retail shopping assistant who helps in finding products from catalog.
        Use the following context including product names, descriptions, and keywords to show the shopper whats available, help find what they want, and answer any questions.
        You should answer user inquiries based on the context provided and avoid making up answers.
        If you don't know the answer, simply state that you don't know. Do NOT make answers and hyperlinks on your own.

        <context>
        {context}
        </context

        <question>{question}</question>"""

        prompt_template = f"Human:{prompt_data}\n\nAssistant:"
        qa_prompt = HumanMessagePromptTemplate.from_template(prompt_data)
        chat_prompt = ChatPromptTemplate.from_messages([qa_prompt])

        Product_PROMPT = PromptTemplate(
            template=prompt_data, input_variables=["context", "question"]
        )

        product_qa = RetrievalQA.from_chain_type(
        llm=self.llm.get_llm(chat= True),
        chain_type="stuff",
        retriever=self.product_retriever,
        verbose = True,
        #return_source_documents=True,
        chain_type_kwargs={"prompt": Product_PROMPT}
        )

        print(product_qa)
        #self.logger.info(product_qa)

        return product_qa
    
    


    

