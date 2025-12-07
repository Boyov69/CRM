"""Backend configuration"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    # Database
    DATA_FILE = 'data/practices.json'
    EMAIL_LOGS_FILE = 'data/email_logs.json'
    
    # Email Provider
    EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'sendgrid')
    
    # SendGrid
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@zorgcore.be')
    SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'ZorgCore Team')
    
    # Gmail API
    GMAIL_CREDENTIALS_FILE = 'credentials.json'
    GMAIL_TOKEN_FILE = 'token.json'
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    # SMTP
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True') == 'True'
    
    # Slack
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google Maps API (for lead discovery)
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Brave Search API (for website finding)
    BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Campaign Settings
    MAX_EMAILS_PER_PRACTICE = int(os.getenv('MAX_EMAILS_PER_PRACTICE', 3))
    EMAIL_DELAY_DAYS = [0, 5, 12]
    DAILY_EMAIL_LIMIT = int(os.getenv('DAILY_EMAIL_LIMIT', 100))
    EMAILS_PER_MINUTE = int(os.getenv('EMAILS_PER_MINUTE', 10))
    
    # Tracking
    ENABLE_OPEN_TRACKING = os.getenv('ENABLE_OPEN_TRACKING', 'True') == 'True'
    ENABLE_CLICK_TRACKING = os.getenv('ENABLE_CLICK_TRACKING', 'True') == 'True'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/campaign.log'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DAILY_EMAIL_LIMIT = 10


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DAILY_EMAIL_LIMIT = 500


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
