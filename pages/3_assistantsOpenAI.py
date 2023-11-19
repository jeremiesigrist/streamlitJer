# Import necessary libraries
import openai
import streamlit as st
from bs4 import BeautifulSoup
import requests
import pdfkit
import time
import os
import pickle
import re
import datetime

# Set your OpenAI Assistant ID here
assistant_id = os.getenv("assistant_id1")

# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
client = openai
 


# Fonction pour sauvegarder la variable dans un fichier
def sauvegarder_variable(variable, nom_fichier):
    with open(nom_fichier, 'wb') as fichier:
        pickle.dump(variable, fichier)

# Fonction pour charger la variable depuis un fichier
def charger_variable(nom_fichier):
    with open(nom_fichier, 'rb') as fichier:
        variable = pickle.load(fichier)
    return variable

def convertir_en_nom_de_fichier(chaine):
    # Supprimer les caractères spéciaux et les espaces
    chaine = re.sub(r'[^\w\s]', ' ', chaine)
    # Remplacer les espaces par des tirets bas
    chaine = chaine.replace(' ', '_')
    # Limiter la longueur à 255 caractères (limite généralement acceptée sur de nombreux systèmes de fichiers)
    chaine = chaine[:255]
    # Supprimer les tirets bas consécutifs et en fin de chaîne
    chaine = re.sub('_+', '_', chaine)
    chaine = chaine.rstrip('_')
    return chaine

# Dossier où seront stockés les fichiers
dossier_fichiers_init = 'fichiers_sessions'

local_session_name = "3_assistantsOpenAI"

dossier_fichiers = dossier_fichiers_init + '/' + local_session_name

os.makedirs(dossier_fichiers, exist_ok=True)

if local_session_name not in st.session_state:
    st.session_state[local_session_name] = {}
 
local_session = st.session_state[local_session_name]

# Initialize session state variables for file IDs and chat control
if "file_id_list" not in local_session:
    local_session['file_id_list'] = []

# local_session['AAAA']="TUTUT_TEZRTZETRZERTZERT"

# st.write(st.session_state)

# if "start_chat" not in st.session_state:
#     local_session['start_chat'] = False

if "thread_id" not in local_session:    
    thread = client.beta.threads.create()
    local_session['thread_id'] = thread.id

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="ChatGPT-like Chat App", page_icon=":speech_balloon:")

