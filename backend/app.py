"""
Main Flask application for CRM backend
"""
from flask import Flask
from flask_cors import CORS
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.api import register_blueprints

# Ensure log directory exists before configuring logging
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(project_root, Config.LOG_FILE)
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register API blueprints
    register_blueprints(app)
    
    # Initialize WebSocket
    from flask_sock import Sock
    sock = Sock(app)
    
    from backend.services.voice_service import VoiceService
    voice_service = VoiceService()
    
    @sock.route('/api/voice/stream')
    def voice_stream(ws):
        # Run async handler in sync context if needed, or use sock's threading
        # For simplicity calling the service method handled in a simple loop
        import asyncio
        asyncio.run(voice_service.handle_audio_stream(ws))
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'version': '0.1.0'}
    
    return app


if __name__ == '__main__':
    # Change to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
