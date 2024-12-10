import logging
import uuid
from flask import request
from google.cloud import logging_v2 as cloud_logging
from google.cloud import trace

# Initialize Cloud Trace Client
tracer = trace.Client()

def setup_logging():
    """Initialize Google Cloud Logging."""
    client = cloud_logging.Client()
    client.setup_logging()
    logging.info("Google Cloud Logging is configured.")

def add_correlation_id(app):
    """Middleware to add Correlation ID to every request."""
    @app.before_request
    def start_trace_and_add_correlation_id():
        # Start a trace span
        tracer.start_span(name=request.endpoint)

        # Generate or retrieve Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.correlation_id = correlation_id

        # Attach Correlation ID to logs
        logging.info(f"Correlation ID: {correlation_id}")

    @app.after_request
    def end_trace_and_add_correlation_id_to_response(response):
        # End the trace span
        tracer.end_span()

        # Include Correlation ID in the response headers
        response.headers["X-Correlation-ID"] = request.correlation_id
        return response