# Define functions for scraping, converting text to PDF, and uploading to OpenAI
def scrape_website(url):
    """Scrape text from a website URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()

def text_to_pdf(text, filename):
    """Convert text content to a PDF file."""
    path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_string(text, filename, configuration=config)
    return filename

def upload_to_openai(filepath):
    """Upload a file to OpenAI and return its file ID."""
    with open(filepath, "rb") as file:
        response = openai.files.create(file=file, purpose="assistants")
    return response.id


# Barre de menu latérale
expander_sessions = st.sidebar.expander(label = "Liste des conversations", expanded=True)

# st.sidebar.title('Liste des conversations')

# Liste des fichiers existants
# fichiers_existant = os.listdir(dossier_fichiers)


# Liste des fichiers existants avec les chemins complets
chemins_fichiers = [os.path.join(dossier_fichiers, fichier) for fichier in os.listdir(dossier_fichiers)]
# st.write(chemins_fichiers)
# Trier les fichiers par date de création croissante
fichiers_existant = sorted(chemins_fichiers, key=os.path.getctime, reverse=True)
# st.write(fichiers_existant)

# Si aucun fichier n'existe, afficher un message
if not fichiers_existant:
    expander_sessions.warning("Pas encore de sessions enregistrée.")
else:
    for fichier in fichiers_existant:
        # fichier_path = os.path.join(dossier_fichiers, fichier)

        timestamp_creation = os.path.getctime(fichier)
        date_creation = datetime.datetime.fromtimestamp(timestamp_creation).strftime("%Y-%m-%d  %H:%M:%S")
        bouton_texte = f"{fichier.replace(dossier_fichiers+'/','')}"
        bouton_help = f"Date d'enregistrement: {date_creation}"

        if expander_sessions.button(bouton_texte, help=bouton_help):
            # Action à effectuer lorsqu'un bouton est cliqué
            # st.write(f"Vous avez cliqué sur le fichier {fichier}")
            # Charger la variable du fichier sélectionné
            st.session_state[local_session_name] = charger_variable(fichier)

            local_session = st.session_state[local_session_name]

            # st.write('Variable chargée:', local_session)


# Create a sidebar for API key configuration and additional features
# st.sidebar.header("Configuration")

try:
    # st.write('ST SECRET')
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    import os
    # st.write('ST OS')
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        openai_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
 
if openai_api_key:
    openai.api_key = openai_api_key

# Additional features in the sidebar for web scraping and file uploading
expander = st.sidebar.expander(label = "Additional Features", expanded=False)
# st.sidebar.header("Additional Features")
website_url = expander.text_input("Enter a website URL to scrape and organize into a PDF", key="website_url")

# Button to scrape a website, convert to PDF, and upload to OpenAI
if expander.button("Scrape and Upload"):
    # Scrape, convert, and upload process
    scraped_text = scrape_website(website_url)
    pdf_path = text_to_pdf(scraped_text, "content/scraped_content.pdf")
    file_id = upload_to_openai(pdf_path)
    local_session['file_id_list'].append(file_id)
    #st.sidebar.write(f"File ID: {file_id}")

# Sidebar option for users to upload their own files
uploaded_file = expander.file_uploader("Upload a file to OpenAI embeddings", key="file_uploader")

# Button to upload a user's file and store the file ID
if expander.button("Upload File"):
    # Upload file provided by user
    if uploaded_file:
        with open(f"content/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        additional_file_id = upload_to_openai(f"content/{uploaded_file.name}")
        local_session['file_id_list'].append(additional_file_id)
        expander.write(f"Additional File ID: {additional_file_id}")

# Display all file IDs
if local_session['file_id_list']:
    expander.write("Uploaded File IDs:")
    for file_id in local_session['file_id_list']:
        expander.write(file_id)
        # Associate files with the assistant
        assistant_file = client.beta.assistants.files.create(
            assistant_id=assistant_id, 
            file_id=file_id
        )

# # Button to start the chat session
# if st.sidebar.button("Start Chat"):
#     # Check if files are uploaded before starting chat
#     if local_session['file_id_list']:
#         local_session['start_chat'] = True
#         # Create a thread once and store its ID in session state
#         thread = client.beta.threads.create()
#         local_session['thread_id'] = thread.id
#         st.write("thread id: ", thread.id)
#     else:
#         st.sidebar.warning("Please upload at least one file to start the chat.")



# Button to start the chat session ================== MODIF BY JER
if st.sidebar.button("Start a new Chat"):
    st.session_state[local_session_name] = {}

    local_session = st.session_state[local_session_name]    

    # # Check if files are uploaded before starting chat
    # local_session['start_chat'] = True
    # # Create a thread once and store its ID in session state
    # thread = client.beta.threads.create()
    # local_session['thread_id'] = thread.id
    # # st.write("thread id: ", thread.id)


# # Button to start the chat session ================== MODIF BY JER
# if st.sidebar.button("Start Chat"):
#     # Check if files are uploaded before starting chat
local_session['start_chat'] = True
# Create a thread once and store its ID in session state
# thread = client.beta.threads.create()
# local_session['thread_id'] = thread.id
# st.write("thread id: ", thread.id)    

# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {'filename': 'cited_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            # Placeholder for file download citation
            cited_file = {'filename': 'downloaded_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}')  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + '\n\n' + '\n'.join(citations)
    return full_response



# Main chat interface setup
from PIL import Image
image = Image.open('pages/images/_d4dc0b47-ad66-4004-aad1-509cb34d3d18.jpg')

col1, mid, col2 = st.columns([1,5,30])
with col1:
    st.image(image, width=100 )
with col2:
    st.title("Assistant et Coach")



st.write("Tu peux continuer une conversation passée en cliquant sur le bouton correspondant à gauche")
st.write("Tu peux uploader des fichiers d'instruction pour m'aider (en tant que coach) à améliorer mes reponses")

# Only show the chat interface if the chat has been started
# if local_session['start_chat']:
# Initialize the model and messages list if not already in session state
options_models = ["gpt-4-1106-preview", "gpt-3.5-turbo-1106"]
if "openai_model" not in local_session:
    # Liste d'options


    # Sélection de l'option
    local_session['openai_model'] = st.sidebar.selectbox("Model", options_models)
    # local_session['openai_model'] = "gpt-4-1106-preview"   # gratuit jusqu'au 17/11 ==> NON
    # local_session['openai_model'] = "gpt-3.5-turbo-1106"   
else:
    index = options_models.index(local_session['openai_model'])
    st.sidebar.selectbox('Model', options_models, index=index)

if "messages" not in local_session:
    local_session['messages'] = []

# Display existing messages in the chat
for message in local_session['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for the user
if prompt := st.chat_input("Bonjour comment vas tu aujourd'hui?"):
    # Add user message to the state and display it
    local_session['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add the user's message to the existing thread
    client.beta.threads.messages.create(
        thread_id=local_session['thread_id'],
        role="user",
        content=prompt
    )

    # Create a run with additional instructions
    run = client.beta.threads.runs.create(
        thread_id=local_session['thread_id'],
        assistant_id=assistant_id,
        # instructions="Please answer the queries using the knowledge provided in the files.When adding other information mark it clearly as such.with a different color"
    )

    # Poll for the run to complete and retrieve the assistant's messages
    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=local_session['thread_id'],
            run_id=run.id
        )

    # Retrieve messages added by the assistant
    messages = client.beta.threads.messages.list(
        thread_id=local_session['thread_id']
    )

    # Process and display assistant messages
    assistant_messages_for_run = [
        message for message in messages 
        if message.run_id == run.id and message.role == "assistant"
    ]
    for message in assistant_messages_for_run[::-1]:
        full_response = process_message_with_citations(message)
        local_session['messages'].append({"role": "assistant", "content": full_response})
        with st.chat_message("assistant"):
            st.markdown(full_response, unsafe_allow_html=True)

# st.write(st.session_state)

if len(local_session["messages"]) > 0:
    # st.write("sauvegarde de la sessions")
    nom_fichier_valide = convertir_en_nom_de_fichier(local_session["messages"][0]["content"][:30])
    nom_fichier_valide = nom_fichier_valide+'.pck'
    # st.write(nom_fichier_valide)
    if prompt:
        sauvegarder_variable(local_session, dossier_fichiers + '/' + nom_fichier_valide)

# else:
#     # Prompt to start the chat
#     st.write("tu peux uploader des fichiers d'instruction pour m'aider (en tant que coach) à améliorer mes reponses")