import pandas as pd
import numpy as np
import json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def calculate_moving_average(df, period=50):
    """
    Calculates the moving average for the given period and returns it as a DataFrame.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for calculating the moving average (default: 50 days).
    :return: DataFrame with a new 'Moving Average' column.
    """
    if len(df) < period:
        moving_avg = df['Close'].rolling(window=len(df)).mean()
    else:
        moving_avg = df['Close'].rolling(window=period).mean()

    # Create a DataFrame with Moving Average
    result_df = pd.DataFrame({
        "Date": df["Date"],
        "Close": df["Close"],
        f"Moving Average ({period})": moving_avg
    })
    return result_df

def calculate_moving_averages(df, period=50):
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

def calculate_fibonacci_retracements(df, period=30):
    """
    Calculates Fibonacci retracement levels for a given period.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for calculating Fibonacci levels (default: 30 days).
    :return: A dictionary of Fibonacci levels.
    """
    if len(df) < period:
        raise ValueError("Not enough data to calculate Fibonacci retracements.")
    
    high = df['High'].iloc[-period:].max()
    low = df['Low'].iloc[-period:].min()
    levels = {
        '0.0%': high,
        '23.6%': high - (high - low) * 0.236,
        '38.2%': high - (high - low) * 0.382,
        '50.0%': high - (high - low) * 0.5,
        '61.8%': high - (high - low) * 0.618,
        '100.0%': low,
    }
    return levels

def calculate_rsi(df, period=14):
    """
    Calculates the Relative Strength Index (RSI) for the given period.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for RSI calculation (default: 14 days).
    :return: RSI value.
    """
    if len(df) < period:
        raise ValueError("Not enough data to calculate RSI.")
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_atr(df, period=14):
    """
    Calculates the Average True Range (ATR) for the given period.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for ATR calculation (default: 14 days).
    :return: ATR value.
    """
    if len(df) < period:
        raise ValueError("Not enough data to calculate ATR.")
    
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr.iloc[-1]

def calculate_obv(df):
    """
    Calculates the On-Balance Volume (OBV) indicator.
    
    :param df: DataFrame containing OHLC data with volume.
    :return: OBV value.
    """
    if 'Volume' not in df.columns or df['Volume'].isnull().all():
        print("Missing volume data; skipping OBV calculation.")  # Replace logging with print
        return 0  # Neutral score when volume data is unavailable

    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return obv[-1]


# def calculate_obv(df):
#     """
#     Calculates the On-Balance Volume (OBV) indicator.
    
#     :param df: DataFrame containing OHLC data with volume.
#     :return: OBV value.
#     """
#     if 'Volume' not in df.columns or df['Volume'].isnull().all():
#         lg.warning("Missing volume data; skipping OBV calculation.")
#         return 0  # Neutral score when volume data is unavailable

#     obv = [0]
#     for i in range(1, len(df)):
#         if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
#             obv.append(obv[-1] + df['Volume'].iloc[i])
#         elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
#             obv.append(obv[-1] - df['Volume'].iloc[i])
#         else:
#             obv.append(obv[-1])
#     return obv[-1]


def calculate_stochastic_oscillator(df, period=14):
    """
    Calculates the Stochastic Oscillator for a given period.
    
    :param df: DataFrame containing OHLC data.
    :param period: Period for Stochastic Oscillator calculation (default: 14 days).
    :return: Stochastic Oscillator value (percentage K).
    """
    if len(df) < period:
        raise ValueError("Not enough data to calculate Stochastic Oscillator.")
    
    high_max = df['High'].rolling(window=period).max()
    low_min = df['Low'].rolling(window=period).min()
    stochastic_oscillator = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    return stochastic_oscillator.iloc[-1]
