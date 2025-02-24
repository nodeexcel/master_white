import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Twitter API credentials
    # X_USER_ID = int(os.getenv("X_USER_ID"))
    
    X_USER_ID = os.getenv("X_USER_ID", 1892103401103818753).strip().replace('"', '').replace("'", "")
    if X_USER_ID:
        try:
            # Clean the value by removing extra spaces and quotes
            X_USER_ID = int(X_USER_ID.strip().replace('"', ''))  # Clean up unwanted characters
        except ValueError as e:
            print(f"Error: X_USER_ID is not a valid integer. {e}")
            X_USER_ID = None
    
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
    X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    # Bot configurations
    MENTION_BOT_INTERVAL = int(os.getenv("MENTION_BOT_INTERVAL", 60))  # Seconds
    INFLUENCER_BOT_INTERVAL = int(os.getenv("INFLUENCER_BOT_INTERVAL", 3600))  # Seconds
    MAX_COMMENTS_PER_TWEET = int(os.getenv("MAX_COMMENTS_PER_TWEET", 100))
    
    # Content settings
    POST_THEMES = os.getenv("POST_THEMES", "technology,social media,AI").split(",")
    REPLY_TONE = os.getenv("REPLY_TONE", "friendly,professional")
    
    TIME_WINDOW_MINUTES = int(os.getenv('TIME_WINDOW_MINUTES', 1440))   #The time window in minutes to filter mentions (e.g., 1440 for 24 hours).
    
    #db innit
    MONGO_URI = os.getenv("MONGO_URI")
