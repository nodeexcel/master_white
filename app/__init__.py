from flask import Flask
from app.config import Config
from app.database import init_db, mongo_client
from app.Agent.services.mention_handler import start_search_handler
from app.Agent.services.mention_bot import start_mention_consumer
from app.Influencer import start_influencer
import threading
import logging
import time
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    
    # Initialize database
    if init_db(app):
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to initialize database")
    
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Start mention checker thread
        checker_thread = threading.Thread(
            target=start_search_handler,
            daemon=True,
            name='mention_checker'
        )
        checker_thread.start()
        logger.info("Started mention checker thread")
        
        # Start consumer thread
        consumer_thread = threading.Thread(
            target=start_mention_consumer,
            daemon=True,
            name='mention_consumer'
        )
        consumer_thread.start()
        logger.info("Started consumer thread")
        
        # Start influencer thread
        influencer_thread = threading.Thread(
            target=start_influencer,
            daemon=True,
            name='influencer'
        )
        influencer_thread.start()
        logger.info("Started influencer thread")
    
    logger.info("Application startup complete")
    return app
