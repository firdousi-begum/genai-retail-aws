from langchain.memory import MongoDBChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory
from attrs import define, field, Factory
from langchain.schema.messages import HumanMessage, AIMessage

@define(kw_only=True)
class MongoDBMemory:
    connection_string: str

    def get_messages(self, session_id):
        chat_history = MongoDBChatMessageHistory(
            connection_string=self.connection_string, session_id=session_id)
        
        # Initialize an empty list to store the JSON representations
        json_messages = []
        # Iterate through the list of messages and create dictionaries
        for message in chat_history.messages:
            if isinstance(message, HumanMessage):
                json_message = {"type": "human", "content": message.content}
            elif isinstance(message, AIMessage):
                json_message = {"type": "ai", "content": message.content}
            json_messages.append(json_message)

        return json_messages
    
    def get_memory(self, session_id, k=3):
        chat_history = MongoDBChatMessageHistory(
            connection_string=self.connection_string, session_id=session_id)

        memory = ConversationBufferMemory(
            k= k,
            memory_key="chat_history",
            return_messages=True
        )
        memory.chat_memory = chat_history
        return memory