import feedparser

RSS_FEED_URL = "https://news.itmo.ru/ru/rss/"

def get_latest_news(count: int = 3) -> list:
    feed = feedparser.parse(RSS_FEED_URL)
    sources = []
    for entry in feed.entries[:count]:
        sources.append(entry.link)
    return sources