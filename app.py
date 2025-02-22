import streamlit as st
import os
import dotenv
import uuid
from time import time

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

from rag_methods import (
    load_doc_to_db, 
    load_url_to_db,
    stream_llm_response,
    stream_llm_rag_response,
)


dotenv.load_dotenv()
os.environ["USER_AGENT"] = "myagent"

MODELS = ["openai/gpt-4o",
          "openai/gpt-4o-mini",]

st.set_page_config(
    page_title = "RAG coches",
    page_icon = "🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# HEADER

st.html("""<h2 style="text-align: center;">📚🔍 <i> ¿Te gusta conducir? </i> 🤖💬</h2>""")

# --- Initial Setup ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "rag_sources" not in st.session_state:
    st.session_state.rag_sources = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
]

# --- Side Bar LLM API Tokens ---
with st.sidebar:
    if "AZ_OPENAI_API_KEY" not in os.environ:
        default_openai_api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        with st.popover("🔐 OpenAI"):
            openai_api_key = st.text_input(
                "Introduce your OpenAI API Key (https://platform.openai.com/)", 
                value=default_openai_api_key, 
                type="password",
                key="openai_api_key",
            )

    else:
        openai_api_key = None
        st.session_state.openai_api_key = None
        az_openai_api_key = os.getenv("AZ_OPENAI_API_KEY")
        st.session_state.az_openai_api_key = az_openai_api_key

# --- Main Content ---
# Checking if the user has introduced the OpenAI API Key, if not, a warning is displayed
missing_openai = openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key

if missing_openai and ("AZ_OPENAI_API_KEY" not in os.environ):
    st.write("#")
    st.warning("⬅️ Please introduce an API Key to continue...")

else:
    # Sidebar

    with st.sidebar:
        st.divider()
        st.selectbox(
        "🤖 Select a Model", 
        [model for model in MODELS if ("openai" in model and not missing_openai)],
        key="model"
        )
    
        cols0 = st.columns(2)

        with cols0[0]:
            is_vector_db_loaded = ("vector_db" in st.session_state and st.session_state.vector_db is not None)
            st.toggle(
                "Use RAG", 
                value=is_vector_db_loaded, 
                key="use_rag", 
                disabled=not is_vector_db_loaded,
            )
            

        with cols0[1]:
            st.button("Clear Chat", on_click = lambda: st.session_state.messages.clear(), type = "primary")
        
        st.header ("RAG sources:")

        #File upload input 
        st.file_uploader(
            "Upload a document",
            type = ["pdf","txt","docx","md"],
            accept_multiple_files=True,
            on_change=load_doc_to_db,
            key = "rag_docs",
        )

        #URL input
        st.text_input(
            "Upload an URL",
            placeholder="https://example.com",
            on_change=load_url_to_db,
            key = "rag_url"
        )

        with st.expander(f"Documents in DB ({0 if not is_vector_db_loaded else len(st.session_state.vector_db.get()['metadatas'])})"):
            st.write([] if not is_vector_db_loaded else [meta["source"] for meta in st.session_state.vector_db.get()['metadatas']])


    #Main chat app
    model_provider = st.session_state.model.split("/")[0]

    if model_provider == "openai":
        llm_stream = ChatOpenAI(
            model_name = st.session_state.model.split("/")[-1],
            temperature = 0.1,
            streaming = True
        )
    else: 
        print("Modelo no detectado")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Your message"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            fullresponse = ""

            messages = [HumanMessage(content = m["content"]) if m["role"] == "user" else AIMessage(content = m["content"]) for m in st.session_state.messages]


            if not st.session_state.use_rag:
                st.write_stream(stream_llm_response(llm_stream,messages))
            else:
                st.write_stream(stream_llm_rag_response(llm_stream,messages))