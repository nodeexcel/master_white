from flask import Flask
from flask_pymongo import PyMongo
from app.config import Config
from apscheduler.schedulers.background import BackgroundScheduler

mongo_client = PyMongo()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    mongo_client.init_app(app)

    # Initialize scheduler inside create_app to avoid circular imports
    scheduler = BackgroundScheduler()
    
    # Import mention_job here to avoid circular imports
    from app.services.mention_bot import mention_job
    scheduler.add_job(func=mention_job, trigger='interval', minutes=1)
    scheduler.start()
    
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        if scheduler.running:
            scheduler.shutdown()

    return app
