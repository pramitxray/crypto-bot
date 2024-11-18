import streamlit as st
from plot import line_chart
from trader import make_trading_decision,fetch_ohlc_data
from sentiment_analysis import fetch_google_trends_data, analyze_trends_sentiment
from technical_indicators import (
    calculate_moving_average,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_fibonacci_retracements,
    calculate_rsi,
    calculate_atr,
    calculate_obv,
    calculate_stochastic_oscillator,
)
import pandas as pd
import matplotlib.pyplot as plt
import logging as lg

lg.basicConfig(level=lg.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Streamlit app
st.title("Cryptocurrency Prediction Analysis")

# Input section
crypto_symbol = st.text_input("Enter the cryptocurrency ticker:")

if st.button("Analyze"):
    st.header(f"Analysis for {crypto_symbol.capitalize()}")

    stock_df = fetch_ohlc_data(crypto_symbol=crypto_symbol, days=30)
    if stock_df is not None:
        filtered_stock_df = stock_df[["Date", "Open", "High", "Low", "Close"]]
        st.subheader("OHLC Data Table")
        st.write(filtered_stock_df.tail(5))
    else:
        st.error(f"Failed to fetch OHLC data for {crypto_symbol}. Please check the symbol or try again later.")
        st.stop()  # Stop further execution if OHLC data is not available

    # Fetch OHLC data and plot
    st.subheader("OHLC Graph")
    ohlc_data = fetch_ohlc_data(crypto_symbol)
    if ohlc_data is not None:
        fig = line_chart(ohlc_data, crypto_symbol.capitalize())
        st.plotly_chart(fig)
    else:
        st.error("Failed to fetch OHLC data.")
    
    st.subheader("Moving Averages")
    moving_averages_df = calculate_moving_average(stock_df, period=50)
    st.table(moving_averages_df.tail(5))

    # Technical indicators table
    st.subheader("Technical Indicators")
    if ohlc_data is not None:
        try:
            # Calculate all 8 technical indicators
            macd_signal = calculate_macd(ohlc_data)
            upper_band, lower_band = calculate_bollinger_bands(ohlc_data)
            fibonacci_levels = calculate_fibonacci_retracements(ohlc_data)
            rsi = calculate_rsi(ohlc_data)
            atr = calculate_atr(ohlc_data)
            obv = calculate_obv(ohlc_data)
            stochastic_oscillator = calculate_stochastic_oscillator(ohlc_data)

            # Create a dictionary for all indicators
            indicators = {
                "MACD Signal": macd_signal,
                "Upper Bollinger Band": upper_band.iloc[-1],
                "Lower Bollinger Band": lower_band.iloc[-1],
                "RSI": rsi,
                "ATR": atr,
                "OBV": obv,
                "Stochastic Oscillator": stochastic_oscillator,
                "Fibonacci Level (61.8%)": fibonacci_levels["61.8%"],
                "Fibonacci Level (38.2%)": fibonacci_levels["38.2%"],
            }

            # Display the indicators in a table
            st.table(pd.DataFrame(indicators.items(), columns=["Indicator", "Value"]))
        except Exception as e:
            st.error(f"Failed to calculate technical indicators: {str(e)}")
    else:
        st.error("Failed to calculate technical indicators.")

    # Fetch and display sentiment score
    st.subheader("Sentiment Analysis")
    news_data = fetch_google_trends_data(crypto_symbol)
    if news_data is not None:
        # Calculate sentiment score
        sentiment_score = analyze_trends_sentiment(news_data, crypto_symbol)

        # Display the overall sentiment score
        st.write(f"**Sentiment Score for {crypto_symbol.capitalize()}:** {sentiment_score:.4f}")
    else:
        st.error("No news articles available for sentiment analysis.")

    st.subheader("Trading Decision")
    decision = make_trading_decision(crypto_symbol)
    st.success(decision)
