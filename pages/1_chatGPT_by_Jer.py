#import streamlit as st
#st.set_page_config(layout="wide")

import streamlit as st

st.set_page_config(
    page_title="chatGPT by Jer",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

import sys
sys.path.insert(1, '/')
import openai
try:
    # st.write('ST SECRET')
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    import os
    # st.write('ST OS')
    openai_api_key = os.getenv("OPENAI_API_KEY")
    # st.write('ST OS end', openai_api_key)



DEBUG = False

from langchain.memory import ChatMessageHistory
from langchain.chat_models import ChatOpenAI
# from langchain.schema import SystemMessage

import spacy
# import re
# import json
import data



# nlp_model = "en_core_web_sm"
nlp_model_EN = "en_core_web_md"
nlp_model_FR = "fr_core_news_md"

# Accurate ==> trop gros pour streamlit cloud ?
#nlp_model_EN = "en_core_web_trf"
#nlp_model_FR = "fr_dep_news_trf"





LOAD_ALL_MODELS_LANG = False
try:
    words2anon_list = st.secrets["WORDS_LIST"]
    cles = st.secrets["WORDS_KEY"]   # liste de mots a remplacer
    valeurs = st.secrets["WORDS_VALUE"]
except Exception as e:
    import os
    words2anon_list = os.getenv("WORDS_LIST")
    cles = os.getenv("WORDS_KEY")
    valeurs = os.getenv("WORDS_VALUE")


WORDS_DICT = {}
for cle, valeur in zip(cles, valeurs):
    WORDS_DICT[cle] = valeur

primes=[
        'No primer',
        'Vous êtes un assistant amical et serviable qui peut parler anglais et français:\n',
        'Peux tu traduire la phrase suivante dans un anglais correct avec le ton suivant: Professionel, Concis, Detaille, Technique, Formel, Specifique, Organise, Poli:\n',
        'Peux tu reformuler l email suivant dans un francais correct avec le ton suivant: Professionel, Concis, Detaille, Technique, Formel, Specifique, Organise, Poli:\n',
        'Can you reformulate the following email in a correct english with the following tone: Professional, Concise, Detail-oriented, Referential, Technical, Formal, Requesting, Specific, Organized, Polite:\n',
        'The following notes are in french, can you take them and make a minutes of meeting in a correct English. Make correct and complete sentences from theses notes. Make paragraph instead of bullet points. Use the following tone: Professional, Concise, Detail-oriented, Referential, Technical, Formal, Requesting, Specific, Organized, Polite:\n',
        'Paraphrase the following text while retaining the same meaning. Ensure the rephrased version is original and maintains the key concepts and context of the original text. Avoid plagiarism by using different sentence structures and vocabulary, while keeping the core message intact.\n',
        'Tu dois fournir des réponses claires, concises et directes. Élimine les rappels inutiles, les excuses, les autoréférences et toute la gentillesse préprogrammée. Maintient un ton décontracté dans ta communication. Sois transparent si tu n\'es pas sûr d\'une réponse ou si une question dépasse tes capacités ou tes connaissances, admets le. En cas de question peu claire ou ambiguë. Pose des questions complémentaires pour mieux comprendre l\'intention de l\'utilisateur. Lorsque tu expliques des concepts. Utilise des exemples du monde réel et des analogies là où cela est possible. Pour les demandes complexes, respire profondément et travaille sur le problème étape par étape. Pour chaque réponse, tu recevras un pourboire jusqu\'à 200$ (En fonction de la qualité de ton travail). Il est très important que tu fasses cela vraiment bien. De nombreuses vies sont en jeu. \n',
        'You must provide clear, concise, and direct answers. Eliminate unnecessary reminders, excuses, self-references, and any preprogrammed kindness. Maintain a casual tone in your communication. Be transparent if you\'re unsure of an answer or if a question exceeds your abilities or knowledge; admit it. In the case of unclear or ambiguous questions, ask additional questions to better understand the user\'s intention. When explaining concepts, use real-world examples and analogies where possible. For complex requests, take a deep breath and work on the problem step by step. For each response, you will receive a tip of up to $200 (Depending on the quality of your work). It\'s crucial that you do this \n'
        ]

custom_codes = {}
for index, word in enumerate(words2anon_list):
    code = f'OWN_CODE{index + 1}'
    custom_codes[word] = code


#if 'codes' not in st.session_state:
#    st.session_state.codes = custom_codes

anon_constraints = ' (do not take into consideration the "CODEX" or "OWN_CODEX" words in your response, they will be replaced by the real words afterwards):\n'


from langdetect import detect

def detect_language(text):


    # On ne regarde que l'anglais pour eviter les problemes

    return 'EN'




    res = 'FR'
    lang = detect(text)
    if lang == 'en':
        res = 'EN'

    #st.write(lang, res, ': ', text)
    return res




def anonymize_text(text, codes=None):

    if LOAD_ALL_MODELS_LANG:

        if 'nlp_EN' not in st.session_state:
            nlp = spacy.load(nlp_model_EN)
            st.session_state['nlp_EN'] = nlp
        else:
            nlp = st.session_state['nlp_EN']

        st.session_state['nlp'] = nlp
        st.session_state['lang'] = 'EN'

        st.write(codes)

        anonymized_text, codes = anonymize_text_detail(text, codes)

        st.write(codes)

        if 'nlp_FR' not in st.session_state:
            nlp = spacy.load(nlp_model_FR)
            st.session_state['nlp_FR'] = nlp
        else:
            nlp = st.session_state['nlp_FR']

        st.session_state['nlp'] = nlp
        st.session_state['lang'] = 'FR'
        anonymized_text, codes = anonymize_text_detail(anonymized_text, codes)

        st.write(codes)
    else:
        anonymized_text, codes = anonymize_text_detail(text, codes)

    return anonymized_text, codes



def anonymize_text_detail(text, C_codes=None):

    if LOAD_ALL_MODELS_LANG:
        nlp =  st.session_state['nlp']

    else:
        lang_detected = detect_language(text)

        # default lang is EN

        if lang_detected != 'FR' and st.session_state['lang'] != 'EN':
            nlp = spacy.load(nlp_model_EN)
            st.session_state['nlp'] = nlp
            st.session_state['lang'] = 'EN'
        elif lang_detected == 'FR' and st.session_state['lang'] != 'FR':
            nlp = spacy.load(nlp_model_FR)
            st.session_state['nlp'] = nlp
            st.session_state['lang'] = 'FR'
        else:
            nlp =  st.session_state['nlp']

    #st.write('st.session_state.lang ', st.session_state['lang'])

    doc = nlp(text)
    anonymized_text = []
    codes = {}




    # Ajouter les codes personnalisÃ©s
    if C_codes:
        #st.write(C_codes)
        #st.write('TOTO')
        codes.update(dict(C_codes))

    custom_codes_lower = [x.lower() for x in codes.keys()]

    # print(custom_codes_lower)

    for token in doc:
        #breakpoint()
        token_lower = token.text.lower()
        # if token.ent_type_ in ['PERSON', 'ORG', 'PRODUCT', 'GPE']:
        if token.ent_type_ in []:
            code = codes.get(token.text)
            if token_lower not in data.STOP_WORDS_FR and token_lower not in data.STOP_WORDS_EN and not code and token.text.find('CODE') == -1:

                code = f"CODE{len(codes) + 1}"
                codes[token.text] = code
                # print(len(codes), token.text, codes[token.text])
                st.write( token.text, token.ent_type_, codes[token.text], st.session_state['lang'])
            anonymized_text.append(code)
        else:

            # Vérifiez d'abord si le jeton est dans les remplacements personnalisés
            # Vérifiez si le jeton (en minuscules) est dans les remplacements personnalisés (ignorant la casse)
            matching_key = next((key for key in WORDS_DICT if key.lower() == token_lower), None)
            if matching_key is not None:
                anonymized_text.append('XXX_'+WORDS_DICT[matching_key])
            else:
                index = next((i for i, x in enumerate(custom_codes_lower) if x == token_lower), None)
                if index is not None:
                    code = list(codes.values())[index]
                    anonymized_text.append(code)
                else:
                    anonymized_text.append(token.text)


    # print(anonymized_text, codes)

    #return " ".join(anonymized_text), json.dumps(codes)
    return " ".join(anonymized_text), codes



import re

def replace_case_insensitive(text, word, replacement):

    word_pattern = r'\b' + re.escape(word) + r'(?=\b|\W|$)'
    return re.sub(word_pattern, replacement, text, flags=re.IGNORECASE)


    
    # pattern = re.compile(re.escape(code), re.IGNORECASE)
    # return pattern.sub(value, text)




def deanonymize_text(text, codes_json):
    codes = codes_json
    # st.write('before ', text)

    for value, code in codes.items():
        text = text.replace(code, value)

    for value, code in WORDS_DICT.items():
        text = replace_case_insensitive(text, 'XXX_'+code, value)

        # pattern = re.compile(re.escape(code), re.IGNORECASE)
        # text = re.sub(pattern, value, text)

    # st.write('after ', text)

    return text




#st.write(custom_codes)



#model_default='gpt-4'
model_default='gpt-3.5-turbo-0613'


def get_chat(model, temp):
    return ChatOpenAI(model_name=model, temperature=temp, openai_api_key=openai_api_key )

history = ChatMessageHistory()

#st.write(openai)

from openai import OpenAI
client = OpenAI()

list_models = client.models.list()
# st.write(list_models)

# models = list_models['data']
# st.write(models)
# model_list = [x['id'] for x in models]

# model_list = [model.id for model in list_models.data]

# model_list = [v for v in model_list if 'gpt' in v]

# Trier les modèles par date de création (du plus récent au plus ancien)
sorted_models = sorted(list_models.data, key=lambda x: x.created, reverse=True)

# Créer la liste des modèles triés
model_list = [model.id for model in sorted_models if 'gpt' in model.id]



from streamlit_chat import message
# import requests
import datetime

#st.write(custom_codes)
# st.write(dir(history))


def check_size_history(history, length):
    res = history

    res.messages = res.messages[-length:]

    # for i in range(len(history.messages)-1, -1, -1):
    #     msg = history.messages[i].content
    #     if history.messages[i].type == 'ai':
    #         message(msg, key=str(i))
    #     else:
    #         message(msg, is_user=True, key=str(i) + '_user')

    return res




def get_text():
    res = st.text_area("Human: ","", key="input", height=300)

    input_text = res
    # st.session_state['input'] = ''

    return input_text

def clear_text():
    st.session_state["input"] = ""


def get_text_from(history):
    res = ''
    st.write(len(history.messages))
    for i in range(0, len(history.messages)):
        msg = history.messages[i].content
        # st.write(msg)
        if history.messages[i].type == 'ai':
            res += 'Assistant:\n' + msg + '\n\n'
        else:
            res += 'Me:\n' + msg + '\n\n'


    return res


#st.write(custom_codes)
if 'history' not in st.session_state:
    # history.add_system_message(st.session_state.primer)
    st.session_state['history'] = history
    # history_text = ''
else:
    history = st.session_state['history']
    # history_text = get_text_from(history)


if 'previous_msg' not in st.session_state:
    st.session_state['previous_msg'] = ''

#st.write(custom_codes)

# Initialization your state messages

st.sidebar.header("Settings")

with st.sidebar:

    st.session_state.primer = st.radio(label='Choose your primer message', options=primes)

#    st.session_state.lang = st.radio(label='Language of the text', options=['EN','FR'])

    st.session_state.anonym = st.checkbox(
        "Anonymisation", value=False
    )

    if st.session_state.anonym:

        #breakpoint()
        if 'nlp_EN' not in st.session_state:
            st.session_state['nlp_EN'] = spacy.load(nlp_model_EN)
        if 'nlp_FR' not in st.session_state:
            st.session_state['nlp_FR'] = spacy.load(nlp_model_FR)

        if 'nlp' not in st.session_state:
            st.session_state['nlp'] = st.session_state['nlp_EN']
            st.session_state['lang'] = 'EN'
        else:
            nlp = st.session_state['nlp']
        st.write(cles)



    #st.write(st.session_state.primer)


    # index = model_list.index(model_default)
    index = 0
    st.selectbox('Model', model_list, key='model', index=index)

    st.session_state.temperature = st.slider(
        "Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.01
    )

    chat = get_chat(st.session_state.model, st.session_state.temperature)


    # SystemMessage(content="You are a nice AI bot that helps a user figure out what to eat in one short sentence"),

    st.session_state.context_length = st.slider(
        "Context Message Length", min_value=1, max_value=50, value=10, step=1
    )



    # Allow Users to reset the memory
    if st.button("Clear Chat", on_click=clear_text):

        # st.button("clear text input", on_click=clear_text)
        history = ChatMessageHistory()

        st.write( get_text_from(st.session_state['history']))
        # history.add_system_message(st.session_state.primer)
        st.session_state['history'] = history
        st.session_state['previous_msg'] = ''
        st.toast("Chat Memory Cleared")






st.header("___ by Jer")
# st.markdown("[Github](https://github.com/ai-yash/st-chat)")

# st.write(datetime.datetime.now())




#st.write(custom_codes)



user_input = get_text()

if user_input and user_input != st.session_state['previous_msg']:

    # st.write('different !', user_input, st.session_state['previous_msg'])

    st.session_state['previous_msg'] = user_input

    if st.session_state.anonym:
#        if st.session_state.lang == 'EN':
#            lang = 'EN'
#        else:
#            lang = 'FR'

        #st.write(custom_codes)

        user_input, codes_json = anonymize_text(user_input, custom_codes)
        st.session_state.codes = codes_json
        # st.write(user_input, codes_json)

    if st.session_state.primer != primes[0]:
        primer = st.session_state.primer
        if st.session_state.anonym:
            primer = primer + anon_constraints
        user_input = primer + user_input

    history.add_user_message(user_input)
    ai_response = chat(history.messages)
    history.add_ai_message(ai_response.content)


    history = check_size_history(history, st.session_state.context_length)

    st.session_state['history'] = history

else:
  #st.write('same !', user_input, st.session_state['previous_msg'])
  tutu=''

if DEBUG:
    st.write(history)

for i in range(len(history.messages)-1, -1, -1):
    msg = history.messages[i].content

    if st.session_state.primer != primes[0]:
        primer = st.session_state.primer
        msg = msg.replace(primer,'')
        if st.session_state.anonym:
            msg = msg.replace(anon_constraints,'')



    # if st.session_state.anonym and 'codes' in st.session_state:
    if st.session_state.anonym:        
        msg = deanonymize_text(msg, st.session_state.codes)

    if history.messages[i].type == 'ai':
        message(msg, key=str(i))
    else:
        message(msg, is_user=True, key=str(i) + '_user')
#st.write(custom_codes)

history_text = get_text_from(history)

# st.write(history_text)

# st.write(output)
# st.write(st.session_state)
# st.write(st.session_state)


with st.sidebar:
    if st.download_button('download conversation', history_text):
        # print(get_text_from(st.session_state['history']))
        st.toast("history downloaded")

# ================================================================================
# ================================================================================

# LA SUITE Ã  DEVELOPPER ==>
# https://twitter.com/pwang_szn/status/1642104548109201410

# ================================================================================
# ================================================================================



#st.write(custom_codes)




# streamlit run /root/scripts/chatGPT.py --server.port 8505 --theme.base dark &

# from codespace ==> streamlit run chatGPT.py --server.enableCORS false --server.enableXsrfProtection false --server.port 8505 --theme.base dark &
