import sys
import os
import logging

from dotenv import load_dotenv

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load env from the same directory as this script
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY")

def test_components():
    logger.info("--> Testing imports...")
    try:
        from collector import TwitterCollector
        from database import SupabaseHandler
        from analysis import RiskAnalyzer
        logger.info("✅ Imports successful.")
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return

    logger.info("--> Initializing components (Dry Run)...")
    try:
        c = TwitterCollector()
        d = SupabaseHandler() # Will warn if no keys
        a = RiskAnalyzer()    # Will warn if no keys
        logger.info("✅ Initialization successful.")
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return
        
    logger.info("--> Testing Collector (Query: BMSG)...")
    try:
        # Limit to 3 tweets for quick test
        tweets = c.search_tweets("BMSG", number=3)
        logger.info(f"✅ Collector check finished. Found {len(tweets)} tweets.")
        if tweets:
            t = tweets[0]
            logger.info(f"   Sample: {t.get('text')[:30]}...")
    except Exception as e:
        logger.error(f"❌ Collector check failed: {e}")

if __name__ == "__main__":
    test_components()
