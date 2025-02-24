import tweepy
import datetime
from app.utils.common_utils import generate_unique_response
from app.config import Config
import logging

logger = logging.getLogger(__name__)

def create_x_client(config):
    """
    Create the Twitter Client
    """
    return tweepy.Client(
        bearer_token=config.BEARER_TOKEN,
        consumer_key=config.CONSUMER_KEY,
        consumer_secret=config.CONSUMER_SECRET,
        access_token=config.X_ACCESS_TOKEN,
        access_token_secret=config.X_ACCESS_TOKEN_SECRET,
    )

def fetch_mentions(client: object, user_id: int):
    """
    return the user's mentions info and their comment
    """
    try:
        time_window_minutes = Config.TIME_WINDOW_MINUTES
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(minutes=time_window_minutes)
        
        # Convert to ISO 8601 format (e.g., 2023-02-22T10:15:00Z)
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        response = client.get_users_mentions(
            id=user_id,  # Ensure clean integer ID
            tweet_fields=['created_at', 'text', 'author_id'],
            expansions=[
                'author_id',
                'in_reply_to_user_id',
                'referenced_tweets.id',
                'referenced_tweets.id.author_id'
            ],
            max_results=10,
            start_time=start_time_str,
            end_time=end_time_str
        )
        return response

    except tweepy.errors.Unauthorized as e:  # Handle 401 Unauthorized error
        logger.error("Unauthorized. Check API credentials and permissions.%s", e)
        return None

    except tweepy.errors.TooManyRequests as e:  # Handle Rate Limit Exceeded
        logger.error("Rate limit exceeded. Try again later. Details: %s", e)
        return None

    except Exception as e:
        logger.error("Exception occurred in get_users_mentions_info: %s", e)
        return None

def store_mentions_data(mentions_data: list, collection):
    if not mentions_data:
        return
    for tweet in mentions_data:
        tweet_id = tweet.id
        if collection.find_one({"tweet_id": tweet_id}) is None:
            doc = {
                "tweet_id": tweet_id,
                "text": tweet.text,
                "is_processed": False,
                "reply_text": None,
            }
            collection.insert_one(doc)
            print(f"Stored tweet {tweet_id} in DB.")
        else:
            print(f"Tweet {tweet_id} already exists in DB.")

def reply_mentions_tweet(client, tweet_id, user_text, openai_client):
    """Handle the complete reply process"""
    try:
        reply_text = generate_unique_response(openai_client, user_text)
        if not reply_text:
            return False, None           
                    
        response = client.create_tweet(
            in_reply_to_tweet_id=tweet_id,
            text=reply_text
        )
        logger.info(f"Successfully replied to tweet {tweet_id} and response {response}")
        return True, reply_text
        
    except tweepy.errors.Forbidden as e:
        logger.error(f"403 Forbidden error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error replying to tweet {tweet_id}: {e}")
        return False, None
