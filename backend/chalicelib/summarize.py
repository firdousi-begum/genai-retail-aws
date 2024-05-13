from langchain.llms.bedrock import Bedrock
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_fm import ClaudeV2

class SummarizeAssistant():
    def __init__(
        self, 
        client, 
        logger= None
    ):
        self.client = client 
        self.logger = logger  
        self.llm = ClaudeV2(client=self.client, token_count=2000, temperature=0.2).get_llm()

    def summarize_long_text(self, long_text, system_prompt = None, combine_prompt= None):
        if long_text is None or long_text == '':
            return
        output = ''

        split_docs = self.split_long_text(long_text)
        num_docs = len(split_docs)

        num_tokens_first_doc = self.llm.get_num_tokens(split_docs[0].page_content)

        print(
            f"Now we have {num_docs} documents and the first one has {num_tokens_first_doc} tokens"
        )

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
        human_message_prompt = HumanMessagePromptTemplate.from_template(combine_prompt)
        prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt],
        )

        summary_chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce", verbose=False, combine_prompt=prompt)
        output = summary_chain.run(split_docs)
        return output.strip() 


    def split_long_text(self, long_text):
        if long_text is None:
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=4000, chunk_overlap=100
        )

        docs = text_splitter.create_documents([long_text])
        return docs
