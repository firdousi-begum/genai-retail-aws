from langchain.schema.retriever import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.vectorstores.base import VectorStore
from typing import Any, List
from pydantic import BaseModel, Field
from attrs import define

import logging

logger=logging.getLogger(__name__)

class OSExtendedRetriever(BaseRetriever):
    vectorstore: VectorStore
    """VectorStore to use for retrieval."""
    search_type: str = "similarity"
    """Type of search to perform. Defaults to "similarity"."""
    search_kwargs: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:

        documents_with_scores = self.vectorstore.similarity_search_with_score(query=query, **self.search_kwargs)
        updated_docs = self.update_metadata_with_score(documents_with_scores)
        #logger.info(f'updated_docs: {len(updated_docs)}, newdocs: {len(newdocs)}')
        #updated_docs.extend(newdocs)
        return updated_docs 

    def update_metadata_with_score(self,documents_with_scores):
        #newdocs = []
        for doc, score in documents_with_scores:
            doc.metadata = { **doc.metadata, **{"score": score}}
            source = doc.metadata.get('source','').strip()
            title = doc.metadata.get('title','').strip()
            doc.page_content = f''' Document link <source>[{title}]({source}), Score: {score}</source>. \n\n {doc.page_content} '''
            #logger.info(f'doc: {doc}')
            # newdocs.append( Document 
            #     (   
            #         metadata= doc.metadata,
            #         page_content= f'Source: {source}. Score: {score}. Title: {title}.'
            #     ))
        return [doc for (doc, _) in documents_with_scores]
    
    def create_sources_text_with_score(self,source_documents):
        # Remove duplicate entries based on metadata['source']
        unique_sources = {}
        sources_markdown = "##### Sources:\n\n"

        for idx, doc in enumerate(source_documents):
            source = doc.metadata.get('source','').strip()
            score = doc.metadata.get('score',0.0)
            title = doc.metadata.get('title','').strip()
            page_num = doc.metadata.get('page', 0)
            print(page_num)
            if title == '':
                title = source
            #logger.info(f'source: {source}, score: {score},title: {title} ')
            if source and (source not in unique_sources or score > unique_sources[source][1]):
                unique_sources[source] = (title, score, page_num)
        
        sorted_sources = sorted(unique_sources.items(), key=lambda x: x[1][1], reverse=True)

        # Create the text with the desired format
        for source, (title, score, page_num) in sorted_sources:
            sources_markdown += "- " + "\n- ".join([f"[{title}]({source}), Score: {score}"]) + "\n"
            if page_num != 0:
                sources_markdown += f", Page: {page_num}\n"
            else:
                sources_markdown += "\n"

        return sources_markdown

