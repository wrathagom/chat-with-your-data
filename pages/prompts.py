import streamlit as st
import json

if "prompts" not in st.session_state:
    with open("prompts.json", 'r') as f:
        st.session_state.prompts = json.load(f)

defaultNewPromptName = "New Prompt Name"
defaultNewPromptBody = "Prompt Body"

st.session_state.newPromptName = defaultNewPromptName
st.session_state.newPromptBody = defaultNewPromptBody

st.title('Prompts')

st.write('Only these three prompts would actually get user: default, query, and interpret. Might add in more dynamic tool selection in the future.')

st.divider()

def addNewPrompt():
    name = st.session_state.newPromptName
    body = st.session_state.newPromptBody
    st.session_state.prompts[name] = body

    st.session_state.newPromptName = defaultNewPromptName
    st.session_state.newPromptBody = defaultNewPromptBody

    # Writing to sample.json
    with open("prompts.json", "w") as outfile:
        outfile.write(json.dumps(st.session_state.prompts, indent=2))

def editPrompt(name, value):
    print('Editing', name, value)
    st.session_state.newPromptName = name
    st.session_state.newPromptBody = value

for prompt in st.session_state.prompts.keys():
    col1, col2, col3 = st.columns([5,1,1])

    with col1:
        st.subheader(prompt)
    with col2:
        st.button(
            'Edit',
            use_container_width=True,
            key='edit-{}'.format(prompt),
            kwargs={"name": prompt, "value": st.session_state.prompts[prompt]},
            on_click=editPrompt
        )
    with col3:
        st.button('Delete', use_container_width=True, key='delete-{}'.format(prompt), type='primary')

    st.code(st.session_state.prompts[prompt])

with st.form("newPromptForm", clear_on_submit=True):
    st.write("Create a New prompt")
    newName = st.text_input('Name', value=st.session_state.newPromptName, key='newPromptName')
    newBody = st.text_area('Body', value=st.session_state.newPromptBody, key='newPromptBody', help='Two parameters are available `{query}` which is the users text and `{datasets}` which is a markdown formatted list of available datasets.')

   # Every form must have a submit button.
    submitted = st.form_submit_button("Submit", on_click=addNewPrompt, use_container_width=True)
