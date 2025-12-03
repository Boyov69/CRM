"""
SMS Service - Twilio Integration
Handles all SMS operations: sending, templates, tracking
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending and managing SMS messages via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not configured. SMS functionality disabled.")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info(f"Twilio SMS service initialized with number {self.from_number}")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if SMS service is available"""
        return self.client is not None
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        practice_id: Optional[int] = None,
        campaign_id: Optional[int] = None
    ) -> Dict:
        """
        Send a single SMS message
        
        Args:
            to_number: Recipient phone number (E.164 format: +32...)
            message: SMS content (max 160 chars for single SMS)
            practice_id: Optional practice ID for tracking
            campaign_id: Optional campaign ID for tracking
            
        Returns:
            Dict with status, message_sid, cost, etc.
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'SMS service not configured',
                'message': 'Twilio credentials missing'
            }
        
        # Validate phone number format
        if not to_number.startswith('+'):
            # Assume Belgian number if no country code
            if to_number.startswith('0'):
                to_number = '+32' + to_number[1:]
            else:
                to_number = '+32' + to_number
        
        # Clean phone number
        to_number = ''.join(c for c in to_number if c.isdigit() or c == '+')
        
        try:
            # Send SMS via Twilio
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            result = {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'to_number': to_number,
                'from_number': self.from_number,
                'message': message,
                'segments': self._calculate_segments(message),
                'direction': 'outbound',
                'practice_id': practice_id,
                'campaign_id': campaign_id,
                'sent_at': datetime.now().isoformat(),
                'cost': None  # Will be updated via webhook
            }
            
            logger.info(f"SMS sent successfully to {to_number}: {message_obj.sid}")
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {e}")
            return {
                'success': False,
                'error': 'twilio_error',
                'message': str(e),
                'code': e.code,
                'to_number': to_number
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return {
                'success': False,
                'error': 'unknown_error',
                'message': str(e)
            }
    
    def send_bulk_sms(
        self,
        recipients: List[Dict],
        message: str,
        campaign_id: Optional[int] = None
    ) -> Dict:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of dicts with 'practice_id' and 'phone_number'
            message: SMS content
            campaign_id: Optional campaign ID
            
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
            
            # Send SMS
            result = self.send_sms(
                to_number=phone,
                message=personalized_message,
                practice_id=practice_id,
                campaign_id=campaign_id
            )
            
            if result['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            results['results'].append(result)
        
        logger.info(f"Bulk SMS sent: {results['sent']}/{results['total']} successful")
        return results
    
    def get_message_status(self, message_sid: str) -> Dict:
        """
        Get delivery status of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dict with status, delivery info, cost
        """
        if not self.is_available():
            return {'error': 'SMS service not configured'}
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'message_sid': message.sid,
                'status': message.status,
                'to_number': message.to,
                'from_number': message.from_,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'date_updated': message.date_updated.isoformat() if message.date_updated else None,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'price': float(message.price) if message.price else None,
                'price_unit': message.price_unit,
                'num_segments': message.num_segments
            }
        except TwilioRestException as e:
            logger.error(f"Error fetching message status: {e}")
            return {'error': str(e)}
    
    def get_message_history(self, phone_number: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get SMS history, optionally filtered by phone number
        
        Args:
            phone_number: Optional filter by recipient
            limit: Max messages to return
            
        Returns:
            List of message dicts
        """
        if not self.is_available():
            return []
        
        try:
            if phone_number:
                # Normalize phone number
                if not phone_number.startswith('+'):
                    phone_number = '+32' + phone_number.lstrip('0')
                
                messages = self.client.messages.list(
                    to=phone_number,
                    limit=limit
                )
            else:
                messages = self.client.messages.list(limit=limit)
            
            return [
                {
                    'message_sid': msg.sid,
                    'to': msg.to,
                    'from': msg.from_,
                    'body': msg.body,
                    'status': msg.status,
                    'direction': msg.direction,
                    'date_sent': msg.date_sent.isoformat() if msg.date_sent else None,
                    'price': float(msg.price) if msg.price else None,
                    'num_segments': msg.num_segments
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error fetching message history: {e}")
            return []
    
    def _calculate_segments(self, message: str) -> int:
        """
        Calculate number of SMS segments
        SMS: 160 chars = 1 segment, 153 chars per segment after that
        """
        length = len(message)
        if length <= 160:
            return 1
        return (length - 160) // 153 + 2
    
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
        
        # Replace variables
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
        Validate and format phone number
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Dict with validation result and formatted number
        """
        # Basic validation
        if not phone:
            return {'valid': False, 'error': 'empty_phone'}
        
        # Remove spaces, dashes, dots
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Check format
        if cleaned.startswith('+32'):
            # Belgian format
            if len(cleaned) == 12:  # +32 + 9 digits
                return {'valid': True, 'formatted': cleaned}
            else:
                return {'valid': False, 'error': 'invalid_length'}
        elif cleaned.startswith('0'):
            # Local format, add +32
            formatted = '+32' + cleaned[1:]
            if len(formatted) == 12:
                return {'valid': True, 'formatted': formatted}
            else:
                return {'valid': False, 'error': 'invalid_length'}
        else:
            # Assume Belgian, add +32
            formatted = '+32' + cleaned
            if len(formatted) == 12:
                return {'valid': True, 'formatted': formatted}
            else:
                return {'valid': False, 'error': 'invalid_format'}
    
    def estimate_cost(self, message: str, recipients: int = 1) -> Dict:
        """
        Estimate cost of sending SMS
        
        Args:
            message: SMS content
            recipients: Number of recipients
            
        Returns:
            Dict with cost estimate
        """
        segments = self._calculate_segments(message)
        
        # Belgium SMS cost (approximate)
        COST_PER_SEGMENT = 0.0075  # €0.0075 per segment
        
        total_segments = segments * recipients
        total_cost = total_segments * COST_PER_SEGMENT
        
        return {
            'segments_per_message': segments,
            'total_recipients': recipients,
            'total_segments': total_segments,
            'cost_per_segment': COST_PER_SEGMENT,
            'total_cost': round(total_cost, 4),
            'currency': 'EUR'
        }


# SMS Templates
SMS_TEMPLATES = {
    'initial_contact': {
        'name': 'Initieel Contact',
        'content': 'Hallo {naam}, wij zijn gespecialiseerd in het ondersteunen van huisartsenpraktijken. Interesse in een gesprek? Groet, [Uw Naam]',
        'category': 'marketing',
        'variables': ['naam']
    },
    'follow_up': {
        'name': 'Follow-up',
        'content': 'Beste {naam}, ik stuurde je vorige week een email over onze diensten. Heb je even tijd voor een korte call? Groet, [Uw Naam]',
        'category': 'marketing',
        'variables': ['naam']
    },
    'meeting_reminder': {
        'name': 'Afspraak Herinnering',
        'content': 'Reminder: onze afspraak morgen om {tijd}. Tot dan! Groet, [Uw Naam]',
        'category': 'transactional',
        'variables': ['tijd']
    },
    'document_share': {
        'name': 'Document Delen',
        'content': 'Hallo {naam}, zoals beloofd: hier is de link naar het document: {link}. Groet, [Uw Naam]',
        'category': 'transactional',
        'variables': ['naam', 'link']
    },
    'thank_you': {
        'name': 'Bedankt',
        'content': 'Bedankt voor je tijd vandaag, {naam}! Ik stuur de info zo snel mogelijk door. Groet, [Uw Naam]',
        'category': 'transactional',
        'variables': ['naam']
    },
    'special_offer': {
        'name': 'Speciaal Aanbod',
        'content': 'Exclusief aanbod voor praktijken in {gemeente}: [details]. Interesse? Bel ons! Groet, [Uw Naam]',
        'category': 'marketing',
        'variables': ['gemeente']
    }
}


def get_templates() -> Dict:
    """Get all SMS templates"""
    return SMS_TEMPLATES


def get_template(template_id: str) -> Optional[Dict]:
    """Get specific SMS template"""
    return SMS_TEMPLATES.get(template_id)
