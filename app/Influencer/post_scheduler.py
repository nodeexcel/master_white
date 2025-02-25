import schedule
import time
from datetime import datetime
import logging
from app.config import Config
from app.Agent.utils.twitter_utils import create_x_client
from .content_generator import DogContentGenerator

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self):
        self.client = create_x_client(Config)
        self.content_generator = DogContentGenerator()
        self.post_history = []
        
    def post_content(self):
        try:
            post = self.content_generator.generate_post()
            
            # Avoid duplicate content types in succession
            while len(self.post_history) > 0 and post["type"] == self.post_history[-1]:
                post = self.content_generator.generate_post()
                
            response = self.client.create_tweet(text=post["content"])
            
            self.post_history.append(post["type"])
            if len(self.post_history) > 5:
                self.post_history.pop(0)
                
            logger.info(f"Posted new content of type: {post['type']}")
            return True
        except Exception as e:
            logger.error(f"Error posting content: {e}")
            return False
            
    def start_scheduler(self):
        # Post immediately on startup
        self.post_content()
        
        # Schedule regular posts
        schedule.every(35).minutes.do(self.post_content)
        
        while True:
            schedule.run_pending()
            time.sleep(60) 