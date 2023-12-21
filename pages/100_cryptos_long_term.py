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




# # Streamlit app
# def main():
#     st.title("Cryptocurrency Trading Signals")

#     coin_list = ["bitcoin", "cardano", "ethereum", "algorand", "solana"]
#     nb_years_list = [1,2,3,4,5,6,7,8,9,10]
#     selected_coin = st.sidebar.selectbox("Select a cryptocurrency", coin_list)
#     nb_years = st.sidebar.selectbox("Select a duration in years", nb_years_list, index=4)
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=nb_years*365)  # Two years ago

#     df = fetch_weekly_coin_prices(selected_coin, start_date, end_date)
#     if df is not None:
#         # st.write("Data:")
#         # st.write(df)

#         st.write("Trading Signals:")
#         df = trading_signals(df)

#         # Plotting the graph
#         plt.figure(figsize=(15, 7))

#         # Ajouter les points d'achat et de vente
#         plt.scatter(df[df['Buy']].index, df[df['Buy']]['price'], color='green', label='Achat (flèche vert)', marker='^', s=100)
#         plt.scatter(df[df['Sell']].index, df[df['Sell']]['price'], color='red', label='Vente (flèche rouge)', marker='v', s=100)
#         if log:
#             # Tracer le prix du Bitcoin en échelle logarithmique pour mieux visualiser les variations
#             plt.semilogy(df['price'], label='Prix du '+selected_coin)
#             # Afficher les autres indicateurs en échelle logarithmique également
#             plt.semilogy(df['SMA'], label='SMA', alpha=0.6, linestyle='--')
#             plt.semilogy(df['upper_band'], label='Bande Supérieure Bollinger', alpha=0.5, linestyle='--')
#             plt.semilogy(df['lower_band'], label='Bande Inférieure Bollinger', alpha=0.5, linestyle='--')
#         else:
#             # Tracer le prix du Bitcoin en échelle logarithmique pour mieux visualiser les variations
#             plt.plot(df['price'], label='Prix du '+selected_coin)
#             # Afficher les autres indicateurs en échelle logarithmique également
#             plt.plot(df['SMA'], label='SMA', alpha=0.6, linestyle='--')
#             plt.plot(df['upper_band'], label='Bande Supérieure Bollinger', alpha=0.5, linestyle='--')
#             plt.plot(df['lower_band'], label='Bande Inférieure Bollinger', alpha=0.5, linestyle='--')


#         # Ajouter les légendes et les titres
#         plt.title('Signaux de Trading du '+selected_coin)
#         plt.xlabel('Date')
#         plt.ylabel('Prix en USD')
#         plt.legend()

#         st.pyplot(plt)  # Show the plot in Streamlit app

#         # Optionally, you can save the DataFrame to a CSV file
#         # df.to_csv('bitcoins_trading_signals.csv')
#     else:
#         st.write("Failed to fetch data.")

# if __name__ == "__main__":
#     main()


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

if __name__ == "__main__":
    main()