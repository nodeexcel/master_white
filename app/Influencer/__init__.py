from .post_scheduler import PostScheduler
import threading
import logging

logger = logging.getLogger(__name__)

def start_influencer():
    try:
        scheduler = PostScheduler()
        scheduler.start_scheduler()
    except Exception as e:
        logger.error(f"Error starting influencer: {e}") 