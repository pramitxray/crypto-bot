import requests
import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch OHLC data from CoinGecko
def fetch_ohlc_data(crypto_symbol, vs_currency="usd", days=365):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_symbol}/ohlc?vs_currency={vs_currency}&days={days}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('Date', inplace=True)
        return df
    else:
        print(f"Failed to fetch OHLC data: {response.status_code}")
        return None

# Function to plot OHLC data
def plot_ohlc(crypto_symbol):
    df = fetch_ohlc_data(crypto_symbol)

    if df is not None:
        plt.figure(figsize=(14, 7))
        plt.plot(df.index, df['Open'], label='Open', color='blue')
        plt.plot(df.index, df['High'], label='High', color='green')
        plt.plot(df.index, df['Low'], label='Low', color='red')
        plt.plot(df.index, df['Close'], label='Close', color='orange')
        
        plt.title(f'OHLC Data for {crypto_symbol.capitalize()} (Last 12 Months)')
        plt.xlabel('Date')
        plt.ylabel('Price (in USD)')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()