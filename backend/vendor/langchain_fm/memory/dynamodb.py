from langchain.memory import DynamoDBChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory
from attrs import define, field, Factory

@define(kw_only=True)
class DynamoDBMemory:
    table_name: str

    def get_memory(self, session_id, k=3):
        chat_history = DynamoDBChatMessageHistory(
            table_name= self.table_name, session_id=session_id)

        memory = ConversationBufferMemory(
            k= k,
            memory_key="chat_history",
            return_messages=True
        )
        memory.chat_memory = chat_history
        return memory