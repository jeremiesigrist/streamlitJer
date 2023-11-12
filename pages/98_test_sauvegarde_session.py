import streamlit as st
import os
import pickle

# Fonction pour sauvegarder la variable dans un fichier
def sauvegarder_variable(variable, nom_fichier):
    with open(nom_fichier, 'wb') as fichier:
        pickle.dump(variable, fichier)

# Fonction pour charger la variable depuis un fichier
def charger_variable(nom_fichier):
    with open(nom_fichier, 'rb') as fichier:
        variable = pickle.load(fichier)
    return variable

# Dossier où seront stockés les fichiers
dossier_fichiers_init = 'fichiers_sessions'
local_session_name = "98_test_sauvegarde_session"
dossier_fichiers = dossier_fichiers_init + '/' + local_session_name

os.makedirs(dossier_fichiers, exist_ok=True)

if local_session_name not in st.session_state:
    st.session_state[local_session_name] = {}
 
local_session = st.session_state[local_session_name]



# Barre de menu latérale
st.sidebar.title('Liste des sessions')

# Liste des fichiers existants
fichiers_existant = os.listdir(dossier_fichiers)

# Si aucun fichier n'existe, afficher un message
if not fichiers_existant:
    st.sidebar.warning("Aucun fichier existant.")
else:
    for fichier in fichiers_existant:
        fichier_path = os.path.join(dossier_fichiers, fichier)
        if st.sidebar.button(fichier):
            # Action à effectuer lorsqu'un bouton est cliqué
            st.write(f"Vous avez cliqué sur le fichier {fichier}")
            # Charger la variable du fichier sélectionné
            variable_chargee = charger_variable(fichier_path)
            st.write('Variable chargée:', variable_chargee)


# Saisie de nombre
age_utilisateur = st.number_input("Entrez votre âge:")

local_session["AGE"] = age_utilisateur

sauvegarder_variable(local_session, dossier_fichiers + '/age_'+str(local_session["AGE"])+'.pck')


