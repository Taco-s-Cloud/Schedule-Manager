from flask import Flask
from flask_cors import CORS
from .routers import schedules
from .database import engine, Base
# from .middleware.logging import setup_logging, add_correlation_id
from google.cloud import logging_v2 as cloud_logging

def create_app():
    app = Flask(__name__)
    CORS(app)
    client = cloud_logging.Client()
    client.setup_logging() 
    # setup_logging()
    # add_correlation_id(app)
    # Register blueprints
    app.register_blueprint(schedules.schedules_blueprint)
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    return app
