from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain

#Chat messages history
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory, SQLChatMessageHistory
import streamlit as st

# load model ollama in local machine
llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.2:latest",
    temperature=0.5,
    max_tokens=500
)


session_id = "Bayuzen"
st.title("How can I help you today?")
st.write("Enter you query below")
session_id = st.text_input("Enter you name",session_id)


#create session id for chat history
def get_session_history(session_id:str) -> BaseChatMessageHistory:
    return SQLChatMessageHistory(session_id=session_id, connection="sqlite:///chathistory.db")

#create prompt template
template = ChatPromptTemplate.from_messages(
    [
        ("human","{prompt}"),
        ('placeholder',"{history}")
    ]
)

#create chain invoke
chain = template | llm | StrOutputParser()

store = {}
history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="prompt", history_messages_key='history')


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

prompt = st.chat_input("Enter your query")



if prompt:
    response = history.invoke({"prompt":prompt},config={"configurable":{"session_id":session_id}})
    
    st.session_state.chat_history.append({"role":"user",
                                          "content":prompt})
    
    
    with st.chat_message('user'):
        st.markdown(prompt)
    
    st.session_state.chat_history.append({"role":"assistant",
                                          "content":response})
    
    with st.chat_message('assistant'):
        st.markdown(response)
    