import feedparser
from ..integrations.google_sheets import add_new_topic

def get_google_news_trends(region='KR'):
    """
    Fetches trending news from Google News RSS.
    This is much more stable than Google Trends scrapers.
    """
    # Google News RSS for South Korea (KR)
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    print(f"Fetching trending news from {rss_url}...")
    
    try:
        feed = feedparser.parse(rss_url)
        trends = []
        
        if not feed.entries:
            print("No entries found in the News RSS feed.")
            return []
            
        for entry in feed.entries:
            # We take the title as the topic
            title = entry.title
            # Often titles have " - Publisher" at the end, let's clean it slightly
            clean_title = title.split(' - ')[0]
            trends.append({"topic": clean_title})
            
        return trends
    except Exception as e:
        print(f"Error fetching news trends: {e}")
        return []

def analyze_and_store_trends(region='KR', limit=5):
    """
    Fetches news trends and stores them into Google Sheets.
    """
    trends = get_google_news_trends(region)
    
    if not trends:
        print("No news trends found.")
        return []
        
    print(f"Found {len(trends)} trending news topics.")
    
    added_topics = []
    count = 0
    for item in trends:
        if count >= limit:
            break
            
        topic = item['topic']
        success = add_new_topic(topic)
        if success:
            added_topics.append(topic)
            count += 1
            
    return added_topics

if __name__ == "__main__":
    # Test execution
    analyze_and_store_trends()
