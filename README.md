# chat-with-your-data

This demo is still very much a work in progress, but is good enough for people to play around with if they want to and are adventuresome.

## Getting started

Before running, you need to create a `.streamlit/secrets.toml` file. There is a starter file provided at `.streamlit/secrets.toml.example`. So to get started:

```
cp secrets.toml.example secrets.toml
vim secrets.toml
```

Enter your Cluster details and your openai API key. Now you're ready to run the streamlit app:

### Docker
The simplest way to get started is to just `docker-compose up` assuming you have docker installed. This will build 

### Local
If you want locally then something like the below should work:

1. `conda create --name streamlit python=3.11`
2. `conda install pip`
3. `pip install -r requirements.txt`
4. `streamlit run chat.py`