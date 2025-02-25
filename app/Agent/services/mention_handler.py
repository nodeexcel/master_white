import tweepy
from app.config import Config
from app.Agent.utils.twitter_utils import create_x_client
from app.Agent.utils.queue_handler import MessageQueue
from app.database import mongo_client
import logging
from datetime import datetime, timedelta
import time
import pytz

logger = logging.getLogger(__name__)

class MentionSearchHandler:
    def __init__(self):
        self.client = create_x_client(Config)
        self.message_queue = None
        self.conversation_collection = mongo_client.db['conversations']
        self.last_check_time = datetime.now(pytz.UTC) - timedelta(minutes=30)  # Look back 5 minutes on startup
        self.processed_tweets = set()
        
    def ensure_queue(self):
        if not self.message_queue:
            self.message_queue = MessageQueue()
        
    def process_mentions(self):
        try:
            logger.info(f"Checking for mentions since {self.last_check_time}")
            self.ensure_queue()
            
            start_time = self.last_check_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            print(start_time,"start_time")
            # Get mentions since last check
            mentions = tweepy.Paginator(
                self.client.get_users_mentions,
                id=Config.X_USER_ID,
                tweet_fields=['created_at', 'text', 'in_reply_to_user_id'],
                expansions=['author_id'],
                start_time=start_time,
                max_results=100
            ).flatten(limit=100)
            
            mentions = list(mentions)  # Convert iterator to list to handle rate limits
            logger.info(f"Retrieved {len(mentions)} mentions from Twitter API")
            
            mention_count = 0
            for mention in mentions:
                # # Skip if already processed in this session
                # if mention.id in self.processed_tweets:
                #     logger.info(f"Skipping already processed tweet {mention.id}")
                #     continue
                    
                # Skip if already in database
                # if self.conversation_collection.find_one({"tweet_id": mention.id}):
                #     logger.info(f"Skipping tweet {mention.id} - found in database")
                #     self.processed_tweets.add(mention.id)
                #     continue
                
                # Skip if it's a reply to our own tweet
                # if str(mention.in_reply_to_user_id) == str(Config.X_USER_ID):
                #     logger.info(f"Skipping tweet {mention.id} - reply to our tweet")
                #     self.processed_tweets.add(mention.id)
                #     continue
                
                logger.info(f"Processing new mention: {mention.id}")
                
                mention_data = {
                    "author_id": mention.author_id,
                    "tweet_id": mention.id,
                    "text": mention.text
                }
                
                try:
                    self.message_queue.publish_message(mention_data)
                    mention_count += 1
                    self.processed_tweets.add(mention.id)
                    logger.info(f"Successfully queued mention {mention.id}")
                except Exception as e:
                    logger.error(f"Failed to queue mention {mention.id}: {e}")
                    self.message_queue = None
            
            logger.info(f"Found {mention_count} new mentions")
            self.last_check_time = datetime.now(pytz.UTC)
            
            # Cleanup processed tweets set if it gets too large
            if len(self.processed_tweets) > 1000:
                logger.info("Cleaning up processed tweets cache")
                self.processed_tweets.clear()
                
        except Exception as e:
            logger.error(f"Error processing mentions: {e}")
            self.message_queue = None

def start_search_handler():
    handler = MentionSearchHandler()
    while True:
        try:
            handler.process_mentions()
            time.sleep(3600)  # Check every minute
        except Exception as e:
            logger.error(f"Error in search handler: {e}")
            time.sleep(15) 