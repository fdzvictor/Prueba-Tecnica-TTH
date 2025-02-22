import streamlit as st
import os
import dotenv
from pathlib import Path
from time import time

#Loaders para diferentes formatos
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders import (
    WebBaseLoader, 
    PyPDFLoader, 
    Docx2txtLoader,
    TextLoader,
    JSONLoader,
)

#Embeddings, chnukizar y subir a bdd
from langchain_community.vectorstores import Chroma
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

dotenv.load_dotenv()
os.environ["USER_AGENT"] = "myagent"

DB_DOCS_LIMIT = 10

#Function to stream llm response:
def stream_llm_response(llm_stream,messages):
    response_message = ""

    for chunk in llm_stream.stream(messages):
        response_message += chunk.content
        yield chunk
    
    st.session_state.messages.append({"role":"assistant", "content":response_message})

def load_doc_to_db():
    #Use loader according to doc type:
    if "rag_docs" in st.session_state and st.session_state.rag_docs:
        docs = []
        for doc_file in st.session_state.rag_docs:
            if doc_file.name not in st.session_state.rag_sources:
                if len(st.session_state.rag_sources) < DB_DOCS_LIMIT:
                    os.makedirs("source_files",exist_ok = True)
                    file_path = f"source_files/{doc_file.name}"
                    with open(file_path,"wb") as file:
                        file.write(doc_file.read())
                    
                    try:
                        if doc_file.type == "application/pdf":
                            loader = PyPDFLoader(file_path)

                        elif  doc_file.name.endswith(".docx"):
                            loader = Docx2txtLoader(file_path)

                        elif doc_file.type in ["text/plain", "text/markdown"]:
                            loader = TextLoader(file_path)
                        
                        else:
                            st.warning(f"Document type {doc_file.type} not supported.")
                            continue

                        docs.extend(loader.load())
                        st.session_state.rag_sources.append(doc_file.name)

                    except Exception as e:
                        st.toast(f"error loading document {doc_file.type}: {str(e)}",icon="⚠️")
                        print(f"error loading {doc_file.type}: {str(e)}")

                    # finally: 
                    #     os.remove(file_path)

                else:
                    st.error(f"Max documents reached: ({DB_DOCS_LIMIT})")

        if docs:
            _split_and_load_docs(docs)
            st.toast(f"Document *{str([doc_file.name for doc_file in st.session_state.rag_docs])[1:-1]}* loaded succesfully",icon="✅")

def load_url_to_db():
    if "rag_url" in st.session_state and st.session_state.rag_url:
        url = st.session_state.rag_url
        docs = []
        if url not in st.session_state.rag_sources:
            if len(st.session_state.rag_sources) < 10:
                try:
                    loader = WebBaseLoader(url)
                    docs.extend(loader.load())
                    st.session_state.rag_sources.append(url)

                except Exception as e:
                    st.error(f"Error loading document from {url}: {e}")

                if docs:
                    _split_and_load_docs(docs)
                    st.toast(f"Document from URL *{url}* loaded successfully.", icon="✅")

            else:
                st.error("Maximum number of documents reached (10).")

def initialize_vector_db(docs):
    
    vector_db = Chroma.from_documents(
        documents=docs,
        embedding = OpenAIEmbeddings(),
        collection_name = f"{str(time()).replace('.','')[:14]}_" + st.session_state['session_id']
    )

    chroma_client = vector_db._client
    collection_names = sorted([collection.name for collection in chroma_client.list_collections()])
    print(f"number of collections: {len(collection_names)}")
    while len(collection_names) > 20:
        chroma_client.delete_collection(collection_names[0])
        collection_names.pop[0]
    
    return vector_db

def _split_and_load_docs(docs):

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,
    chunk_overlap=1000,
)

    document_chunks = text_splitter.split_documents(docs)

    if "vector_db" not in st.session_state:
        st.session_state.vector_db = initialize_vector_db(docs)
    else:
        st.session_state.vector_db.add_documents(document_chunks)

def _get_context_retriever_chain(vector_db,llm):

    retriever = vector_db.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name = "messages"),
    ("user","{input}"),
    ("user", "Given the above conversation, generate a search query to look up in order to get relevant information of the conversation, focusing on the most recent messages")
    ])
    retriever_chain = create_history_aware_retriever(llm,retriever,prompt)

    return retriever_chain

def get_conversational_rag_chain(llm):

    retriever_chain = _get_context_retriever_chain(st.session_state.vector_db, llm)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are a helpful assistant. You will have to answer to user's queries.
         You will have some context to help you with your answers, but not always will be completely related or helpful.
         You can also use your knowledge to assist anwering the user's queries.\n
         {context}"""),
         MessagesPlaceholder(variable_name = "messages"),
         ("user","{input}"),
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm,prompt)

    return create_retrieval_chain(retriever_chain,stuff_documents_chain)

def stream_llm_rag_response(llm_stream,messages):
    conversation_rag_chain = get_conversational_rag_chain(llm_stream)
    response_message = "*(RAG Response)\n"
    for chunk in conversation_rag_chain.pick("answer").stream({"messages" : messages[:-1], "input": messages[-1].content}):
        response_message += chunk
        yield chunk

    st.session_state.messages.append({"role":"assistant", "content": response_message})

