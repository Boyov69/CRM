"""API routes registration"""
from flask import Flask
from backend.api.practices import practices_bp
from backend.api.campaigns import campaigns_bp
from backend.api.leads import leads_bp


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    app.register_blueprint(practices_bp, url_prefix='/api')
    app.register_blueprint(campaigns_bp, url_prefix='/api')
    app.register_blueprint(leads_bp, url_prefix='/api')
