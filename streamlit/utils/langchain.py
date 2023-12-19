from langchain.llms.bedrock import Bedrock
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains.llm import LLMChain, PromptTemplate
from langchain.chains.mapreduce import MapReduceChain
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain, StuffDocumentsChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from utils import bedrock
import logging



# load_summarize_chain provides three ways of summarization: stuff, map_reduce, and refine.
# stuff puts all the chunks into one prompt. Thus, this would hit the maximum limit of tokens.
# map_reduce summarizes each chunk, combines the summary, and summarizes the combined summary. If the combined summary is too large, it would raise error.
# refine summarizes the first chunk, and then summarizes the second chunk with the first summary. The same process repeats until all chunks are summarized.

def summarize_long_text(long_text,bedrock_client, modelId = 'amazon.titan-tg1-large', generationConfig = None, system_prompt = None, combine_prompt= None):
    if long_text is None or long_text == '':
        return
    output = ''
    if generationConfig is None:
        generationConfig = {
            "maxTokenCount":4096,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
    
    llm = Bedrock(
        model_id= modelId,
        model_kwargs= generationConfig,
        client= bedrock_client,
    )

    documents_to_embed = split_long_text(long_text)
    num_docs = len(documents_to_embed)

    num_tokens_first_doc = llm.get_num_tokens(documents_to_embed[0].page_content)

    print(
        f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
    )

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
    human_message_prompt = HumanMessagePromptTemplate.from_template(combine_prompt)
    prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt],
    )

    summary_chain = load_summarize_chain(llm=llm, chain_type="map_reduce", verbose=False, combine_prompt=prompt)
    output = summary_chain.run(documents_to_embed)
    return output.strip() 


def split_long_text(long_text):
    if long_text is None:
        return
    
    text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n"], chunk_size=4000, chunk_overlap=100
    )

    docs = text_splitter.create_documents([long_text])
    return docs

def generate_text_qa(prompt_data= None, modelId = 'amazon.titan-tg1-large', generationConfig = None):
    if prompt_data is None:
        return
    
    if generationConfig is None:
        generationConfig = {
            "maxTokenCount":4096,
            "stopSequences":[],
            "temperature":0,
            "topP":0.9
            }
        
    bedrock_a= bedrock.BedrockAssistant(modelId)
    llm = Bedrock(
        model_id= modelId,
        model_kwargs= generationConfig,
        client= bedrock_a.get_bedrock_client(),
    )
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    output = llm_chain.run(prompt_data)
    #qa_chain = load_qa_chain(llm=llm, chain_type="stuff", verbose=True)
    #output = qa_chain.run(question= prompt)
    return output.strip() 









