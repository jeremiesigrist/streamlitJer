

import streamlit as st

st.title("ChatGPT-like clone")


try:
    # st.write('ST SECRET')
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    import os
    # st.write('ST OS')
    openai_api_key = os.getenv("OPENAI_API_KEY")
    # st.write('ST OS end', openai_api_key)

from openai import OpenAI

client = OpenAI(api_key=openai_api_key)

component = "chatGPT_by_Jer_V2" 

if component not in st.session_state:
    st.session_state[component] = {}

if "openai_model" not in st.session_state[component]:
    st.session_state[component]["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state[component]:
    st.session_state[component]['messages'] = []

for message in st.session_state[component]['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state[component]['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(model=st.session_state[component]["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state[component]['messages']
            ],
            stream=True):
            st.write(response.choices[0])
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state[component]['messages'].append({"role": "assistant", "content": full_response}) 