import requests
import pandas as pd
from datetime import datetime
import logging as lg
from technical_indicators import (
    calculate_moving_average,
    calculate_moving_averages,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_fibonacci_retracements,
    calculate_rsi,
    calculate_atr,
    calculate_obv,
    calculate_stochastic_oscillator
)
from sentiment_analysis import fetch_and_analyze_trends  # Google Trends sentiment analysis
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

def fetch_ohlc_data(crypto_symbol, vs_currency="usd", days=30):
    url = f"{COINGECKO_API_BASE}/coins/{crypto_symbol}/ohlc?vs_currency={vs_currency}&days={days}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Attempt to fetch volume data
        market_data = fetch_market_data(crypto_symbol)
        if market_data and 'trading_volume' in market_data:
            df['Volume'] = market_data['trading_volume']
        else:
            df['Volume'] = None  # Placeholder if volume is unavailable

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
    crypto_symbol = input("Enter the cryptocurrency ticker: ").lower()
    return crypto_symbol

def make_trading_decision(crypto_symbol):
    # Fetch data
    ohlc_data = fetch_ohlc_data(crypto_symbol)
    market_data = fetch_market_data(crypto_symbol)
    sentiment_score = fetch_and_analyze_trends(crypto_symbol)  # Using Google Trends for sentiment

    # if ohlc_data is None or market_data is None or sentiment_score is None:
    #     lg.error("Failed to retrieve necessary data for decision making.")
    #     return

    # Calculate technical indicators
    macd_signal = calculate_macd(ohlc_data)
    bollinger_bands = calculate_bollinger_bands(ohlc_data)
    fibonacci_levels = calculate_fibonacci_retracements(ohlc_data)
    rsi = calculate_rsi(ohlc_data)
    atr = calculate_atr(ohlc_data)
    obv = calculate_obv(ohlc_data)
    stochastic_oscillator = calculate_stochastic_oscillator(ohlc_data)

    # Apply weightages to technical indicators
    technical_indicators_score = 0

    # MACD
    if macd_signal == "bullish":
        technical_indicators_score += 1
    elif macd_signal == "bearish":
        technical_indicators_score -= 1

    # RSI
    if rsi < 30:  # Oversold
        technical_indicators_score += 1
    elif rsi > 70:  # Overbought
        technical_indicators_score -= 1

    # Stochastic Oscillator
    if stochastic_oscillator < 20:  # Oversold
        technical_indicators_score += 1
    elif stochastic_oscillator > 80:  # Overbought
        technical_indicators_score -= 1

    # Bollinger Bands
    if ohlc_data['Close'].iloc[-1] > bollinger_bands[0].iloc[-1]:  # Above upper band (overbought)
        technical_indicators_score -= 1
    elif ohlc_data['Close'].iloc[-1] < bollinger_bands[1].iloc[-1]:  # Below lower band (oversold)
        technical_indicators_score += 1

    # Fibonacci Retracements
    if ohlc_data['Close'].iloc[-1] > fibonacci_levels['61.8%']:
        technical_indicators_score += 1
    elif ohlc_data['Close'].iloc[-1] < fibonacci_levels['38.2%']:
        technical_indicators_score -= 1

    # ATR (Volatility)
    average_atr = ohlc_data['Close'].rolling(window=14).mean().iloc[-1]
    if atr > average_atr:  # High volatility
        technical_indicators_score -= 1
    else:  # Low volatility
        technical_indicators_score += 1

    # OBV (Momentum)
    if obv > 0:
        technical_indicators_score += 1
    else:
        technical_indicators_score -= 1

    moving_average = calculate_moving_averages(ohlc_data, period=50)

    if market_data and 'trading_volume' in market_data:
        volume_score = 1 if market_data['trading_volume'] > moving_average else -1
    else:
        volume_score = 0
        
    ohlc_score = 1 if ohlc_data['Close'].iloc[-1] > ohlc_data['Open'].iloc[-1] else -1

    # Display individual scores
    print(f"Sentiment Score (Google Trends): {sentiment_score}")
    technical_indicators_score = max(technical_indicators_score, 0)
    print(f"Technical Indicators Score: {technical_indicators_score}")
    print(f"OHLC Score: {ohlc_score}")
    

    # Combine all weighted scores
    overall_score = (
        WEIGHTAGES['sentiment'] * sentiment_score +
        WEIGHTAGES['technical_indicators'] * technical_indicators_score +
        WEIGHTAGES['trading_volume'] * volume_score +
        WEIGHTAGES['ohlc'] * ohlc_score 
        # ((WEIGHTAGES['market_cap_dominance'] * market_data['market_cap'] ) /1e9)
    )

    # Display overall score
    print(f"Overall Score for {crypto_symbol}: {overall_score}")

    # Decision based on overall score
    if overall_score >= 0.4:
        lg.info(f"BUY signal for {crypto_symbol}.")
        return "BUY"
    else:
        lg.info(f"NO BUY signal for {crypto_symbol}.")
        return "NO BUY"
        

if __name__ == "__main__":
    # Prompt the user for a cryptocurrency symbol
    crypto_symbol = get_crypto_symbol()
    make_trading_decision(crypto_symbol)
