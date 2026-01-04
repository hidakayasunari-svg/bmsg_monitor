import google.generativeai as genai
import os
import json
import logging
import time
import warnings

# Suppress the FutureWarning from google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("RiskAnalyzer initialized with Gemini Pro")
        else:
            logger.warning("GEMINI_API_KEY not found. Analysis will be skipped.")
            self.model = None

    def analyze_tweet(self, tweet_text, user_info=None):
        """
        Analyze a tweet for risk, sentiment, and aggression.
        Returns a JSON object with scores.
        """
        if not self.model:
            return None

        username = user_info.get('username', 'unknown') if user_info else 'unknown'
        followers = user_info.get('followers', 0) if user_info else 0

        prompt = f"""
        Analyze the following social media post for reputation risk to the artist/agency (BMSG).
        
        Post by: @{username} (Followers: {followers})
        Content: "{tweet_text}"
        
        Evaluate on these scales (0-10):
        1. Sentiment Score (-1.0 to 1.0, where -1 is negative)
        2. Aggression Level (0-10)
        3. Spread Risk (0-10)
        4. Legal Risk (0-10)
        5. Overall Risk Score (0-10)

        IMPORTANT: Provide the 'reason' in JAPANESE.

        Return ONLY a raw JSON string like this (no code blocks):
        {{
            "sentiment": 0.0,
            "aggression": 0,
            "spread_risk": 0,
            "legal_risk": 0,
            "risk_score": 0,
            "reason": "description"
        }}
        """

        try:
            # Rate limiting handling (simple sleep)
            time.sleep(1.0) 
            
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Clean up code blocks if present
            if text_response.startswith("```json"):
                text_response = text_response[7:-3]
            elif text_response.startswith("```"):
                text_response = text_response[3:-3]
                
            result = json.loads(text_response)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return None
