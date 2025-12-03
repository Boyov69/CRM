# modules/response_tracker.py
import os.path
import base64
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class GmailResponseTracker:
    """
    Trackt antwoorden via Gmail API
    """
    
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticatie met Gmail API"""
        if not os.path.exists(Config.GMAIL_CREDENTIALS_FILE):
            logger.warning("Gmail credentials file not found. Response tracking disabled.")
            return

        try:
            if os.path.exists(Config.GMAIL_TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(Config.GMAIL_TOKEN_FILE, Config.GMAIL_SCOPES)
            
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        Config.GMAIL_CREDENTIALS_FILE, Config.GMAIL_SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(Config.GMAIL_TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail API authenticatie succesvol")
            
        except Exception as e:
            logger.error(f"Gmail authenticatie fout: {e}")
            self.service = None

    def check_for_replies(self, practice_emails):
        """
        Check of er antwoorden zijn van specifieke email adressen
        
        Args:
            practice_emails: List van email adressen om te checken
        
        Returns:
            Dictionary met {email: reply_data}
        """
        if not self.service:
            return {}
            
        replies = {}
        
        try:
            # Zoek naar ongelezen berichten in Inbox
            # Query: is:unread in:inbox
            results = self.service.users().messages().list(userId='me', q='is:unread in:inbox').execute()
            messages = results.get('messages', [])
            
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                
                from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                
                # Extract email adres from "Naam <email@domain.com>"
                import re
                email_match = re.search(r'<(.+?)>', from_header)
                sender_email = email_match.group(1) if email_match else from_header
                
                if sender_email in practice_emails:
                    # We hebben een antwoord!
                    body = self._get_email_body(msg)
                    
                    replies[sender_email] = {
                        'subject': subject,
                        'body': body,
                        'date': datetime.now().isoformat(),
                        'message_id': message['id']
                    }
                    
                    logger.info(f"Antwoord gedetecteerd van {sender_email}")
                    
                    # Markeer als gelezen (optioneel, misschien wil user dit zelf doen)
                    # self._mark_as_read(message['id'])
            
            return replies
            
        except Exception as e:
            logger.error(f"Fout bij checken replies: {e}")
            return {}
    
    def _get_email_body(self, msg):
        """Haal body uit email message"""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    return base64.urlsafe_b64decode(data).decode()
        elif 'body' in msg['payload']:
            data = msg['payload']['body']['data']
            return base64.urlsafe_b64decode(data).decode()
        return ""
    
    def _mark_as_read(self, message_id):
        """Markeer bericht als gelezen"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except Exception as e:
            logger.error(f"Fout bij markeren als gelezen: {e}")

class ResponseMatcher:
    """
    Analyseert antwoorden om intentie te bepalen
    """
    
    POSITIVE_KEYWORDS = ['interesse', 'demo', 'afspraak', 'bellen', 'graag', 'ja', 'zeker']
    NEGATIVE_KEYWORDS = ['geen interesse', 'uitschrijven', 'stop', 'nee', 'niet bellen']
    
    @staticmethod
    def analyze_sentiment(email_body):
        """
        Simpele sentiment analyse
        Returns: 'positive', 'negative', 'neutral'
        """
        body_lower = email_body.lower()
        
        positive_score = sum(1 for word in ResponseMatcher.POSITIVE_KEYWORDS if word in body_lower)
        negative_score = sum(1 for word in ResponseMatcher.NEGATIVE_KEYWORDS if word in body_lower)
        
        if negative_score > 0:
            return 'negative'
        elif positive_score > 0:
            return 'positive'
        else:
            return 'neutral'

class AutomatedResponseHandler:
    """
    Handelt automatische reacties af op basis van sentiment
    """
    
    @staticmethod
    def handle_response(practice_data, reply_data):
        """
        Verwerk een antwoord
        """
        sentiment = ResponseMatcher.analyze_sentiment(reply_data['body'])
        
        action_taken = "none"
        
        if sentiment == 'negative':
            # Automatisch uitschrijven
            # Update practice status to 'Opt-out'
            action_taken = "opt_out"
            
        elif sentiment == 'positive':
            # Markeer als 'Lead' en stuur notificatie naar sales
            action_taken = "mark_lead"
            
            # Optioneel: Stuur automatische bevestiging
            # send_confirmation_email(...)
            
        return {
            'sentiment': sentiment,
            'action': action_taken
        }
