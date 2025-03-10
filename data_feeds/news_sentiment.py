import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
from logs.logger import log_message
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ✅ Initialize Chrome Driver
def get_chrome_driver():
    return uc.Chrome(version_main=133)

# ✅ Fetch News for All Pairs in config.json
def fetch_news_sentiment():
    with open("config.json", "r") as file:
        config = json.load(file)

    sentiment_results = {}
    for symbol in config["trading_pairs"]:
        news_list = fetch_yahoo_news(symbol) or fetch_forexfactory_news()
        sentiment_score = analyze_sentiment(news_list)
        sentiment_results[symbol] = sentiment_score

    return sentiment_results

# ✅ Yahoo Finance News Scraper
def fetch_yahoo_news(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        return [news.text.strip() for news in soup.find_all("h3")]
    
    except Exception:
        return None

# ✅ ForexFactory Scraper (Fallback)
def fetch_forexfactory_news():
    driver = get_chrome_driver()
    driver.get("https://www.forexfactory.com/news")
    time.sleep(10)

    try:
        news_list = [news.text.strip() for news in driver.find_elements(By.CSS_SELECTOR, "div.news-title a")]
        driver.quit()
        return news_list

    except Exception:
        driver.quit()
        return None

# ✅ Sentiment Analysis
def analyze_sentiment(news_list):
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(news)["compound"] for news in news_list]
    return round(sum(scores) / len(scores), 2) if scores else 0

if __name__ == "__main__":
    print(fetch_news_sentiment())
