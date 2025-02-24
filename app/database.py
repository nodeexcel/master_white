from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo_client = PyMongo()

def init_db(app):
    """Initialize the database with the Flask app"""
    try:
        mongo_client.init_app(app)
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False 