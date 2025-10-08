#!/usr/bin/env python3
"""
Main entry point for the Raspberry Pi 3 application
"""

import os
import sys
import signal
import logging
from app import create_app
from config import get_config

# Get configuration
config = get_config()

# Configure logging with config settings
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


def signal_handler(_sig, _frame):
    """Handle graceful shutdown"""
    logger.info("Shutting down gracefully...")
    # GPIO cleanup will be handled by the GPIOController
    sys.exit(0)


def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create Flask app and SocketIO instance
    app, socketio = create_app()

    # Get host and port from configuration
    host = config.HOST
    port = config.PORT
    debug = config.DEBUG

    logger.info(f"Starting Raspberry Pi 3 Application on http://{host}:{port}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    logger.info(f"Debug mode: {debug}")

    try:
        # Run the application
        # Note: This uses Werkzeug development server, suitable for local network use
        # For production deployment on public networks, see DEPLOYMENT.md for Gunicorn setup
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True,  # Intentional: This app is designed for local use
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
