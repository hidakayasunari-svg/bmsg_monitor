import os
from supabase import create_client, Client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseHandler:
    def __init__(self, url=None, key=None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not found in env. Database operations will be skipped.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.url, self.key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None

    def save_tweet(self, tweet_data):
        """
        Save a single tweet to the database.
        upsert is used to prevent duplicates (requires 'id' to be unique constraint).
        """
        if not self.client:
            logger.debug("Skipping save (no DB client)")
            return None
            
        try:
            # Prepare data for insertion (match schema)
            # Assuming table 'tweets' exists with columns matching keys
            data, count = self.client.table("tweets").upsert(tweet_data).execute()
            return data
        except Exception as e:
            logger.error(f"Error saving tweet {tweet_data.get('id')}: {e}")
            return None

    def get_latest_tweets(self, limit=10):
        if not self.client: return []
        try:
            response = self.client.table("tweets").select("*").order("collected_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []

    def log_message(self, message: str, level: str = "INFO"):
        """Write a log message to the system_logs table."""
        if not self.client: return
        try:
            timestamp = datetime.now().astimezone().isoformat()
            data = {"message": message, "level": level, "created_at": timestamp}
            self.client.table("system_logs").insert(data).execute()
        except Exception as e:
            # Fallback to logger if DB fails
            logger.error(f"Failed to log message to DB: {e}")

    def check_pending_commands(self):
        """Check for pending commands in system_commands table."""
        if not self.client: return []
        try:
            response = self.client.table("system_commands")\
                .select("*")\
                .eq("status", "PENDING")\
                .order("created_at", desc=False)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to check commands: {e}")
            return []

    def update_command_status(self, command_id: int, status: str):
        """Update the status of a command."""
        if not self.client: return
        try:
            now = datetime.now().astimezone().isoformat()
            self.client.table("system_commands")\
                .update({"status": status, "processed_at": now})\
                .eq("id", command_id)\
                .execute()
        except Exception as e:
            logger.error(f"Failed to update command status: {e}")

