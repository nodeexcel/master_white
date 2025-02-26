import tweepy
import logging
import time
from app.Agent.utils.common_utils import generate_response

logger = logging.getLogger(__name__)

def create_x_client(config):
    """Create the Twitter Client with v2 API"""
    # Create v2 client
    client = tweepy.Client(
        bearer_token=config.BEARER_TOKEN,
        consumer_key=config.CONSUMER_KEY,
        consumer_secret=config.CONSUMER_SECRET,
        access_token=config.X_ACCESS_TOKEN,
        access_token_secret=config.X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    
    # Create v1 auth
    auth = tweepy.OAuth1UserHandler(
        config.CONSUMER_KEY,
        config.CONSUMER_SECRET,
        config.X_ACCESS_TOKEN,
        config.X_ACCESS_TOKEN_SECRET
    )
    
    # Create v1 API for media upload
    api = tweepy.API(auth)
    
    return client, api

def create_x_auth(config):
    """Create Twitter OAuth 2.0 Client"""
    return tweepy.OAuth2BearerHandler(config.BEARER_TOKEN)

def reply_to_tweet(client, tweet_id: str, user_text: str, openai_client) -> tuple[bool, str]:
    """Reply to a tweet with generated response"""
    try:
        reply_text = generate_response(openai_client, user_text)
        if not reply_text:
            return False, None

        response = client.create_tweet(
            text=reply_text,
            in_reply_to_tweet_id=tweet_id
        )
        logger.info(f"Successfully replied to tweet {tweet_id}")
        return True, reply_text

    except tweepy.Forbidden as e:
        logger.error(f"Cannot reply to tweet {tweet_id}: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error replying to tweet {tweet_id}: {e}")
        return False, None

def send_direct_message(client, user_id: str, message: str) -> bool:
    """Send a direct message using Twitter API v2"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Check if message is within Twitter's character limit
            if len(message) > 280:
                message = message[:277] + "..."
            
            # Use v2 API for DMs
            response = client.create_direct_message(
                participant_id=user_id,
                text=message
            )
            
            if response and hasattr(response, 'data'):
                logger.info(f"Successfully sent DM to user {user_id}")
                return True
            
            logger.error(f"Failed to send DM - Invalid response: {response}")
            return False
            
        except tweepy.TooManyRequests as e:
            wait_time = int(e.response.headers.get('x-rate-limit-reset', 60))
            logger.warning(f"Rate limit hit. Waiting {wait_time} seconds")
            if attempt < max_retries - 1:
                time.sleep(min(wait_time, 60))  # Wait max 60 seconds
                continue
            return False
            
        except tweepy.Forbidden as e:
            # Instead of DM, let's reply to the tweet
            logger.warning(f"Cannot send DM to user {user_id}, will try replying to tweet instead")
            return False
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed to send DM: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return False
    
    return False

def upload_media(api, image_path: str) -> str:
    """Upload media using Twitter API v1.1"""
    try:
        media = api.media_upload(filename=image_path)
        return media.media_id
    except Exception as e:
        logger.error(f"Error uploading media: {e}")
        raise
