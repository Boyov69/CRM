# modules/sendgrid_integration.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization, Substitution
import logging
from config import Config

logger = logging.getLogger(__name__)

class SendGridEmailService:
    """
    Professional email service via SendGrid
    - Betere deliverability
    - Tracking ingebouwd
    - Hogere verzendlimieten
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.SENDGRID_API_KEY
        # Only initialize if API key is present to avoid errors during dev without key
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
            self.from_email = Email(Config.SENDGRID_FROM_EMAIL, Config.SENDGRID_FROM_NAME)
        else:
            self.client = None
            logger.warning("SendGrid API Key missing. Service initialized in mock mode.")
    
    def send_email(self, to_email, subject, body_text, body_html=None, 
                   tracking_settings=None, custom_args=None):
        """
        Verstuur email via SendGrid
        """
        if not self.client:
             logger.info(f"[MOCK SENDGRID] To: {to_email} | Subject: {subject}")
             return True, {'status_code': 202, 'message_id': 'mock-id', 'body': 'mock-body'}

        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body_text,
                html_content=body_html or body_text
            )
            
            # Tracking instellingen
            if tracking_settings is None:
                tracking_settings = {
                    'open_tracking': Config.ENABLE_OPEN_TRACKING,
                    'click_tracking': Config.ENABLE_CLICK_TRACKING
                }
            
            message.tracking_settings = self._build_tracking_settings(tracking_settings)
            
            # Custom arguments voor analytics
            if custom_args:
                for key, value in custom_args.items():
                    message.custom_arg = CustomArg(key, str(value))
            
            # Verstuur
            response = self.client.send(message)
            
            logger.info(f"Email verzonden naar {to_email} - Status: {response.status_code}")
            
            return True, {
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'body': response.body
            }
            
        except Exception as e:
            logger.error(f"SendGrid fout voor {to_email}: {e}")
            return False, {'error': str(e)}
    
    def send_bulk_emails(self, recipients_data):
        """
        Verstuur bulk emails met personalisatie
        """
        success_count = 0
        failed_count = 0
        results = []
        
        for recipient in recipients_data:
            success, response = self.send_email(
                to_email=recipient['email'],
                subject=recipient['subject'],
                body_text=recipient['body_text'],
                body_html=recipient.get('body_html'),
                custom_args=recipient.get('custom_args')
            )
            
            results.append({
                'email': recipient['email'],
                'success': success,
                'response': response
            })
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        return success_count, failed_count, results
    
    def _build_tracking_settings(self, settings):
        """Bouw tracking settings object"""
        from sendgrid.helpers.mail import TrackingSettings, OpenTracking, ClickTracking
        
        tracking = TrackingSettings()
        
        if settings.get('open_tracking'):
            tracking.open_tracking = OpenTracking(
                enable=True,
                substitution_tag='[TRACKING_PIXEL]'
            )
        
        if settings.get('click_tracking'):
            tracking.click_tracking = ClickTracking(
                enable=True,
                enable_text=True
            )
        
        return tracking
    
    def get_email_stats(self, start_date, end_date=None):
        """
        Haal email statistieken op via SendGrid API
        """
        if not self.client:
            return {}

        try:
            params = {
                'start_date': start_date,
                'aggregated_by': 'day'
            }
            
            if end_date:
                params['end_date'] = end_date
            
            response = self.client.client.stats.get(query_params=params)
            
            return response.to_dict
            
        except Exception as e:
            logger.error(f"Fout bij ophalen stats: {e}")
            return {}
    
    def validate_email(self, email):
        """
        Valideer email adres via SendGrid Validation API
        """
        if not self.client:
             # Fallback naar simpele regex validatie
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))

        try:
            # SendGrid email validation
            # Note: Dit vereist een betaald SendGrid plan
            response = self.client.client.validations.email.post(
                request_body={'email': email}
            )
            return response.status_code == 200
        except:
            # Fallback naar simpele regex validatie
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))

# Webhook handler voor SendGrid events
class SendGridWebhookHandler:
    """
    Verwerkt webhooks van SendGrid voor event tracking
    Events: delivered, opened, clicked, bounced, etc.
    """
    
    @staticmethod
    def process_webhook(webhook_data):
        """
        Verwerk inkomende webhook data
        """
        from datetime import datetime
        import json
        
        events = []
        
        for event in webhook_data:
            event_type = event.get('event')
            email = event.get('email')
            timestamp = event.get('timestamp')
            practice_id = event.get('practice_id')  # Custom arg
            
            events.append({
                'type': event_type,
                'email': email,
                'timestamp': datetime.fromtimestamp(timestamp),
                'practice_id': practice_id
            })
            
            logger.info(f"Webhook event: {event_type} voor {email}")
        
        return events
    
    @staticmethod
    def update_practice_tracking(practice_id, event_type):
        """Update praktijk data met tracking info"""
        # Circular import avoidance
        # In a real app, data access layer should be separate
        # For now, we will assume this is called from app context or refactor later
        pass
