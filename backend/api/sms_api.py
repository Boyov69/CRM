"""
SMS API Endpoints
Handles SMS sending, templates, and history
"""
from flask import Blueprint, jsonify, request
import logging
from datetime import datetime

from backend.services.sms_service import SMSService, get_templates, get_template
from backend.services.database import DatabaseService

logger = logging.getLogger(__name__)

sms_bp = Blueprint('sms', __name__)
sms_service = SMSService()
db = DatabaseService()


def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to E.164 format for matching"""
    if not phone:
        return ""
    
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # If no country code, assume Belgian number
    if not cleaned.startswith('+'):
        if cleaned.startswith('0'):
            cleaned = '+32' + cleaned[1:]
        else:
            cleaned = '+32' + cleaned
    
    return cleaned


@sms_bp.route('/sms/status', methods=['GET'])
def sms_status():
    """Check if SMS service is available"""
    return jsonify({
        'available': sms_service.is_available(),
        'from_number': sms_service.from_number if sms_service.is_available() else None
    })


@sms_bp.route('/sms/send', methods=['POST'])
def send_sms():
    """
    Send a single SMS
    
    Body:
    {
        "to_number": "+32123456789",
        "message": "Hello!",
        "practice_id": 1,  # optional
        "campaign_id": 1   # optional
    }
    """
    data = request.json
    
    to_number = data.get('to_number')
    message = data.get('message')
    practice_id = data.get('practice_id')
    campaign_id = data.get('campaign_id')
    
    if not to_number or not message:
        return jsonify({'error': 'to_number and message are required'}), 400
    
    # Send SMS
    result = sms_service.send_sms(
        to_number=to_number,
        message=message,
        practice_id=practice_id,
        campaign_id=campaign_id
    )
    
    if result['success']:
        # Save to practice history
        if practice_id:
            practice = db.get_practice(practice_id)
            if practice:
                if 'communication_history' not in practice:
                    practice['communication_history'] = []
                
                practice['communication_history'].append({
                    'type': 'sms',
                    'direction': 'outbound',
                    'message': message,
                    'to': to_number,
                    'message_sid': result['message_sid'],
                    'status': result['status'],
                    'sent_at': result['sent_at']
                })
                
                db.upsert_practice(practice)
        
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@sms_bp.route('/sms/bulk', methods=['POST'])
def send_bulk_sms():
    """
    Send SMS to multiple recipients
    
    Body:
    {
        "recipients": [
            {"practice_id": 1, "phone_number": "+32123456789", "naam": "Dr. Smith"},
            {"practice_id": 2, "phone_number": "+32987654321", "naam": "Dr. Jones"}
        ],
        "message": "Hallo {naam}!",
        "campaign_id": 1  # optional
    }
    """
    data = request.json
    
    recipients = data.get('recipients', [])
    message = data.get('message')
    campaign_id = data.get('campaign_id')
    
    if not recipients or not message:
        return jsonify({'error': 'recipients and message are required'}), 400
    
    # Send bulk SMS
    result = sms_service.send_bulk_sms(
        recipients=recipients,
        message=message,
        campaign_id=campaign_id
    )
    
    # Update practices with communication history
    for sms_result in result['results']:
        if sms_result.get('success') and sms_result.get('practice_id'):
            practice = db.get_practice(sms_result['practice_id'])
            if practice:
                if 'communication_history' not in practice:
                    practice['communication_history'] = []
                
                practice['communication_history'].append({
                    'type': 'sms',
                    'direction': 'outbound',
                    'message': sms_result['message'],
                    'to': sms_result['to_number'],
                    'message_sid': sms_result['message_sid'],
                    'status': sms_result['status'],
                    'sent_at': sms_result['sent_at'],
                    'campaign_id': campaign_id
                })
                
                db.upsert_practice(practice)
    
    return jsonify(result), 200


@sms_bp.route('/sms/history/<int:practice_id>', methods=['GET'])
def get_sms_history(practice_id):
    """Get SMS history for a specific practice"""
    practice = db.get_practice(practice_id)
    
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404
    
    # Filter SMS from communication history
    sms_history = [
        msg for msg in practice.get('communication_history', [])
        if msg.get('type') == 'sms'
    ]
    
    # Sort by date (newest first)
    sms_history.sort(key=lambda x: x.get('sent_at', ''), reverse=True)
    
    return jsonify({
        'practice_id': practice_id,
        'practice_name': practice.get('naam'),
        'phone_number': practice.get('tel'),
        'total_sms': len(sms_history),
        'history': sms_history
    })


@sms_bp.route('/sms/history', methods=['GET'])
def get_all_sms_history():
    """Get all SMS history across all practices"""
    phone_number = request.args.get('phone_number')
    limit = int(request.args.get('limit', 50))
    
    # Fetch from Twilio
    history = sms_service.get_message_history(phone_number=phone_number, limit=limit)
    
    return jsonify({
        'total': len(history),
        'history': history
    })


@sms_bp.route('/sms/status/<message_sid>', methods=['GET'])
def get_message_status(message_sid):
    """Get delivery status of a specific message"""
    status = sms_service.get_message_status(message_sid)
    return jsonify(status)


@sms_bp.route('/sms/templates', methods=['GET'])
def get_sms_templates():
    """Get all SMS templates"""
    templates = get_templates()
    return jsonify({
        'total': len(templates),
        'templates': templates
    })


@sms_bp.route('/sms/templates/<template_id>', methods=['GET'])
def get_sms_template(template_id):
    """Get a specific SMS template"""
    template = get_template(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify(template)


@sms_bp.route('/sms/validate-phone', methods=['POST'])
def validate_phone():
    """
    Validate and format phone number
    
    Body:
    {
        "phone_number": "0123456789"
    }
    """
    data = request.json
    phone = data.get('phone_number')
    
    if not phone:
        return jsonify({'error': 'phone_number is required'}), 400
    
    result = sms_service.validate_phone_number(phone)
    return jsonify(result)


@sms_bp.route('/sms/estimate-cost', methods=['POST'])
def estimate_cost():
    """
    Estimate SMS cost
    
    Body:
    {
        "message": "Your message here",
        "recipients": 100
    }
    """
    data = request.json
    message = data.get('message', '')
    recipients = data.get('recipients', 1)
    
    estimate = sms_service.estimate_cost(message, recipients)
    return jsonify(estimate)


@sms_bp.route('/sms/webhook', methods=['POST'])
def sms_webhook():
    """
    Twilio webhook for SMS status updates and incoming messages
    
    Twilio sends POST requests with status updates
    """
    # Get Twilio data
    message_sid = request.form.get('MessageSid')
    message_status = request.form.get('MessageStatus')
    from_number = request.form.get('From')
    to_number = request.form.get('To')
    body = request.form.get('Body')
    
    logger.info(f"SMS webhook: {message_sid} - {message_status}")
    
    # Handle incoming SMS (replies)
    if body and from_number:
        # This is an incoming message (reply)
        logger.info(f"Incoming SMS from {from_number}: {body}")
        
        # Normalize the incoming phone number for matching
        normalized_from = normalize_phone_number(from_number)
        
        # Find practice by phone number
        practices = db.get_practices()
        practice = next(
            (p for p in practices 
             if normalize_phone_number(p.get('tel', '')) == normalized_from),
            None
        )
        
        if practice:
            # Add to communication history
            if 'communication_history' not in practice:
                practice['communication_history'] = []
            
            practice['communication_history'].append({
                'type': 'sms',
                'direction': 'inbound',
                'message': body,
                'from': from_number,
                'to': to_number,
                'message_sid': message_sid,
                'received_at': datetime.now().isoformat()
            })
            
            # Mark as replied in workflow
            if 'workflow' not in practice:
                practice['workflow'] = {}
            
            practice['workflow']['sms_replied'] = True
            practice['workflow']['last_sms_reply'] = datetime.now().isoformat()
            
            db.upsert_practice(practice)
            
            # TODO: Trigger automation (e.g., notify sales team)
    
    # Handle status updates (delivered, failed, etc.)
    elif message_status:
        # Update message status in database
        # This could update the communication_history entry
        logger.info(f"SMS status update: {message_sid} -> {message_status}")
        
        # TODO: Update practice communication history with new status
    
    return '', 200  # Twilio expects 200 OK
