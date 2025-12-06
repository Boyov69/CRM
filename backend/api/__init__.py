"""API routes registration"""
from flask import Flask
from backend.api.practices import practices_bp
from backend.api.campaigns import campaigns_bp
from backend.api.leads import leads_bp
from backend.api.pipeline_api import pipeline_bp
from backend.api.sms_api import sms_bp
from backend.api.whatsapp_api import whatsapp_bp
from backend.api.inbox_api import inbox_bp
from backend.api.voice_api import voice_bp


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    app.register_blueprint(practices_bp, url_prefix='/api')
    app.register_blueprint(campaigns_bp, url_prefix='/api')
    app.register_blueprint(leads_bp, url_prefix='/api')
    app.register_blueprint(pipeline_bp, url_prefix='/api')
    app.register_blueprint(sms_bp, url_prefix='/api')
    app.register_blueprint(whatsapp_bp, url_prefix='/api')
    app.register_blueprint(inbox_bp, url_prefix='/api/inbox')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
