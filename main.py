import os

import streamlit as st
from dotenv import load_dotenv

from utils import NAME_MAPPING, Model

# Load environment variables from .env
load_dotenv()
PASSWORD = os.getenv("PASSWORD")

st.set_page_config(initial_sidebar_state="collapsed")

# Initialize session state for authentication and conversation
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication: Ask for password if not yet authenticated
if not st.session_state.authenticated:
    st.title("Login")
    password_input = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    st.stop()

# Sidebar: Model selection using radio buttons
st.sidebar.title("Settings")
selected_model = st.sidebar.radio(
    "Select Model",
    options=[
        "o4-mini",
        "Gemini-2.5-Pro",
        "gpt-4o",
        "gpt-4o-mini-search-preview",
        "gpt-4o-search-preview",
    ],
)
st.session_state.selected_model = NAME_MAPPING[selected_model]

if "Gemini" in selected_model:
    if not st.session_state.get("model") or st.session_state.model_type == "openai":
        st.session_state.model_type = "google"
        st.session_state.model = Model(model_type="google")
else:
    if not st.session_state.get("model") or st.session_state.model_type == "google":
        st.session_state.model_type = "openai"
        st.session_state.model = Model(model_type="openai")

# Display the conversation history using st.chat_message
for message in st.session_state.model.history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# Accept user input via chat input widget
user_input = st.chat_input("Enter your message")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    assistant_answer = st.session_state.model.chat(user_input)
    with st.chat_message("assistant"):
        st.markdown(assistant_answer)

    st.rerun()
