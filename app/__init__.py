from flask import Flask
from flask_cors import CORS
from .routers import schedules
from .database import engine, Base

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["https://taco-ui-1024364663505.us-central1.run.app"])
    # Register blueprints
    app.register_blueprint(schedules.schedules_blueprint)
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    return app
