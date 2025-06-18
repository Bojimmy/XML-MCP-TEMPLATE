"""
Flask Application Factory

This module creates and configures the Flask application for XML processing.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS


def create_app(config_name=None):
    """
    Create and configure Flask application
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure CORS for web UI integration
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Basic configuration
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'xml-mcp-template-dev-key'),
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True
    )
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'xml-mcp-template'}, 200
    
    @app.route('/')
    def index():
        """Root endpoint with API information"""
        return {
            'service': 'XML-MCP Template Flask Server',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'analyze': '/api/analyze',
                'generate': '/api/generate', 
                'status': '/api/status',
                'data': '/api/data'
            }
        }, 200
    
    return app


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error', 'message': 'Something went wrong'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle unexpected exceptions"""
        app.logger.error(f"Unhandled exception: {e}")
        return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500