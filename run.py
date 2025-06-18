#!/usr/bin/env python3
"""
Flask Server for XML-MCP Template

This Flask server provides REST API endpoints for XML processing.
It works in conjunction with the MCP server to provide a dual-server architecture.

Usage:
    python run.py

The server will start on http://localhost:5000 by default.
"""

import os
import logging
from flask import Flask
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for Flask server"""
    # Create Flask application
    app = create_app()
    
    # Configuration
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Start the server
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == '__main__':
    main()