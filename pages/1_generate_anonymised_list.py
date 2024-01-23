import streamlit as st
import spacy
from nltk.corpus import wordnet
import nltk

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
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY")

nlp_model_EN = "en_core_web_md"
nlp_model_FR = "fr_core_news_md"

try:
    words2anon_list = st.secrets["WORDS_LIST"]
    cles = st.secrets["WORDS_KEY"]   # liste de mots a remplacer
    valeurs = st.secrets["WORDS_VALUE"]
    word_list_to_ignore = st.secrets["WORDS_TO_IGNORE"]
except Exception as e:
    import os
    words2anon_list = os.getenv("WORDS_LIST")
    cles = os.getenv("WORDS_KEY")
    valeurs = os.getenv("WORDS_VALUE")
    word_list_to_ignore = os.getenv("WORDS_TO_IGNORE")

WORDS_DICT = {}
for cle, valeur in zip(cles, valeurs):
    WORDS_DICT[cle] = valeur

nltk.download('wordnet')

def get_synonyms(word):
    # synonyms = []
    # for syn in wordnet.synsets(word):
    #     for lemma in syn.lemmas():
    #         synonyms.append(lemma.name())
    # return list(set(synonyms))

    synonyms = []
    
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    
    if synonyms:
        # S'il y a des synonymes, choisir aléatoirement l'un d'entre eux
        return random.choice(synonyms)
    else:
        # S'il n'y a pas de synonyme, générer une chaîne aléatoire de longueur 5
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))


import random
import string

def check_anonimization(text, words_list):
    nlp = st.session_state['nlp']
    doc = nlp(text)
    lemmatized_words = [token.lemma_ for token in doc]
    filtered_words = set([word for word in lemmatized_words if len(word) > 2 and (len(word) != 3 or word.isupper()) and word not in words_list])
    result_synonyms = {word: get_synonyms(word) for word in filtered_words}
    return filtered_words, result_synonyms



def update_lists(selected_words, synonyms, words_to_ignore):
    for word in selected_words:
        if word not in cles:
            cles.append(word)
    
            valeurs.append(synonyms[word])

    for word in words_to_ignore:
        if word not in word_list_to_ignore:
            word_list_to_ignore.append(word)       

def main():
    st.title("Anonymisation de texte avec Streamlit")

    with st.sidebar:
        if 'nlp_EN' not in st.session_state:
            st.session_state['nlp_EN'] = spacy.load(nlp_model_EN)
        if 'nlp' not in st.session_state:
            st.session_state['nlp'] = st.session_state['nlp_EN']
            st.session_state['lang'] = 'EN'

    text_to_analyze = st.text_area("Entrez le texte à analyser:", "")
    
    # Concaténer cles et WORDS_TO_IGNORE pour former words_to_exclude
    words_to_exclude = cles + word_list_to_ignore

    # Définir une clé unique pour le formulaire
    form_key = 'selection_form'

    # Afficher le formulaire
    with st.form(key=form_key):
        st.subheader("Mots à anonymiser:")
        result, synonyms = check_anonimization(text_to_analyze, words_to_exclude)
        selected_words = []
        
        # Parcourir les résultats et créer des cases à cocher dans le formulaire
        for word in result:
            checkbox_selected = st.checkbox(word, key=word)
            if checkbox_selected:
                selected_words.append(word)
        
        # Ajouter un bouton au bas du formulaire pour afficher les résultats
        if st.form_submit_button("Afficher les mots sélectionnés et leurs synonymes"):
            # Stocker les résultats dans st.session_state pour éviter le rechargement de la page
            st.session_state.selected_words = selected_words
            st.session_state.non_selected_words = list(result - set(selected_words))
            st.session_state.synonyms = {word: synonyms[word] for word in selected_words}

    # Afficher les résultats à partir de st.session_state après le formulaire
    if 'selected_words' in st.session_state and st.session_state.selected_words:
        st.subheader("Mots sélectionnés et leurs synonymes:")
        update_lists(st.session_state.selected_words, st.session_state.synonyms, st.session_state.non_selected_words)
        for word in st.session_state.selected_words:
            st.write(f"{word}: {st.session_state.synonyms[word]}")

    # Afficher les mots non sélectionnés
    if 'non_selected_words' in st.session_state and st.session_state.non_selected_words:
        st.subheader("Mots non sélectionnés:")
        st.write(", ".join(st.session_state.non_selected_words))

    st.write("WORDS_KEY = {}".format(cles))
    st.write("WORDS_VALUE = {}".format(valeurs))
    st.write("WORDS_TO_IGNORE = {}".format(word_list_to_ignore))

if __name__ == "__main__":
    main()