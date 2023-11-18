import streamlit as st
import os
import re

# Fonction pour supprimer l'extension d'un fichier et le préfixe numérique
def remove_file_extension(filename):
    name_without_extension = filename.rsplit('.', 1)[0]
    modified_name = re.sub(r'^\d+_', '', name_without_extension)
    return modified_name

# Fonction pour scanner le répertoire et obtenir une liste des fichiers triés
def scanner_repertoire(repertoire):
    fichiers = sorted(os.listdir(repertoire))
    return fichiers

# Fonction utilitaire pour charger l'image s'il elle existe
def charger_image(fichier):
    image_path = os.path.join(repertoire_images, fichier + '.jpg')
    return image_path if os.path.exists(image_path) else None

# Affichage des liens avec des images en colonnes multiples
def afficher_liens(fichiers):
    # Nombre de colonnes pour la grille d'images
    cols_per_row = 4

    # Filtrer et garder seulement les fichiers ayant une image correspondante
    fichiers_avec_image = [f for f in fichiers if charger_image(remove_file_extension(f))]

    # Parcourir la liste de fichiers avec image et les afficher sur la grille
    for idx in range(0, len(fichiers_avec_image), cols_per_row):
        cols = st.columns(cols_per_row)
        for i in range(cols_per_row):
            if idx + i < len(fichiers_avec_image):
                fichier = fichiers_avec_image[idx + i]
                clean_name = remove_file_extension(fichier)
                image_path = charger_image(clean_name)
                url = f"{site_web}{clean_name}"
                with cols[i]:
                    st.image(image_path, width=130, caption=clean_name)
                    st.markdown(f"[Lire la suite...]({url})", unsafe_allow_html=True)

# Configurer la page Streamlit
st.set_page_config(page_title='My Python Experiments', layout='wide')

# En-tête de la page
st.title("My Python Experiments")
st.image("https://www.python.org/static/img/python-logo.png", width=500)
st.markdown("This page contains a collection of my experiments in Python.")
st.markdown("**GitHub repository:** [jeremiesigrist/streamlitJer](https://github.com/jeremiesigrist/streamlitJer)")

# Définition des chemins
repertoire = "./pages"
repertoire_images = os.path.join(repertoire, "images")
site_web = "https://streamlit.sigrist31.online/"

# Scanner le répertoire et afficher les fichiers avec leurs images sous forme de grille
fichiers = scanner_repertoire(repertoire)
afficher_liens(fichiers)