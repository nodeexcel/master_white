from flask import Flask
from app.config import Config
from app.database import init_db, mongo_client
from app.Agent.services.mention_handler import MentionSearchHandler
from app.Agent.services.mention_bot import MentionConsumer
import threading
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_bot_service():
    """Single thread to handle both mention checking and processing"""
    handler = MentionSearchHandler()
    consumer = MentionConsumer()
    
    while True:
        try:
            # Process mentions and add to queue
            handler.process_mentions()
            # Process messages from queue
            consumer.message_queue.consume_messages(consumer.process_mention)
            time.sleep(1800)  # Changed from 30 to 1800 seconds (30 minutes)
        except Exception as e:
            logger.error(f"Error in bot service: {e}")
            time.sleep(15)  # Wait before retry

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    
    # Initialize database
    if init_db(app):
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to initialize database")
    
    # Start single bot service thread
    bot_thread = threading.Thread(
        target=start_bot_service,
        daemon=True,
        name='bot_service'
    )
    bot_thread.start()
    logger.info("Started bot service thread")
    
    logger.info("Application startup complete")
    return app
