import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Twitter configuration
    X_USER_ID = os.getenv("X_USER_ID")
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
    X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    # Bot configurations
    TIME_WINDOW_MINUTES = int(os.getenv("TIME_WINDOW_MINUTES", 1440))
    
    # RabbitMQ configuration
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    QUEUE_NAME = os.getenv("QUEUE_NAME", "mr_white_v3_queue")
    
    # MongoDB configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/mr_white_v3")
    
    # New configuration
    X_USERNAME = os.getenv("X_USERNAME")  # Your bot's Twitter username without @
    
