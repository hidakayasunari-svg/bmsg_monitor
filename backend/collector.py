from ntscraper import Nitter
import logging
import time
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterCollector:
    def __init__(self, instance=None):
        """
        Initialize the collector.
        """
        self.scraper = Nitter(log_level=1)
        self.preferred_instance = instance
        logger.info("TwitterCollector initialized")

    def search_tweets(self, query, mode='term', number=50, since=None, until=None):
        """
        Search for tweets using Nitter with retry logic and fallback instances.
        """
        # List of potentially stable instances to try if random fails
        fallback_instances = [
            None, # Try random first
            "https://nitter.privacydev.net",
            "https://nitter.poast.org",
            "https://nitter.lucabased.xyz",
            "https://nitter.net",
        ]

        for instance in fallback_instances:
            try:
                # Add a small random delay to be polite
                time.sleep(random.uniform(1.0, 3.0))
                
                instance_name = instance if instance else "Random"
                logger.info(f"Searching for '{query}' on {instance_name} (Mode: {mode})")
                
                results = self.scraper.get_tweets(
                    query, 
                    mode=mode, 
                    number=number, 
                    since=since, 
                    until=until, 
                    instance=instance
                )
                
                if 'tweets' in results and len(results['tweets']) > 0:
                    tweets = results['tweets']
                    logger.info(f"Found {len(tweets)} tweets on {instance_name}")
                    return self._process_tweets(tweets)
                else:
                    logger.warning(f"No results or empty list on {instance_name}. Retrying next...")
            
            except Exception as e:
                logger.warning(f"Error scraping on {instance_name}: {e}")
                continue
        
        logger.error(f"All instances failed for query: {query}")
        return []

    def _process_tweets(self, raw_tweets):
        """Clean and structure the raw tweet data."""
        processed = []
        for t in raw_tweets:
            try:
                processed.append({
                    'id': t.get('link', '').split('/')[-1] if 'link' in t else None,
                    'url': t.get('link'),
                    'text': t.get('text'),
                    'date': t.get('date'),
                    'user_info': {
                        'username': t.get('user', {}).get('username'),
                        'display_name': t.get('user', {}).get('name'),
                        'profile_img': t.get('user', {}).get('avatar'),
                    },
                    'stats': {
                        'comments': t.get('stats', {}).get('comments'),
                        'retweets': t.get('stats', {}).get('retweets'),
                        'quotes': t.get('stats', {}).get('quotes'),
                        'likes': t.get('stats', {}).get('likes'),
                    },
                    # 'is_retweet': t.get('is-retweet', False), # Rejected by schema
                    'collected_at': datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"Error processing tweet: {e}")
                continue
        return processed

if __name__ == "__main__":
    # Simple test
    collector = TwitterCollector()
    tweets = collector.search_tweets("BMSG", number=5)
    for tweet in tweets:
        print(f"[{tweet['date']}] @{tweet['user']['username']}: {tweet['text'][:50]}... (RT: {tweet['stats']['retweets']})")
