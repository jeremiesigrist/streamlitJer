import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

coin_list = ["bitcoin", "cardano","ethereum", "algorand", "solana"]
# log = True

def fetch_daily_bitcoin_prices(start_date, end_date):
    # Convert dates to timestamps
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    # API Endpoint
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"

    # Parameters for the API
    params = {
        'vs_currency': 'usd',
        'from': start_timestamp,
        'to': end_timestamp
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse response JSON
        data = response.json()
        # We only want the 'prices' data
        prices = data['prices']
        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        # Convert timestamp to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        # Set date as the index
        df.set_index('date', inplace=True)
        # Drop the original timestamp column
        df.drop('timestamp', axis=1, inplace=True)
        return df
    else:
        print("Error:", response.status_code)
        return None

def fetch_weekly_coin_prices(coin, start_date, end_date):
    # Convert dates to timestamps
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    # API Endpoint
    url = "https://api.coingecko.com/api/v3/coins/"+coin+"/market_chart/range"

    print(url)

    # Parameters for the API
    params = {
        'vs_currency': 'usd',
        'from': start_timestamp,
        'to': end_timestamp
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse response JSON
        data = response.json()
        # We only want the 'prices' data
        prices = data['prices']
        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        # Convert timestamp to datetime
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        # Set date as the index
        df.set_index('date', inplace=True)
        # Resample data on a weekly basis, starting on Monday ('W-MON') and keep only 'price' column
        weekly_prices = df['price'].resample('W-MON').agg({'price': 'first'})
        return weekly_prices
    else:
        print("Error:", response.status_code)
        return None

def weekly_coin_prices(coin):
  # Define the range for the last two years up to today
  end_date = datetime.now()
  start_date = end_date - timedelta(days=5*365)  # Two years ago

  # Call the function
  # df_bitcoin = fetch_daily_bitcoin_prices(start_date, end_date)

  df_bitcoin = fetch_weekly_bitcoin_prices(coin, start_date, end_date)

  # Check the resulting DataFrame
  if df_bitcoin is not None:
      # Set option to display all rows
      pd.set_option('display.max_rows', None)
      # Print the entire DataFrame
      # print(df_bitcoin)
  else:
      print("Failed to fetch data.")

  return df_bitcoin


# Cache la fonction fetch_weekly_coin_prices
@st.cache_data
def cached_fetch_weekly_coin_prices(coin, start_date, end_date):
    return fetch_weekly_coin_prices(coin, start_date, end_date)

# Fonction pour calculer les signaux de trading
def trading_signals(df, window=20, no_of_std=2, rsi_window=14, rsi_sell_limit=70):
    # Calcul de la moyenne mobile simple (SMA)
    df['SMA'] = df['price'].rolling(window=window).mean()

    # Calcul de l'écart-type
    df['rolling_std'] = df['price'].rolling(window=window).std()

    # Calcul des bandes de Bollinger
    df['upper_band'] = df['SMA'] + (df['rolling_std'] * no_of_std)
    df['lower_band'] = df['SMA'] - (df['rolling_std'] * no_of_std)

    # Calcul du RSI
    delta = df['price'].diff()
    gain = delta.mask(delta < 0, 0).rolling(window=rsi_window).mean()
    loss = (-delta).mask(delta > 0, 0).rolling(window=rsi_window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Détecter les croisements de la bande inférieure de Bollinger
    df['Buy'] = (df['price'] > df['lower_band']) & (df['price'].shift(1) <= df['lower_band'].shift(1))

    # Détecter les croisements de la bande supérieure de Bollinger
    df['Sell'] = (df['price'] < df['upper_band']) & (df['price'].shift(1) >= df['upper_band'].shift(1))

    # Identifier les points de vente au moment du maximum des prix du Bitcoin et du RSI
    df['Sell'] = df['Sell'] & ((df['price'] == df['price'].rolling(window=3).max()) | (df['RSI'] > rsi_sell_limit))

    return df


# def fetch_latest_coin_info(coin):
#     # Endpoint de l'API pour obtenir les données du marché pour un coin spécifique
#     url = f"https://api.coingecko.com/api/v3/coins/{coin}"

#     # Effectue la requête GET à l'API
#     response = requests.get(url)

#     # Vérifie si la requête a été réussie
#     if response.status_code == 200:
#         # Parse la réponse en JSON
#         data = response.json()

#         # Extrait les données de marché nécessaires
#         market_data = data.get('market_data', {})

#         # Informations à extraire
#         last_price = market_data.get('current_price', {}).get('usd', 'N/A')
#         price_change_24h = market_data.get('price_change_percentage_24h', 'N/A')
#         price_change_7d = market_data.get('price_change_percentage_7d', 'N/A')
#         price_change_30d = market_data.get('price_change_percentage_30d', 'N/A')

#         # Retourner ces informations sous forme de dictionnaire
#         return {
#             'Dernier Prix (USD)': last_price,
#             'Variation de Prix sur 24h (%)': price_change_24h,
#             'Variation de Prix sur 7 jours (%)': price_change_7d,
#             'Variation de Prix sur 30 jours (%)': price_change_30d
#         }
#     else:
#         # Retourner un message d'erreur si la requête a échoué
#         return {"error": f"Failed to fetch data for {coin}. Status code: {response.status_code}"}

def fbn(nb):
    # import locale

    # # Configuration de la région pour le formatage des nombres
    # locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # Exemple pour la France, adapter à votre région
    if nb is not None:

        # formatted_big_number = locale.format_string("%d", nb, grouping=True)
        formatted_big_number = f"{nb:,}"

        return formatted_big_number
    else:
        return nb

@st.cache_data
def fetch_latest_coin_info(coin):

    # Endpoint de l'API pour obtenir les données du marché pour un coin spécifique
    url = f"https://api.coingecko.com/api/v3/coins/{coin}?localization=false&sparkline=false"

    # Effectue la requête GET à l'API
    response = requests.get(url)

    # Vérifie si la requête a été réussie
    if response.status_code == 200:
        # Parse la réponse en JSON
        data = response.json()

        # Extrait les données de marché nécessaires
        market_data = data.get('market_data', {})

        # Informations supplémentaires à extraire
        high_24h = market_data.get('high_24h', {}).get('usd', 'N/A')
        low_24h = market_data.get('low_24h', {}).get('usd', 'N/A')
        market_cap = market_data.get('market_cap', {}).get('usd', 'N/A')
        market_cap_rank = data.get('market_cap_rank', 'N/A')
        all_time_high = market_data.get('ath', {}).get('usd', 'N/A')
        all_time_high_date = market_data.get('ath_date', {}).get('usd')
        if all_time_high_date:
            all_time_high_date = datetime.fromisoformat(all_time_high_date).strftime('%Y-%m-%d')
        circulating_supply = market_data.get('circulating_supply', 'N/A')
        total_supply = market_data.get('total_supply', 'N/A')
        max_supply = market_data.get('max_supply', 'N/A')
        dominance = market_data.get('market_cap_dominance', 'N/A')
        total_volume = market_data.get('total_volume', {}).get('usd', 'N/A')

        return {
            'Dernier Prix (USD)': market_data.get('current_price', {}).get('usd', 'N/A'),
            'Variation de Prix sur 24h (%)': market_data.get('price_change_percentage_24h', 'N/A'),
            'Variation de Prix sur 7 jours (%)': market_data.get('price_change_percentage_7d', 'N/A'),
            'Variation de Prix sur 30 jours (%)': market_data.get('price_change_percentage_30d', 'N/A'),
            'Haute des 24h (USD)': fbn(high_24h),
            'Basse des 24h (USD)': fbn(low_24h),
            'Capitalisation Boursière (USD)': fbn(market_cap),
            'Rang de Capitalisation Boursière': market_cap_rank,
            'Plus Haut Historique (USD)': fbn(all_time_high),
            'Date du Plus Haut Historique': all_time_high_date,
            'Circulation Supply': fbn(circulating_supply),
            'Total Supply': fbn(total_supply),
            'Max Supply': fbn(max_supply),
            'Dominance de marché (%)': dominance,
            'Volume Total échangé sur 24h (USD)': fbn(total_volume)
        }
    else:
        # Retourner un message d'erreur si la requête a échoué
        return {"error": f"Failed to fetch data for {coin}. Status code: {response.status_code}"}        

import plotly.express as px
import plotly.graph_objects as go
def main():
    st.title("Cryptocurrency Trading Signals")

    coin_list = ["bitcoin", "cardano", "ethereum", "algorand", "solana"]
    nb_years_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    selected_coin = st.sidebar.selectbox("Select a cryptocurrency", coin_list)
    nb_years = st.sidebar.selectbox("Select a duration in years", nb_years_list, index=4)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=nb_years * 365)  # Two years ago

    log = st.sidebar.checkbox("Display Log scale", value=True)  # Case à cocher (checkbox)

    df = cached_fetch_weekly_coin_prices(selected_coin, start_date, end_date)

    if df is not None:
        st.write("Trading Signals:")
        df = trading_signals(df)

        fig = px.line(df, x=df.index, y='price', labels={'x': 'Date', 'price': 'Prix en USD'},
                      title='Signaux de Trading du ' + selected_coin)

        # Ajouter les points d'achat et de vente
        fig.add_scatter(x=df[df['Buy']].index, y=df[df['Buy']]['price'], mode='markers', 
                        marker=dict(color='green', symbol='triangle-up', size=10),
                        name='Achat')

        fig.add_scatter(x=df[df['Sell']].index, y=df[df['Sell']]['price'], mode='markers', 
                        marker=dict(color='red', symbol='triangle-down', size=10),
                        name='Vente')

        # Ajouter les bandes de Bollinger
        fig.add_trace(go.Scatter(x=df.index, y=df['upper_band'], mode='lines', line=dict(color='blue', width=1),
                                 name='Bande Supérieure Bollinger'))
        
        fig.add_trace(go.Scatter(x=df.index, y=df['lower_band'], mode='lines', line=dict(color='orange', width=1),
                                 name='Bande Inférieure Bollinger'))

        # Affichage en échelle logarithmique
        if log:
            fig.update_yaxes(type="log")

        # Augmenter la taille du graphique
        fig.update_layout(height=800, width=1200)

        st.plotly_chart(fig)  # Afficher le graphique dans l'application Streamlit
    else:
        st.write("Failed to fetch data.")


        # Nouvelle récupération des informations pour le coin sélectionné
    selected_coin_info = fetch_latest_coin_info(selected_coin)

    # Vérifie si les données ont été récupérées avec succès
    if 'error' not in selected_coin_info:
        # Affiche les données dans un tableau Streamlit
        st.write("Latest Coin Information:")
        st.table(selected_coin_info)
    else:
        # En cas d'erreur, l'affiche
        st.error(selected_coin_info['error'])




if __name__ == "__main__":
    main()