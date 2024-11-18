from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError, TooManyRequestsError
import logging as lg
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import time

# Download VADER lexicon if you haven't already
nltk.download('vader_lexicon')

# Setup logger
lg.basicConfig(level=lg.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Initialize Google Trends (pytrends)
pytrends = TrendReq(hl='en-US', tz=360)

def fetch_google_trends_data(crypto_symbol, timeframe='now 7-d'):
    kw_list = [crypto_symbol]
    
    lg.info(f"Building payload for keyword: {kw_list}")
    
    try:
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo='', gprop='')
        trends_data = pytrends.interest_over_time()
        
        if not trends_data.empty:
            trends_data = trends_data.tail(50)  # Get the last 50 data points
            trends_data.reset_index(inplace=True)  # Reset index to get 'date' column
            trends_data.rename(columns={'date': 'datetime'}, inplace=True)  # Rename index column to datetime
            lg.info(f"Fetched Google Trends data for {crypto_symbol}.")
            return trends_data
        else:
            lg.error(f"No data available for {crypto_symbol}.")
            return None
    except ResponseError as e:
        lg.error(f"Response Error: {e.response.content.decode('utf-8')}")
        return None
    except TooManyRequestsError:
        lg.warning("Too many requests to Google Trends. Retrying after 60 seconds...")
        time.sleep(60)
        return fetch_google_trends_data(crypto_symbol, timeframe)
    finally:
        time.sleep(0.5)




def analyze_trends_sentiment(trends_data, crypto_symbol):
    overall_sentiment = 0
    total_data_points = len(trends_data)

    if total_data_points == 0:
        lg.warning("No data points to analyze sentiment.")
        return 0

    previous_interest_level = None

    for index, row in trends_data.iterrows():
        interest_level = row[crypto_symbol]
        
        # Create unique text based on changes in interest level
        if previous_interest_level is None:
            previous_interest_level = interest_level

        if interest_level > previous_interest_level:
            text = f"The interest in {crypto_symbol} has increased to {interest_level}."
        elif interest_level < previous_interest_level:
            text = f"The interest in {crypto_symbol} has decreased to {interest_level}."
        else:
            text = f"The interest in {crypto_symbol} remains steady at {interest_level}."

        sentiment_score = analyzer.polarity_scores(text)
        lg.info(f"Text: {text} | Sentiment: {sentiment_score}")

        overall_sentiment += sentiment_score['compound']
        previous_interest_level = interest_level  # Update for next iteration

    return overall_sentiment / total_data_points



def fetch_and_analyze_trends(crypto_symbol):
    trends_data = fetch_google_trends_data(crypto_symbol)
    
    if trends_data is not None:
        sentiment_score = analyze_trends_sentiment(trends_data, crypto_symbol)
        lg.info(f"Overall Sentiment Score for {crypto_symbol} (Google Trends): {sentiment_score}")
        return sentiment_score
    else:
        lg.info(f"No trends data found for {crypto_symbol}.")
        return 0
