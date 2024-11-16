import requests
import pandas as pd
from datetime import datetime
import logging as lg
from technical_indicators import calculate_moving_average, calculate_macd, calculate_bollinger_bands  # Technical indicators
from sentiment_analysis import fetch_and_analyze_trends  # Google Trends sentiment analysis
from plot import plot_ohlc
import json

# Setup logger
lg.basicConfig(level=lg.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# CoinGecko API base URL
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"

# Weightages for each factor
WEIGHTAGES = {
    'sentiment': 0.15,
    'technical_indicators': 0.25,
    'trading_volume': 0.10,
    'ohlc': 0.15,
    'market_cap_dominance': 0.10,
    'correlation_matrix': 0.05,
    'hash_rate': 0.05,
    'transaction_volume': 0.10,
    'burn_mechanisms': 0.05
}

# Function to fetch OHLC data from CoinGecko
def fetch_ohlc_data(crypto_symbol, vs_currency="usd", days=30):
    url = f"{COINGECKO_API_BASE}/coins/{crypto_symbol}/ohlc?vs_currency={vs_currency}&days={days}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    else:
        lg.error(f"Failed to fetch OHLC data: {response.status_code}")
        return None

# Function to fetch market cap and trading volume data from CoinGecko
def fetch_market_data(crypto_symbol, vs_currency="usd"):
    url = f"{COINGECKO_API_BASE}/coins/markets?vs_currency={vs_currency}&ids={crypto_symbol}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()[0]
        return {
            'market_cap': data['market_cap'],
            'trading_volume': data['total_volume'],
        }
    else:
        lg.error(f"Failed to fetch market data: {response.status_code}")
        return None

# Main function to handle the trading decision logic
def get_crypto_symbol():
    """
    Prompt the user to enter the cryptocurrency symbol (e.g., 'bitcoin', 'ethereum').
    :return: The cryptocurrency symbol.
    """
    crypto_symbol = input("Enter the cryptocurrency ticker (e.g., 'bitcoin', 'ethereum'): ").lower()
    return crypto_symbol

def make_trading_decision(crypto_symbol):
    # Fetch data
    ohlc_data = fetch_ohlc_data(crypto_symbol)
    market_data = fetch_market_data(crypto_symbol)
    sentiment_score = fetch_and_analyze_trends(crypto_symbol)  # Using Google Trends for sentiment

    if ohlc_data is None or market_data is None or sentiment_score is None:
        lg.error("Failed to retrieve necessary data for decision making.")
        return

    # Calculate technical indicators
    moving_average = calculate_moving_average(ohlc_data, period=50)
    macd_signal = calculate_macd(ohlc_data)
    bollinger_bands = calculate_bollinger_bands(ohlc_data)

    # Apply weightages to each factor
    technical_indicators_score = 0
    if macd_signal == "bullish":
        technical_indicators_score = 1
    elif macd_signal == "bearish":
        technical_indicators_score = -1

    # Trading volume and OHLC score
    volume_score = 1 if market_data['trading_volume'] > moving_average else -1
    ohlc_score = 1 if ohlc_data['Close'].iloc[-1] > ohlc_data['Open'].iloc[-1] else -1

    # Display individual scores
    print(f"Sentiment Score (Google Trends): {sentiment_score}")
    print(f"Technical Indicators Score (MACD): {technical_indicators_score}")
    print(f"Volume Score: {volume_score}")
    print(f"OHLC Score: {ohlc_score}")
    print(f"Market Cap: {market_data['market_cap']}")

    # Combine all weighted scores
    overall_score = (
        WEIGHTAGES['sentiment'] * sentiment_score +
        WEIGHTAGES['technical_indicators'] * technical_indicators_score +
        WEIGHTAGES['trading_volume'] * volume_score +
        WEIGHTAGES['ohlc'] * ohlc_score +
        WEIGHTAGES['market_cap_dominance'] * market_data['market_cap'] / 1e9  # Scaled down for easier scoring
    )

    # Display overall score
    print(f"Overall Score for {crypto_symbol}: {overall_score}")

    # Decision based on overall score
    if overall_score >= 30:
        lg.info(f"BUY signal for {crypto_symbol}.")
        print(f"BUY {crypto_symbol}")
    else:
        lg.info(f"NO BUY signal for {crypto_symbol}.")
        print(f"NO BUY for {crypto_symbol}")
        
    plot_ohlc(crypto_symbol)

if __name__ == "__main__":
    # Prompt the user for a cryptocurrency symbol
    crypto_symbol = get_crypto_symbol()
    make_trading_decision(crypto_symbol)
