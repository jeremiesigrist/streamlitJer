import streamlit as st
import pandas as pd
import requests
from pytz import timezone


# autre url a tester ==> 
# http://192.168.0.158/index.php/hidden
# http://192.168.0.158/index.php/display/record
# http://192.168.0.158/index.php/meter/old_meter_energy_graph
# http://192.168.0.158/index.php/display/historical_data/meter_lifetime_energy/
                            # item	chip	lifetime_energy
                            # 1	    1	    58.3031249999997
                            # 1	    2	    148.35625

# http://192.168.0.158/index.php/display/historical_data        ==> lifetime energy
                            # item	lifetime_energy
                            # 1	    63.715446

# Fonction pour récupérer les données depuis l'API
def get_data():
    url = "http://192.168.0.158/index.php/meter/old_meter_power_graph"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Récupération des données
data = get_data()

if data:
    # Conversion des données power1 en DataFrame Pandas
    power1_data = data.get('power1', [])
    if power1_data:
        df_power1 = pd.DataFrame(power1_data)
        df_power1['time'] = pd.to_datetime(df_power1['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Europe/Paris')
        df_power1 = df_power1.rename(columns={'powerA': 'Production PV'})
        df_power1 = df_power1[['time', 'Production PV']]
    else:
        df_power1 = pd.DataFrame()

    # Conversion des données power2 en DataFrame Pandas
    power2_data = data.get('power2', [])
    if power2_data:
        df_power2 = pd.DataFrame(power2_data)
        df_power2['time'] = pd.to_datetime(df_power2['time'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Europe/Paris')
        df_power2 = df_power2.rename(columns={'powerA': '+From Grid -To'})
        df_power2 = df_power2[['time', '+From Grid -To']]
    else:
        df_power2 = pd.DataFrame()

    # Fusionner les colonnes 'Production PV' de df_power1 et '+From Grid -To' de df_power2 sur la colonne 'time'
    merged_df = pd.merge(df_power1, df_power2, on='time')

    # Inverser l'ordre des résultats du tableau par la colonne 'time'
    merged_df = merged_df.sort_values(by='time', ascending=False)

    # Affichage du DataFrame fusionné inversé dans Streamlit
    st.write("Tableau Fusionné (Ordre Inversé):")
    st.write(merged_df)

    # Créer un graphique en barres avec les dates au fuseau horaire de Paris
    st.write("Graphique en barres:")
    st.bar_chart(merged_df.set_index('time'))

else:
    st.write("Erreur lors de la récupération des données depuis l'API.")
