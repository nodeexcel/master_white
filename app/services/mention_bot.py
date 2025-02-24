import tweepy
# from .config import Config
from app.config import Config
from app.utils.twitter_utils import (
    create_x_client,
    send_direct_message,
    reply_to_tweet
)
from app.utils.common_utils import create_openai_client, generate_response
from app.utils.queue_handler import MessageQueue
from app.utils.prompt_handler import is_dog_related
from app.database import mongo_client
import datetime
import logging
import json
from app.utils.rate_limiter import RateLimiter
import time

logger = logging.getLogger(__name__)

class MentionConsumer:
    def __init__(self):
        self.x_client = create_x_client(Config)
        self.openai_client = create_openai_client(Config)
        self.message_queue = MessageQueue()
        self.rate_limiter = RateLimiter(max_requests=5, time_window=240)
        self.conversation_collection = mongo_client.db['conversations']
    
    def process_mention(self, ch, method, properties, body):
        """Process mentions from the queue"""
        try:
            mention_data = json.loads(body)
            author_id = mention_data.get("author_id")
            tweet_id = mention_data.get("tweet_id")
            text = mention_data.get("text")
            
            # Check if we've already processed this mention
            existing_mention = self.conversation_collection.find_one({"tweet_id": tweet_id})
            if existing_mention is not None:
                logger.info(f"Mention {tweet_id} already processed")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            if not self.rate_limiter.can_proceed(author_id):
                logger.warning(f"Rate limit exceeded for user {author_id}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return
            
            # Generate and send the reply
            success, reply_text = reply_to_tweet(
                client=self.x_client,
                tweet_id=tweet_id,
                user_text=text,
                openai_client=self.openai_client
            )
            
            if success:
                self.conversation_collection.insert_one({
                    "user_id": author_id,
                    "tweet_id": tweet_id,
                    "query": text,
                    "response": reply_text,
                    "timestamp": datetime.datetime.now(),
                    "is_dog_related": is_dog_related(text),
                    "tweet_replied": success
                })
                logger.info(f"Successfully processed mention {tweet_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.error(f"Failed to process mention {tweet_id}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                
        except Exception as e:
            logger.error(f"Error processing mention from queue: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_mention_consumer():
    while True:
        try:
            consumer = MentionConsumer()
            logger.info("Starting message consumer...")
            consumer.message_queue.consume_messages(consumer.process_mention)
        except Exception as e:
            logger.error(f"Error in message consumer: {e}")
            time.sleep(5)  # Wait before retry
