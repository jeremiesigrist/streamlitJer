import streamlit as st

# Set the title of the page
st.title("My Python Experiments")

# Add an image to the page
st.image("https://www.python.org/static/img/python-logo.png", width=500)

# Add a brief description of the page
st.markdown("This page contains a collection of my experiments in Python.")

# Add a list of the experiments
st.markdown("**Experiments:**")

experiments = [
  "chatGPT by Jer"
]

for experiment in experiments:
  st.markdown(experiment)

# Add a link to the GitHub repository for the experiments
st.markdown("**GitHub repository:**")

st.markdown("https://github.com/jeremiesigrist/streamlitJer")

# Add a call to action
st.markdown("**Get started:**")
st.button("Click here to start experimenting with Python!")





# streamlit run Home.py --server.enableCORS false --server.enableXsrfProtection false --server.port 8505 --theme.base dark &