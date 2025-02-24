import tweepy
# from .config import Config
from app.config import Config
import schedule
from app.utils.twitter_utils import (
    fetch_mentions,
    store_mentions_data,
    reply_mentions_tweet,
    create_x_client,
    
)
from app.utils.common_utils import create_openai_client
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

# def fetch_and_store_mentions():
#     try:
#         user_id = Config.X_USER_ID
#         if not user_id or not isinstance(user_id, int):
#             logger.error(f"Invalid X_USER_ID: {user_id}. Must be a valid integer.")
#             return
           
#         # user_id=1892103401103818753
#         logger.debug(f"Fetching mentions for user_id: {user_id}")
#         mentions = fetch_mentions(client=x_client, user_id=user_id)
        
#         print("mention data", mentions)
        
#         print("only data", mentions.data)
#  # Check if 'mentions' is a Response object (with a .data attribute) or a plain list.
#         if not mentions:
#             logger.error("Failed to fetch mentions - no data returned")
#             return

#         if isinstance(mentions, list):
#             data = mentions
#         elif hasattr(mentions, "data"):
#             data = mentions.data
#         else:
#             logger.error("Unexpected type returned from fetch_mentions")
#             return

#         if data:
#             logger.info("Storing Data in mongo db")
#             print("storing mention data")
#             store_mentions_data(mentions_data=data, collection=mention_collection)
#         else:
#             print("No new mentions found.")
#     except Exception as e:
#         print(f"Error fetching mentions: {e}")


def fetch_and_store_mentions():
    try:
        user_id = Config.X_USER_ID
        if not user_id or not isinstance(user_id, int):
            logger.error("Invalid X_USER_ID: %s. Must be a valid integer.", user_id)
            return
           
        logger.debug("Fetching mentions for user_id: %s", user_id)
        mentions = fetch_mentions(client=x_client, user_id=user_id)
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
            is_processed = mention["is_processed"]

            if not is_processed:
                print(f"Processing tweet {tweet_id} with text: {text}")
                response, reply_text = reply_mentions_tweet(
                    client=x_client,
                    tweet_id=tweet_id,
                    user_text=text,
                    openai_client=openai_client,
                )
                print("update_mention_response", response)
                if response:
                    mention_collection.update_one(
                        {"tweet_id": tweet_id},
                        {"$set": {"is_processed": True, "reply_text": str(reply_text)}},
                    )
                    print(
                        f"Successfully processed and replied to tweet {tweet_id} with reply_text: {reply_text}"
                    )
                else:
                    print(f"Failed to reply to tweet {tweet_id}.")

            else:
                print(
                    f"Tweet {tweet_id} has already been processed with reply_text {mention['reply_text']}."
                )
    except Exception as e:
        print(f"Error processing mentions reply: {e}")


def mention_job():
    """
    The scheduled job that runs both fetching and processing.
    """
    print("Starting scheduled job...")
    fetch_and_store_mentions()
    reply_update_mention_tweets()
    print("Job finished.\n")
