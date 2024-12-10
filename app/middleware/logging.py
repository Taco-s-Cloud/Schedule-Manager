import logging
import uuid
from flask import request
from google.cloud import logging_v2 as cloud_logging
from google.cloud import trace
from opencensus.trace import config_integration
from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.tracer import Tracer

# Setup Google Cloud Logging
def setup_logging():
    """Initialize Google Cloud Logging."""
    client = cloud_logging.Client()
    client.setup_logging()
    logging.info("Google Cloud Logging is configured.")

# Middleware for adding Correlation ID and tracing
def add_correlation_id(app):
    """Middleware to add Correlation ID and trace requests."""
    config_integration.trace_integrations(['logging'])
    exporter = stackdriver_exporter.StackdriverExporter()
    tracer = Tracer(exporter=exporter, sampler=AlwaysOnSampler())

    @app.before_request
    def start_trace_and_add_correlation_id():
        # Start a trace
        tracer.span_context.trace_id

        # Generate or retrieve Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.correlation_id = correlation_id

        # Attach Correlation ID to logs
        logging.info(f"Correlation ID: {correlation_id}")

    @app.after_request
    def end_trace_and_add_correlation_id_to_response(response):
        # Include Correlation ID in the response headers
        response.headers["X-Correlation-ID"] = request.correlation_id
        return response
