import streamlit as st
import json
from elasticsearch import Elasticsearch

cloud_id = st.secrets["ELASTIC_CLOUD_ID"]
api_key = st.secrets["ELASTIC_API_KEY"]

es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key
)

if "datasets" not in st.session_state:
    with open("datasets.json", 'r') as f:
        st.session_state.datasets = json.load(f)

defaultNewDatasetName = "New Dataset Name"
defaultNewDatasetAlias = "Dataset Index Alias"
defaultNewDatasetDescription = "Dataset Index Description"

st.session_state.newDatasetName = defaultNewDatasetName
st.session_state.newDatasetAlias = defaultNewDatasetAlias
st.session_state.newDatasetDescription = defaultNewDatasetDescription

st.title('Datasets')

def formatMappings(mapping):
    if 'alias' in mapping:
        print('Need to handle aliases.')
        return mapping
    else:
        fields = []
        properties = mapping[list(mapping.keys())[0]]['mappings']['properties']
        for key in properties.keys():

            property = properties[key]
            if 'type' in property and property['type'] in ['text', 'keyword', 'date' ,'date_range', 'long', 'ip', 'boolean']:
                fields.append(key)

            if 'fields' in property and 'keyword' in property['fields']:
                fields.append('{}.keyword'.format(key))

        return fields

def addNewDataset():
    name = st.session_state.newDatasetName
    alias = st.session_state.newDatasetAlias
    description = st.session_state.newDatasetDescription

    st.session_state.newDatasetName = defaultNewDatasetName
    st.session_state.newDatasetAlias = defaultNewDatasetAlias
    st.session_state.newDatasetDescription = defaultNewDatasetDescription

    # Fetch the mappings from Elasticsearch
    mapping = es.indices.get_mapping(index=alias)

    # Fetch some sample data from Elasticsearch
    body = {
        "size": 2,
        "query": {
            "match_all": {}
        }
    }
    response = es.search(index=alias, body=body)

    dataset = {
        "alias": alias,
        "mappings": formatMappings(dict(mapping)),
        "description": description,
        "sampleData": response['hits']['hits']
    }

    st.session_state.datasets[name] = dataset

    # Writing to sample.json
    with open("datasets.json", "w") as outfile:
        outfile.write(json.dumps(st.session_state.datasets, indent=2))

def editDataset(name, value):
    print('Editing', name, value)
    st.session_state.newDatasetName = name
    st.session_state.newDatasetAlias = value

for dataset in st.session_state.datasets.keys():
    col1, col2, col3 = st.columns([5,1,1])

    with col1:
        st.subheader(dataset)
    with col2:
        st.button(
            'Edit',
            use_container_width=True,
            key='edit-{}'.format(dataset),
            kwargs={"name": dataset, "value": st.session_state.datasets[dataset]},
            on_click=editDataset
        )
    with col3:
        st.button('Delete', use_container_width=True, key='delete-{}'.format(dataset), type='primary')

    st.code(st.session_state.datasets[dataset]['alias'])
    st.write(st.session_state.datasets[dataset]['description'])
    expander = st.expander("Mappings and Sample Data")
    expander.subheader('Mappings')
    expander.write(st.session_state.datasets[dataset]['mappings'])
    expander.subheader('Sample Data')
    expander.write(st.session_state.datasets[dataset]['sampleData'])

with st.form("newDatasetForm", clear_on_submit=True):
    st.write("Create a New dataset")
    newName = st.text_input('Datset Name', value=st.session_state.newDatasetName, key='newDatasetName')
    newAlias = st.text_input('Index Alias', value=st.session_state.newDatasetAlias, key='newDatasetAlias')
    newDescription = st.text_area('Datset Description', value=st.session_state.newDatasetDescription, key='newDatasetDescription')
    

   # Every form must have a submit button.
    submitted = st.form_submit_button("Submit", on_click=addNewDataset, use_container_width=True)
