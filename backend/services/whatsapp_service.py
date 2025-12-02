"""
WhatsApp Service - Twilio WhatsApp Business API Integration
Handles WhatsApp messaging with templates, media, and 2-way conversations
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending and managing WhatsApp messages via Twilio"""
    
    def __init__(self):
        """Initialize Twilio WhatsApp client"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if not all([self.account_sid, self.auth_token]):
            logger.warning("Twilio credentials not configured. WhatsApp functionality disabled.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info(f"Twilio WhatsApp service initialized with number {self.whatsapp_number}")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio WhatsApp client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if WhatsApp service is available"""
        return self.client is not None
    
    def send_message(
        self,
        to_number: str,
        message: str,
        practice_id: Optional[int] = None,
        campaign_id: Optional[int] = None,
        media_url: Optional[str] = None
    ) -> Dict:
        """
        Send a WhatsApp message
        
        Args:
            to_number: Recipient phone number (E.164 format: +32...)
            message: Message content
            practice_id: Optional practice ID for tracking
            campaign_id: Optional campaign ID for tracking
            media_url: Optional URL to media (image, PDF, etc.)
            
        Returns:
            Dict with status, message_sid, etc.
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'WhatsApp service not configured',
                'message': 'Twilio credentials missing'
            }
        
        # Format WhatsApp number
        to_whatsapp = self._format_whatsapp_number(to_number)
        
        try:
            # Prepare message parameters
            message_params = {
                'body': message,
                'from_': self.whatsapp_number,
                'to': to_whatsapp
            }
            
            # Add media if provided
            if media_url:
                message_params['media_url'] = [media_url]
            
            # Send WhatsApp message via Twilio
            message_obj = self.client.messages.create(**message_params)
            
            result = {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'to_number': to_number,
                'to_whatsapp': to_whatsapp,
                'from_whatsapp': self.whatsapp_number,
                'message': message,
                'media_url': media_url,
                'direction': 'outbound',
                'practice_id': practice_id,
                'campaign_id': campaign_id,
                'sent_at': datetime.now().isoformat()
            }
            
            logger.info(f"WhatsApp message sent to {to_number}: {message_obj.sid}")
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp to {to_number}: {e}")
            return {
                'success': False,
                'error': 'twilio_error',
                'message': str(e),
                'code': e.code,
                'to_number': to_number
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp: {e}")
            return {
                'success': False,
                'error': 'unknown_error',
                'message': str(e)
            }
    
    def send_template_message(
        self,
        to_number: str,
        template_name: str,
        template_params: List[str],
        practice_id: Optional[int] = None,
        campaign_id: Optional[int] = None
    ) -> Dict:
        """
        Send a WhatsApp template message (pre-approved by Facebook)
        
        Args:
            to_number: Recipient phone number
            template_name: Name of approved template
            template_params: List of parameter values for template variables
            practice_id: Optional practice ID
            campaign_id: Optional campaign ID
            
        Returns:
            Dict with status
            
        Note: Templates must be pre-approved by Facebook/Meta
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'WhatsApp service not configured'
            }
        
        to_whatsapp = self._format_whatsapp_number(to_number)
        
        # Build template content string
        # This is a simplified version - in production, use Twilio's Content API
        template = WHATSAPP_TEMPLATES.get(template_name)
        if not template:
            return {
                'success': False,
                'error': 'template_not_found',
                'template_name': template_name
            }
        
        # Replace template variables
        message = template['content']
        for i, param in enumerate(template_params, 1):
            message = message.replace(f'{{{{{i}}}}}', param)
        
        # Send as regular message (sandbox mode)
        # In production with approved templates, use ContentSid
        return self.send_message(
            to_number=to_number,
            message=message,
            practice_id=practice_id,
            campaign_id=campaign_id
        )
    
    def send_bulk_whatsapp(
        self,
        recipients: List[Dict],
        message: str,
        campaign_id: Optional[int] = None,
        media_url: Optional[str] = None
    ) -> Dict:
        """
        Send WhatsApp messages to multiple recipients
        
        Args:
            recipients: List of dicts with 'practice_id' and 'phone_number'
            message: Message content
            campaign_id: Optional campaign ID
            media_url: Optional media URL
            
        Returns:
            Dict with success count, failures, results
        """
        results = {
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'results': [],
            'campaign_id': campaign_id
        }
        
        for recipient in recipients:
            phone = recipient.get('phone_number')
            practice_id = recipient.get('practice_id')
            
            if not phone:
                results['failed'] += 1
                results['results'].append({
                    'practice_id': practice_id,
                    'success': False,
                    'error': 'missing_phone_number'
                })
                continue
            
            # Personalize message
            personalized_message = self._personalize_message(message, recipient)
            
            # Send WhatsApp
            result = self.send_message(
                to_number=phone,
                message=personalized_message,
                practice_id=practice_id,
                campaign_id=campaign_id,
                media_url=media_url
            )
            
            if result['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            results['results'].append(result)
        
        logger.info(f"Bulk WhatsApp sent: {results['sent']}/{results['total']} successful")
        return results
    
    def get_message_status(self, message_sid: str) -> Dict:
        """
        Get delivery status of a WhatsApp message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dict with status, delivery info
        """
        if not self.is_available():
            return {'error': 'WhatsApp service not configured'}
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'message_sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'date_updated': message.date_updated.isoformat() if message.date_updated else None,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'num_media': message.num_media
            }
        except TwilioRestException as e:
            logger.error(f"Error fetching WhatsApp message status: {e}")
            return {'error': str(e)}
    
    def get_message_history(
        self,
        phone_number: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get WhatsApp message history
        
        Args:
            phone_number: Optional filter by recipient
            limit: Max messages to return
            
        Returns:
            List of message dicts
        """
        if not self.is_available():
            return []
        
        try:
            # Filter WhatsApp messages only
            filters = {'limit': limit}
            
            if phone_number:
                to_whatsapp = self._format_whatsapp_number(phone_number)
                filters['to'] = to_whatsapp
            
            messages = self.client.messages.list(**filters)
            
            # Filter only WhatsApp messages
            whatsapp_messages = [
                msg for msg in messages
                if msg.from_.startswith('whatsapp:') or msg.to.startswith('whatsapp:')
            ]
            
            return [
                {
                    'message_sid': msg.sid,
                    'to': msg.to,
                    'from': msg.from_,
                    'body': msg.body,
                    'status': msg.status,
                    'direction': msg.direction,
                    'date_sent': msg.date_sent.isoformat() if msg.date_sent else None,
                    'num_media': msg.num_media
                }
                for msg in whatsapp_messages
            ]
        except Exception as e:
            logger.error(f"Error fetching WhatsApp history: {e}")
            return []
    
    def _format_whatsapp_number(self, phone: str) -> str:
        """
        Format phone number for WhatsApp
        
        Args:
            phone: Phone number
            
        Returns:
            WhatsApp formatted number (whatsapp:+32...)
        """
        # Already formatted
        if phone.startswith('whatsapp:'):
            return phone
        
        # Add country code if needed
        if not phone.startswith('+'):
            if phone.startswith('0'):
                phone = '+32' + phone[1:]
            else:
                phone = '+32' + phone
        
        # Clean
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        return f'whatsapp:{phone}'
    
    def _personalize_message(self, template: str, recipient: Dict) -> str:
        """
        Replace variables in message template
        
        Supported variables:
        - {naam} / {name}
        - {gemeente} / {city}
        - {praktijk} / {practice}
        - {email}
        """
        message = template
        
        replacements = {
            '{naam}': recipient.get('naam', recipient.get('name', '')),
            '{name}': recipient.get('naam', recipient.get('name', '')),
            '{gemeente}': recipient.get('gemeente', recipient.get('city', '')),
            '{city}': recipient.get('gemeente', recipient.get('city', '')),
            '{praktijk}': recipient.get('praktijk', recipient.get('practice', '')),
            '{practice}': recipient.get('praktijk', recipient.get('practice', '')),
            '{email}': recipient.get('email', '')
        }
        
        for var, value in replacements.items():
            message = message.replace(var, str(value))
        
        return message
    
    def validate_phone_number(self, phone: str) -> Dict:
        """
        Validate phone number for WhatsApp
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Dict with validation result
        """
        if not phone:
            return {'valid': False, 'error': 'empty_phone'}
        
        # Remove spaces, dashes, dots
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Check Belgian format
        if cleaned.startswith('+32'):
            if len(cleaned) == 12:
                formatted = self._format_whatsapp_number(cleaned)
                return {'valid': True, 'formatted': formatted}
        elif cleaned.startswith('0'):
            formatted = self._format_whatsapp_number('+32' + cleaned[1:])
            if len(formatted) == 22:  # whatsapp:+32 + 9 digits
                return {'valid': True, 'formatted': formatted}
        
        return {'valid': False, 'error': 'invalid_format'}


# WhatsApp Templates
# Note: In production, these must be approved by Facebook/Meta
WHATSAPP_TEMPLATES = {
    'introduction': {
        'name': 'Introductie',
        'content': 'Hallo {{1}}, wij zijn gespecialiseerd in het ondersteunen van huisartsenpraktijken. Interesse in een vrijblijvend gesprek? Groet, {{2}}',
        'category': 'marketing',
        'variables': ['naam', 'sender_name'],
        'status': 'approved',  # In dev: pending approval
        'language': 'nl'
    },
    'follow_up': {
        'name': 'Follow-up',
        'content': 'Beste {{1}}, ik stuurde je vorige week informatie over onze diensten. Heb je even tijd voor een korte call deze week? Groet, {{2}}',
        'category': 'marketing',
        'variables': ['naam', 'sender_name'],
        'status': 'approved',
        'language': 'nl'
    },
    'appointment_confirmation': {
        'name': 'Afspraak Bevestiging',
        'content': 'Hallo {{1}}, hierbij bevestig ik onze afspraak op {{2}} om {{3}}. Tot dan! Groet, {{4}}',
        'category': 'transactional',
        'variables': ['naam', 'datum', 'tijd', 'sender_name'],
        'status': 'approved',
        'language': 'nl'
    },
    'document_share': {
        'name': 'Document Delen',
        'content': 'Hallo {{1}}, zoals beloofd: hier is de informatie die je vroeg. Heb je vragen? Bel me gerust! Groet, {{2}}',
        'category': 'utility',
        'variables': ['naam', 'sender_name'],
        'status': 'approved',
        'language': 'nl',
        'supports_media': True
    },
    'thank_you': {
        'name': 'Bedankt',
        'content': 'Bedankt voor je tijd vandaag, {{1}}! Zoals beloofd stuur ik je alle info door. Heb je vragen? Laat het me weten! Groet, {{2}}',
        'category': 'transactional',
        'variables': ['naam', 'sender_name'],
        'status': 'approved',
        'language': 'nl'
    },
    'special_offer': {
        'name': 'Speciaal Aanbod',
        'content': 'Hallo {{1}}! 🎉 We hebben een exclusief aanbod voor praktijken in {{2}}. Interesse? Neem contact met ons op! Groet, {{3}}',
        'category': 'marketing',
        'variables': ['naam', 'gemeente', 'sender_name'],
        'status': 'approved',
        'language': 'nl'
    },
    'meeting_reminder': {
        'name': 'Meeting Reminder',
        'content': '⏰ Reminder: onze afspraak is morgen om {{1}}. Zie ik je dan! Groet, {{2}}',
        'category': 'transactional',
        'variables': ['tijd', 'sender_name'],
        'status': 'approved',
        'language': 'nl'
    }
}


def get_whatsapp_templates() -> Dict:
    """Get all WhatsApp templates"""
    return WHATSAPP_TEMPLATES


def get_whatsapp_template(template_name: str) -> Optional[Dict]:
    """Get specific WhatsApp template"""
    return WHATSAPP_TEMPLATES.get(template_name)


def get_approved_templates() -> Dict:
    """Get only approved WhatsApp templates"""
    return {
        name: template
        for name, template in WHATSAPP_TEMPLATES.items()
        if template.get('status') == 'approved'
    }
