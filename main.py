import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
PASSWORD = os.getenv("PASSWORD")

# Initialize session state for authentication and conversation
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Add system prompt once at the start of the conversation
SYSTEM_PROMPT = (
    "If you are asked to provide code or LaTeX, embed it in markdown text "
    "such that it is not compiled by the interface."
)

if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

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

client = OpenAI()

# Sidebar: Model selection using radio buttons
st.sidebar.title("Settings")
selected_model = st.sidebar.radio(
    "Select Model",
    options=[
        "o3-mini",
        "o1-mini",
        "gpt-4o",
        "gpt-4o-mini-search-preview",
        "gpt-4o-search-preview",
    ],
)

# Main chat interface
st.title("Chat with ChatGPT")
st.write("This conversation resets on page reload.")

# Display the conversation history using st.chat_message
for message in st.session_state.conversation:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# Accept user input via chat input widget
user_input = st.chat_input("Enter your message")
if user_input:
    # Append the user message to the conversation history
    st.session_state.conversation.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the OpenAI Chat API (non-streamed) with the conversation history
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=st.session_state.conversation,
        )
        assistant_reply = response.choices[0].message.content
        st.session_state.conversation.append(
            {"role": "assistant", "content": assistant_reply}
        )
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        st.rerun()  # Rerun to update the display
    except Exception as e:
        st.error(f"Error: {e}")
