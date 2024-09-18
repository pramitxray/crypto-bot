from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon if you haven't already
nltk.download('vader_lexicon')

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Sample test data
test_data = [
    "Bitcoin surges in popularity!",
    "Bitcoin is crashing!",
    "Bitcoin remains stable."
]

# Analyze sentiment for each text in the test data
for text in test_data:
    sentiment_score = analyzer.polarity_scores(text)
    print(f"Text: {text} | Sentiment: {sentiment_score}")
