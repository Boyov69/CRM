"""Email service - handles email sending"""
import logging
from typing import Dict

from backend.config import Config

logger = logging.getLogger(__name__)


class EmailService:
    """Email service with multiple provider support"""
    
    def __init__(self):
        self.provider = Config.EMAIL_PROVIDER
        self._init_provider()
    
    def _init_provider(self):
        """Initialize email provider"""
        if self.provider == 'sendgrid':
            from modules.sendgrid_integration import SendGridEmailService
            self.client = SendGridEmailService()
        elif self.provider == 'gmail':
            # TODO: Implement Gmail sender
            logger.warning("Gmail sender not yet implemented")
            self.client = None
        else:
            logger.warning(f"Unknown provider: {self.provider}")
            self.client = None
    
    def send_campaign_email(self, practice: Dict, template_type: str, use_ai: bool = False) -> bool:
        """Send campaign email to practice"""
        if not self.client:
            logger.error("Email client not initialized")
            return False
        
        try:
            # Generate email content
            if use_ai:
                from modules.ai_email_generator import AIEmailGenerator
                email_content = AIEmailGenerator.generate_personalized_email(
                    practice, template_type
                )
            else:
                from modules.email_templates import EmailTemplates
                email_content = EmailTemplates.get_template(template_type, practice)
            
            # Send email
            success, _ = self.client.send_email(
                to_email=practice.get('email'),
                subject=email_content['subject'],
                body_text=email_content['body'],
                body_html=email_content.get('html'),
                custom_args={'practice_id': practice['nr']}
            )
            
            return success
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
