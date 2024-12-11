from flask import Flask, request, g
from flask_cors import CORS
from .routers import schedules
from .database import engine, Base
import uuid
from google.cloud import logging_v2 as cloud_logging

def create_app():
    app = Flask(__name__)
    CORS(app)
    # Logging
    client = cloud_logging.Client()
    client.setup_logging() 
    #Correlation id
    @app.before_request
    def set_correlation_id():
        # Check if the header is present; if not, generate a new UUID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        g.correlation_id = correlation_id

    @app.after_request
    def add_correlation_id_to_response(response):
        # Include the correlation ID in the response headers for visibility
        if hasattr(g, "correlation_id"):
            response.headers["X-Correlation-ID"] = g.correlation_id
        return response

    # Register blueprints
    app.register_blueprint(schedules.schedules_blueprint)
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    return app
