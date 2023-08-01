import openai
import streamlit as st
import json
from elasticsearch import Elasticsearch

from shared import initialize_session_state

initialize_session_state()

cloud_id = st.secrets["ELASTIC_CLOUD_ID"]
api_key = st.secrets["ELASTIC_API_KEY"]

es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)

def build_prompt(prompt, data):
    return st.session_state.prompts[prompt].format(**data)

def build_response():
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    print(messages)

    full_response =  openai.ChatCompletion.create(
        model=st.session_state["openai_model"],
        messages=messages,
        stream=False,
        temperature=st.session_state["temperature"]
    )

    try:
        parsed_response = {line.split(' | ')[0]:line.split(' | ')[1] for line in full_response['choices'][0]['message']['content'].split('\n\n')}

        return parsed_response
    except IndexError:
        print(st.session_state['messages'][-1])
        print(full_response)
        # TODO: implement a retry

def displayMessage(role, content, extras=None):
    with st.chat_message(role):
        st.markdown(content)

        if extras != None:
            for extra in extras:
                with st.expander(extra['type']):
                    st.write(extra['body'])

# Actual Application UI
st.title("Elastic Data Agent")

openai.api_key = st.secrets["OPENAI_API_KEY"]

for message in st.session_state.messages:
    if 'extras' in message:
        displayMessage(message["role"], message["content"], message['extras'])
    else:
        displayMessage(message["role"], message["content"])

if prompt := st.chat_input("What is up?"):
    prompted_content = build_prompt('default', {
        'query': prompt
    })

    displayMessage('user', prompt)

    # Step 1: We add the new message with full prompt
    st.session_state.messages.append({"role": "user", "content": prompted_content})

    # Step 2: Send all the messages to OpenAI
    parsedResponse = build_response()

    # Step 3: Remove the prompt formatted user query and add just the agent response.
    st.session_state.messages.pop()
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Step 4: Add the Agent response to the messages
    response = parsedResponse['RESPONSE']
    extras = [{"type": "Full Prompt", "body": prompted_content}, {"type": "Full Response", "body": parsedResponse}]
    st.session_state.messages.append({"role": "assistant", "content": response, "extras": extras})

    # Display assistant response in chat message container
    displayMessage('assistant', response, extras)

    if parsedResponse['TOOL'] == 'query':
        dataset = st.session_state.datasets[parsedResponse['DATASET']]
        alias = dataset['alias']
        promptedContent = build_prompt('query', {
            "query": prompt,
            "alias": alias,
            "mappings": json.dumps(dataset['mappings']),
            "sampleData": json.dumps(dataset['sampleData'])
        })

        st.session_state.messages.append({"role": "user", "content": promptedContent})

        parsedResponse = build_response()

        response = parsedResponse['RESPONSE']
        rawQuery = parsedResponse['BODY']

        # location = parsedResponse['LOCATION']
        extras = [{"type": "Full Prompt", "body": promptedContent}, {"type": "Full Response", "body": parsedResponse}]

        st.session_state.messages.pop()
        st.session_state.messages.append({"role": "assistant", "content": response, "extras": extras})

        displayMessage('assistant', response, extras)

        query = rawQuery
        # if 'size' in query:
        #     if query['size'] > 3:
        #         query['size'] = 3
        # else:
        #     query['size'] = 3

        esResponse = es.sql.query(body={"query": query}, format='csv')

        print(esResponse)

        promptedContent = build_prompt('interpret', {
            "query": prompt,
            "results": esResponse
        })

        st.session_state.messages.append({"role": "user", "content": promptedContent})
        parsedResponse = build_response()
        try:
            response = parsedResponse['RESPONSE']
        except TypeError:
            response = "Sorry it looks like something went wrong trying to grab that data for you."
        extras = [{"type": "Full Prompt", "body": promptedContent}, {"type": "Full Response", "body": parsedResponse}, {"type": "Query Results", "body": esResponse}]
        # Remove the prompt formatted assistant query
        st.session_state.messages.pop()
        st.session_state.messages.append({"role": "assistant", "content": response, "extras": extras})

        displayMessage('assistant', response, extras)

