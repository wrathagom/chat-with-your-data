import streamlit as st
import json

def load_file_as_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def initialize_session_state():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"
        st.session_state['temperature'] = 0.0
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "prompts" not in st.session_state:
        st.session_state.prompts = load_file_as_json("prompts.json")
    if "datasets" not in st.session_state:
        st.session_state.datasets = load_file_as_json("datasets.json")