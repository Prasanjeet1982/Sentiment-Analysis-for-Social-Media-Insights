import tweepy
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# Twitter API credentials (replace with your credentials)
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

def authenticate_twitter_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True)

def perform_sentiment_analysis(api, search_keyword):
    tweets = tweepy.Cursor(api.search, q=search_keyword, count=10, lang="en", tweet_mode="extended").items()
    sentiment_data = {'Tweet': [], 'Sentiment': [], 'Sentiment Score': []}

    for tweet in tweets:
        tweet_text = tweet.full_text
        analysis = TextBlob(tweet_text)
        sentiment_score = analysis.sentiment.polarity
        if sentiment_score > 0:
            sentiment = 'positive'
        elif sentiment_score < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        sentiment_data['Tweet'].append(tweet_text)
        sentiment_data['Sentiment'].append(sentiment)
        sentiment_data['Sentiment Score'].append(sentiment_score)

    df = pd.DataFrame(sentiment_data)
    return df

def visualize_sentiment_distribution(df, plot_filename):
    sentiment_counts = df['Sentiment'].value_counts()
    sentiment_plot = sentiment_counts.plot(kind='bar', color=['green', 'blue', 'red'])
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis for Social Media Insights')
    plt.xticks(rotation=0)
    sentiment_plot.figure.savefig(plot_filename)
    plt.close(sentiment_plot.figure)

@app.post("/analyze")
async def analyze_tweets(request: Request, keyword: str = Form(...)):
    api = authenticate_twitter_api()
    sentiment_df = perform_sentiment_analysis(api, keyword)
    
    plot_filename = 'sentiment_plot.png'
    visualize_sentiment_distribution(sentiment_df, plot_filename)
    
    response_content = f"""
    <html>
        <body>
            <h1>Sentiment Analysis Results</h1>
            <p>Keyword: {keyword}</p>
            <p>Positive Tweets: {sentiment_df['Sentiment'].value_counts()['positive']}</p>
            <p>Negative Tweets: {sentiment_df['Sentiment'].value_counts()['negative']}</p>
            <p>Neutral Tweets: {sentiment_df['Sentiment'].value_counts()['neutral']}</p>
            <img src="{plot_filename}" alt="Sentiment Plot">
        </body>
    </html>
    """

    return HTMLResponse(content=response_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
