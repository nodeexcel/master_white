import tweepy
# from .config import Config
from app.config import Config
import schedule
from app.utils.twitter_utils import (
    fetch_mentions,
    store_mentions_data,
    reply_mentions_tweet,
    get_last_processed_tweet_id,
    create_x_client,
    
)
from app.utils.common_utils import create_openai_client
from pymongo import ReturnDocument
from app import mongo_client
import datetime
import time
import logging

logger = logging.getLogger(__name__,)

x_client = create_x_client(Config)
openai_client = create_openai_client(Config)

# Access database and collection
mention_collection = mongo_client.db['mentions']
print("mention_colect", mention_collection)

def fetch_and_store_mentions():
    try:
        user_id = Config.X_USER_ID
        if not user_id or not isinstance(user_id, int):
            logger.error("Invalid X_USER_ID: %s. Must be a valid integer.", user_id)
            return
           
        logger.debug("Fetching mentions for user_id: %s", user_id)
        
        
        last_processed_id = get_last_processed_tweet_id(mention_collection)
        if last_processed_id:
            logger.debug("Using last processed tweet ID: %s", last_processed_id)
        else:
            logger.debug("No last processed tweet found; fetching latest mentions.")
        
        
        mentions = fetch_mentions(client=x_client, user_id=user_id, since_id=last_processed_id)
        if not mentions:
            logger.error("Failed to fetch mentions – no data returned")
            return

        # If the response has a .data attribute, extract it; otherwise assume it's already a list.
        data = mentions.data if hasattr(mentions, "data") else mentions
        if not data:
            logger.info("No new mentions found.")
            return

        logger.info("Storing %d tweet(s) in MongoDB.", len(data))
        store_mentions_data(mentions_data=data, collection=mention_collection)
    except Exception as e:
        logger.error("Error fetching mentions: %s", e)


def reply_update_mention_tweets():
    try:
        unprocessed_mentions = mention_collection.find({"is_processed": False})
        for mention in unprocessed_mentions:
            tweet_id = mention["tweet_id"]
            text = mention["text"]
            author_id = mention.get("author_id")
            in_reply_to_user_id = mention.get("in_reply_to_user_id")
            # conversation_id = mention.get("conversation_id")

            # Skip bot's own tweets and replies to itself
            if author_id == Config.X_USER_ID or in_reply_to_user_id == Config.X_USER_ID:
                mention_collection.update_one(
                    {"tweet_id": tweet_id},
                    {"$set": {"is_processed": True, "is_own_conversation": True}}
                )
                continue

            # Lock tweet for processing
            locked_mention = mention_collection.find_one_and_update(
                {"tweet_id": tweet_id, "is_processed": False},
                {"$set": {"processing": True}},
                return_document=ReturnDocument.AFTER
            )
            
            if locked_mention:
                try:
                    response, reply_text = reply_mentions_tweet(
                        client=x_client,
                        tweet_id=tweet_id,
                        user_text=text,
                        openai_client=openai_client,
                    )
                    
                    if response:
                        mention_collection.update_one(
                            {"tweet_id": tweet_id},
                            {"$set": {
                                "is_processed": True,
                                "reply_text": str(reply_text),
                                "processing": False
                            }}
                        )
                except Exception as e:
                    mention_collection.update_one(
                        {"tweet_id": tweet_id},
                        {"$set": {"processing": False}}
                    )
                    raise e
    except Exception as e:
        logger.error(f"Error processing mentions: {str(e)}")


def mention_job():
    """
    The scheduled job that runs both fetching and processing.
    """
    print("Starting scheduled job...")
    fetch_and_store_mentions()
    reply_update_mention_tweets()
    print("Job finished.\n")
