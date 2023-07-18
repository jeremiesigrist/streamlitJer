import streamlit as st
import requests
import pandas as pd
import json

# Set the title of the page
st.title("Cryptocurrency Market Tracker")

url = "https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
parameters = {
    "start": 1,
    "limit": 5000,
    "convert": "USD"
}

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"
}

response = requests.get(url, params=parameters, headers=headers)


# st.write(response)
data = json.loads(response.text)
# data = response.json()

# st.write(data)

# Create a Pandas DataFrame from the data
df = pd.DataFrame(data['data'])

st.write(df)

# Select the columns we want to display
df = df[["symbol", "name", "price_usd", "market_cap_usd"]]

# Sort the DataFrame by price
df = df.sort_values("price_usd", ascending=False)

# Display the DataFrame
st.dataframe(df)

# Plot the price of the top 10 cryptocurrencies
st.line_chart(df.head(10)[["price_usd"]])