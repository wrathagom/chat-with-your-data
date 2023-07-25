import openai
import streamlit as st
import json
from elasticsearch import Elasticsearch

cloud_id = st.secrets["ELASTIC_CLOUD_ID"]
api_key = st.secrets["ELASTIC_API_KEY"]

es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)

st.title("Elastic Data Agent")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
    st.session_state["temperature"] = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "prompts" not in st.session_state:
    with open("prompts.json", 'r') as f:
        st.session_state.prompts = json.load(f)

if "datasets" not in st.session_state:
    with open("datasets.json", 'r') as f:
        st.session_state.datasets = json.load(f)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if "fullPrompt" in message:
            with st.expander("Full Prompt"):
                st.markdown(message["fullPrompt"])
        
        if "explanation" in message:
            with st.expander("Explanation"):
                st.write(message["explanation"])

if prompt := st.chat_input("What is up?"):
    promptedContent = st.session_state.prompts['default'].format(query=prompt)

    with st.chat_message("user"):
        st.markdown(prompt)
        with st.expander("Full prompt"):
            st.markdown(promptedContent)

    st.session_state.messages.append({"role": "user", "content": promptedContent})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        full_response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=False,
            temperature=st.session_state["temperature"]
        )

        # Remove the prompt formatted user query
        st.session_state.messages.pop()
        st.session_state.messages.append({"role": "user", "content": prompt, "fullPrompt": promptedContent})

        parsedResponse = {line.split(' | ')[0]:line.split(' | ')[1] for line in full_response['choices'][0]['message']['content'].split('\n\n')}

        response = parsedResponse['RESPONSE']
        st.session_state.messages.append({"role": "assistant", "content": response, "explanation": parsedResponse})
        message_placeholder.write(response)

        expander = st.expander("See explanation")
        expander.write(parsedResponse)

    if parsedResponse['TOOL'] == 'query':
        dataset = st.session_state.datasets[parsedResponse['DATASET']]
        alias = dataset['alias']
        template = st.session_state.prompts['query']
        promptedContent = template.format(query=prompt, mappings=json.dumps(dataset['mappings']), sampleData=json.dumps(dataset['sampleData']))

        # with st.chat_message("assistant"):
        #     st.markdown(prompt)
        #     with st.expander("Full prompt"):
        #         st.markdown(promptedContent)

        st.session_state.messages.append({"role": "assistant", "content": promptedContent})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            full_response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=False,
                temperature=st.session_state["temperature"]
            )

            # Remove the prompt formatted assistant query
            st.session_state.messages.pop()
            # st.session_state.messages.append({"role": "assistant", "content": prompt, "fullPrompt": promptedContent})

            parsedResponse = {line.split(' | ')[0]:line.split(' | ')[1] for line in full_response['choices'][0]['message']['content'].split('\n\n')}

            response = parsedResponse['RESPONSE']
            rawQuery = parsedResponse['BODY']
            st.session_state.messages.append({"role": "assistant", "content": response, "fullPrompt": promptedContent, "explanation": parsedResponse})
            message_placeholder.write(response)

            with st.expander("Full Prompt"):
                st.write(promptedContent)

            with st.expander("See explanation"):
                st.write(parsedResponse)

        query = json.loads(rawQuery)
        if 'size' in query:
            if query['size'] > 3:
                query['size'] = 3
        else:
            query['size'] = 3

        print(query)
        esResponse = es.search(index=alias, body=query)

        print(json.dumps(esResponse['hits']))
        template = st.session_state.prompts['interpret']
        promptedContent = template.format(query=prompt, results=json.dumps(esResponse['hits']))
        st.session_state.messages.append({"role": "assistant", "content": promptedContent})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            full_response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=False,
                temperature=st.session_state["temperature"]
            )

            # print(full_response)

            # Remove the prompt formatted assistant query
            st.session_state.messages.pop()
            # st.session_state.messages.append({"role": "assistant", "content": prompt, "fullPrompt": promptedContent})

            response = full_response['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": response, "fullPrompt": promptedContent, "queryResults": esResponse})
            message_placeholder.write(response)

            with st.expander("Full Prompt"):
                st.write(promptedContent)

            with st.expander("Query Results"):
                st.write(esResponse)