import schedule
import time
from datetime import datetime
import logging
from app.config import Config
from app.Agent.utils.twitter_utils import create_x_client, upload_media
from .content_generator import DogContentGenerator
from .image_generator import DogImageGenerator
import requests
import os

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self):
        self.client, self.api = create_x_client(Config)
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
            
    def post_image_content(self):
        try:
            image_generator = DogImageGenerator()
            post = image_generator.generate_image_and_caption()
            
            if post["image_url"]:
                # Download image
                response = requests.get(post["image_url"])
                temp_image = "temp_image.jpg"
                with open(temp_image, "wb") as f:
                    f.write(response.content)
                
                # Upload media using v1 API
                media_id = upload_media(self.api, temp_image)
                
                # Create tweet with media using v2 API
                response = self.client.create_tweet(
                    text=post["caption"],
                    media_ids=[media_id]
                )
                
                # Cleanup
                os.remove(temp_image)
                
                logger.info(f"Posted new image content of type: {post['type']}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error posting image content: {e}")
            return False

    def start_scheduler(self):
        # Post immediately on startup
        self.post_content()
        self.post_image_content()
        
        # Schedule regular posts
        schedule.every(35).minutes.do(self.post_content)
        schedule.every(60).minutes.do(self.post_image_content)
        
        while True:
            schedule.run_pending()
            time.sleep(60) 