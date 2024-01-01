import streamlit as st
import subprocess
import plotly.graph_objs as go
from datetime import datetime

# Commande à exécuter pour obtenir les logs filtrés
command = "tail -n 50000 /dataJer/homeassistant/config/home-assistant.log | grep --color=auto '.pi_algorithm' | grep --color=auto 'target_tem: 19' | sed 's/DEBUG (MainThread) \[custom_components.versatile_thermostat.pi_algorithm\] PITemperatureRegulator//g'"

# Fonction pour lire les données filtrées et les convertir en listes pour le traçage
def read_logs():
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        bufsize=1,
        universal_newlines=True,
    )

    timestamps = []
    error_values = []
    accumulated_errors = []
    offsets = []
    target_temps = []
    regulated_temps = []

    for line in p.stdout:
        try:
            parts = line.split()
            timestamp = parts[0] + ' ' + parts[1]
            timestamps.append(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f"))

            error_value = float(parts[4])
            error_values.append(error_value)

            accumulated_error = float(parts[6])
            accumulated_errors.append(accumulated_error)

            offset = float(parts[8])
            offsets.append(offset)

            target_temp = float(parts[12])
            target_temps.append(target_temp)

            regulated_temp = float(parts[14])
            regulated_temps.append(regulated_temp)
        except (IndexError, ValueError):
            pass

    return timestamps, error_values, accumulated_errors, offsets, target_temps, regulated_temps

# Lecture des données filtrées
timestamps, error_values, accumulated_errors, offsets, target_temps, regulated_temps = read_logs()

# Création de la série "Température mesurée" (somme de la température cible et de l'erreur)
mesured_temps = [target - error for target, error in zip(target_temps, error_values)]

# Création du graphique avec Plotly
fig = go.Figure()

fig.add_trace(go.Scatter(x=timestamps, y=error_values, mode='lines+markers', name='Évolution de l\'erreur'))
fig.add_trace(go.Scatter(x=timestamps, y=accumulated_errors, mode='lines+markers', name='Erreur accumulée', yaxis='y2'))
fig.add_trace(go.Scatter(x=timestamps, y=offsets, mode='lines+markers', name='Offset', yaxis='y3'))
fig.add_trace(go.Scatter(x=timestamps, y=target_temps, mode='lines+markers', name='Température cible', yaxis='y4'))
fig.add_trace(go.Scatter(x=timestamps, y=regulated_temps, mode='lines+markers', name='Température régulée', yaxis='y4'))
fig.add_trace(go.Scatter(x=timestamps, y=mesured_temps, mode='lines+markers', name='Température mesurée', yaxis='y4'))

# Mise à jour de la visibilité de la légende pour l'erreur (index 0)
fig.update_traces(visible="legendonly", selector=dict(name='Évolution de l\'erreur'))


fig.update_layout(
    title='Évolution des différentes données',
    xaxis_title='Temps',
    width=1500,  # Largeur du graphique
    height=900,  # Hauteur du graphique    
    yaxis=dict(title='Erreur'),
    yaxis2=dict(title='Erreur accumulée', overlaying='y', side='right'),
    yaxis3=dict(title='Offset', overlaying='y', side='right'),
    yaxis4=dict(title='Température', overlaying='y', side='right')
)

# Affichage du graphique avec Streamlit
st.plotly_chart(fig)
