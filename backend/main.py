import time
import schedule
import logging
import argparse
from dotenv import load_dotenv
import os

from collector import TwitterCollector
from database import SupabaseHandler
from analysis import RiskAnalyzer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize modules
collector = TwitterCollector()
db = SupabaseHandler()
analyzer = RiskAnalyzer()

KEYWORDS = os.getenv("MONITOR_KEYWORDS", "BMSG,SKY-HI").split(",")

def job_monitor_keywords():
    logger.info("Starting keyword monitor job")
    db.log_message("Starting keyword monitor job")
    
    for keyword in KEYWORDS:
        logger.info(f"Searching for: {keyword}")
        db.log_message(f"Searching for: {keyword}")
        
        try:
            tweets = collector.search_tweets(keyword, number=20)
            logger.info(f"Found {len(tweets)} tweets for '{keyword}'")
            db.log_message(f"Found {len(tweets)} tweets for '{keyword}'")
            
            for tweet in tweets:
                # 1. Analyse
                risk_result = analyzer.analyze_tweet(tweet['text'], tweet['user'])
                if risk_result:
                    tweet['risk_analysis'] = risk_result
                    tweet['risk_score'] = risk_result.get('risk_score', 0)
                
                # 2. Save
                saved = db.save_tweet(tweet)
                if saved:
                    logger.info(f"Saved tweet: {tweet['id']}")
                else:
                    logger.info(f"Processed tweet (Dry Run): {tweet['id']}")
        except Exception as e:
            error_msg = f"Error processing keyword '{keyword}': {str(e)}"
            logger.error(error_msg)
            db.log_message(error_msg, "ERROR")
    
    db.log_message("Keyword monitor job completed")

def run_once():
    """Run the monitoring job once and exit."""
    logger.info("Running in ONE-SHOT mode")
    db.log_message("Running in ONE-SHOT mode")
    job_monitor_keywords()
    logger.info("ONE-SHOT execution completed")
    db.log_message("ONE-SHOT execution completed")

def run_scheduler():
    # Schedule jobs
    schedule.every(30).minutes.do(job_monitor_keywords)
    
    msg = "Backend Scheduler STARTED. Listening for commands..."
    logger.info(msg)
    db.log_message(msg)
    
    # Run once at startup
    job_monitor_keywords()
    
    while True:
        # 1. Check for manual trigger commands
        commands = db.check_pending_commands()
        for cmd in commands:
            cmd_id = cmd['id']
            command_type = cmd['command']
            
            logger.info(f"Received command: {command_type} (ID: {cmd_id})")
            db.log_message(f"Received command: {command_type}")
            
            # Update to PROCESSING
            db.update_command_status(cmd_id, "PROCESSING")
            
            if command_type == "RUN_NOW":
                try:
                    job_monitor_keywords()
                    db.update_command_status(cmd_id, "COMPLETED")
                    db.log_message("Manual run completed successfully.")
                except Exception as e:
                    logger.error(f"Command execution failed: {e}")
                    db.update_command_status(cmd_id, "FAILED")
                    db.log_message(f"Manual run failed: {str(e)}", "ERROR")
        
        # 2. Run scheduled jobs
        schedule.run_pending()
        time.sleep(2) # Poll every 2 seconds

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BMSG SNS Monitor')
    parser.add_argument('--once', action='store_true', 
                        help='Run once and exit (no continuous monitoring)')
    args = parser.parse_args()
    
    if args.once:
        run_once()
    else:
        run_scheduler()
