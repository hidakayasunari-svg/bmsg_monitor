import logging
import os
from dotenv import load_dotenv
from database import SupabaseHandler

# Load env variables
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEBUG")

def check_data():
    logger.info("--> Checking data in Supabase...")
    db = SupabaseHandler()
    
    if not db.client:
        logger.error("❌ No client.")
        return

    try:
        # Try to select data
        response = db.client.table("tweets").select("*").execute()
        data = response.data
        
        logger.info(f"✅ Query successful.")
        logger.info(f"📊 Row count: {len(data)}")
        
        if len(data) > 0:
            logger.info(f"   First tweet ID: {data[0].get('id')}")
            logger.info(f"   First tweet Text: {data[0].get('text')}")
        else:
            logger.warning("⚠️ Table appears empty to this client.")
            
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")

if __name__ == "__main__":
    check_data()
