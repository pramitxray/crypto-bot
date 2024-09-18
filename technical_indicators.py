import pandas as pd
import json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def calculate_moving_average(df, period=50):
    """
    Calculates the moving average for the given period.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for calculating the moving average (default: 50 days).
    :return: Latest moving average value.
    """
    if len(df) < period:
        return df['Close'].rolling(window=len(df)).mean().iloc[-1]
    return df['Close'].rolling(window=period).mean().iloc[-1]

def calculate_macd(df):
    """
    Calculates the MACD (Moving Average Convergence Divergence).
    
    :param df: DataFrame containing OHLC data.
    :return: "bullish" or "bearish" signal.
    """
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()

    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        return "bullish"
    elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
        return "bearish"
    return "neutral"

def calculate_bollinger_bands(df, period=20):
    """
    Calculates the Bollinger Bands.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for calculating the Bollinger Bands (default: 20 days).
    :return: Upper and lower Bollinger Bands.
    """
    mid_band = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    upper_band = mid_band + (std * 2)
    lower_band = mid_band - (std * 2)

    return upper_band, lower_band
