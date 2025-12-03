"""
WhatsApp API Endpoints
Handles WhatsApp messaging, templates, and history
"""
from flask import Blueprint, jsonify, request
import logging
from datetime import datetime

from backend.services.whatsapp_service import (
    WhatsAppService,
    get_whatsapp_templates,
    get_whatsapp_template,
    get_approved_templates
)
from backend.services.database import DatabaseService

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)
whatsapp_service = WhatsAppService()
db = DatabaseService()


@whatsapp_bp.route('/whatsapp/status', methods=['GET'])
def whatsapp_status():
    """Check if WhatsApp service is available"""
    return jsonify({
        'available': whatsapp_service.is_available(),
        'whatsapp_number': whatsapp_service.whatsapp_number if whatsapp_service.is_available() else None,
        'mode': 'sandbox' if 'sandbox' in whatsapp_service.whatsapp_number.lower() else 'production'
    })


@whatsapp_bp.route('/whatsapp/send', methods=['POST'])
def send_whatsapp():
    """
    Send a WhatsApp message
    
    Body:
    {
        "to_number": "+32123456789",
        "message": "Hello!",
        "practice_id": 1,       # optional
        "campaign_id": 1,       # optional
        "media_url": "https://..." # optional
    }
    """
    data = request.json
    
    to_number = data.get('to_number')
    message = data.get('message')
    practice_id = data.get('practice_id')
    campaign_id = data.get('campaign_id')
    media_url = data.get('media_url')
    
    if not to_number or not message:
        return jsonify({'error': 'to_number and message are required'}), 400
    
    # Send WhatsApp message
    result = whatsapp_service.send_message(
        to_number=to_number,
        message=message,
        practice_id=practice_id,
        campaign_id=campaign_id,
        media_url=media_url
    )
    
    if result['success']:
        # Save to practice history
        if practice_id:
            practice = db.get_practice(practice_id)
            if practice:
                if 'communication_history' not in practice:
                    practice['communication_history'] = []
                
                practice['communication_history'].append({
                    'type': 'whatsapp',
                    'direction': 'outbound',
                    'message': message,
                    'to': to_number,
                    'message_sid': result['message_sid'],
                    'status': result['status'],
                    'media_url': media_url,
                    'sent_at': result['sent_at']
                })
                
                db.upsert_practice(practice)
        
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@whatsapp_bp.route('/whatsapp/send-template', methods=['POST'])
def send_template():
    """
    Send a WhatsApp template message
    
    Body:
    {
        "to_number": "+32123456789",
        "template_name": "introduction",
        "template_params": ["Dr. Smith", "John"],
        "practice_id": 1,
        "campaign_id": 1
    }
    """
    data = request.json
    
    to_number = data.get('to_number')
    template_name = data.get('template_name')
    template_params = data.get('template_params', [])
    practice_id = data.get('practice_id')
    campaign_id = data.get('campaign_id')
    
    if not to_number or not template_name:
        return jsonify({'error': 'to_number and template_name are required'}), 400
    
    # Send template message
    result = whatsapp_service.send_template_message(
        to_number=to_number,
        template_name=template_name,
        template_params=template_params,
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
                    'type': 'whatsapp',
                    'direction': 'outbound',
                    'template': template_name,
                    'message': result['message'],
                    'to': to_number,
                    'message_sid': result['message_sid'],
                    'status': result['status'],
                    'sent_at': result['sent_at']
                })
                
                db.upsert_practice(practice)
        
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@whatsapp_bp.route('/whatsapp/bulk', methods=['POST'])
def send_bulk_whatsapp():
    """
    Send WhatsApp messages to multiple recipients
    
    Body:
    {
        "recipients": [
            {"practice_id": 1, "phone_number": "+32123456789", "naam": "Dr. Smith"},
            {"practice_id": 2, "phone_number": "+32987654321", "naam": "Dr. Jones"}
        ],
        "message": "Hallo {naam}!",
        "campaign_id": 1,
        "media_url": "https://..."  # optional
    }
    """
    data = request.json
    
    recipients = data.get('recipients', [])
    message = data.get('message')
    campaign_id = data.get('campaign_id')
    media_url = data.get('media_url')
    
    if not recipients or not message:
        return jsonify({'error': 'recipients and message are required'}), 400
    
    # Send bulk WhatsApp
    result = whatsapp_service.send_bulk_whatsapp(
        recipients=recipients,
        message=message,
        campaign_id=campaign_id,
        media_url=media_url
    )
    
    # Update practices with communication history
    for wa_result in result['results']:
        if wa_result.get('success') and wa_result.get('practice_id'):
            practice = db.get_practice(wa_result['practice_id'])
            if practice:
                if 'communication_history' not in practice:
                    practice['communication_history'] = []
                
                practice['communication_history'].append({
                    'type': 'whatsapp',
                    'direction': 'outbound',
                    'message': wa_result['message'],
                    'to': wa_result['to_number'],
                    'message_sid': wa_result['message_sid'],
                    'status': wa_result['status'],
                    'media_url': media_url,
                    'sent_at': wa_result['sent_at'],
                    'campaign_id': campaign_id
                })
                
                db.upsert_practice(practice)
    
    return jsonify(result), 200


@whatsapp_bp.route('/whatsapp/history/<int:practice_id>', methods=['GET'])
def get_whatsapp_history(practice_id):
    """Get WhatsApp history for a specific practice"""
    practice = db.get_practice(practice_id)
    
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404
    
    # Filter WhatsApp from communication history
    whatsapp_history = [
        msg for msg in practice.get('communication_history', [])
        if msg.get('type') == 'whatsapp'
    ]
    
    # Sort by date (newest first)
    whatsapp_history.sort(key=lambda x: x.get('sent_at', ''), reverse=True)
    
    return jsonify({
        'practice_id': practice_id,
        'practice_name': practice.get('naam'),
        'phone_number': practice.get('tel'),
        'total_messages': len(whatsapp_history),
        'history': whatsapp_history
    })


@whatsapp_bp.route('/whatsapp/history', methods=['GET'])
def get_all_whatsapp_history():
    """Get all WhatsApp history across all practices"""
    phone_number = request.args.get('phone_number')
    limit = int(request.args.get('limit', 50))
    
    # Fetch from Twilio
    history = whatsapp_service.get_message_history(phone_number=phone_number, limit=limit)
    
    return jsonify({
        'total': len(history),
        'history': history
    })


@whatsapp_bp.route('/whatsapp/status/<message_sid>', methods=['GET'])
def get_message_status(message_sid):
    """Get delivery status of a specific WhatsApp message"""
    status = whatsapp_service.get_message_status(message_sid)
    return jsonify(status)


@whatsapp_bp.route('/whatsapp/templates', methods=['GET'])
def get_templates():
    """Get all WhatsApp templates"""
    approved_only = request.args.get('approved_only', 'false').lower() == 'true'
    
    if approved_only:
        templates = get_approved_templates()
    else:
        templates = get_whatsapp_templates()
    
    return jsonify({
        'total': len(templates),
        'templates': templates
    })


@whatsapp_bp.route('/whatsapp/templates/<template_name>', methods=['GET'])
def get_template(template_name):
    """Get a specific WhatsApp template"""
    template = get_whatsapp_template(template_name)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify(template)


@whatsapp_bp.route('/whatsapp/validate-phone', methods=['POST'])
def validate_phone():
    """
    Validate and format phone number for WhatsApp
    
    Body:
    {
        "phone_number": "0123456789"
    }
    """
    data = request.json
    phone = data.get('phone_number')
    
    if not phone:
        return jsonify({'error': 'phone_number is required'}), 400
    
    result = whatsapp_service.validate_phone_number(phone)
    return jsonify(result)


@whatsapp_bp.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Twilio webhook for WhatsApp status updates and incoming messages
    
    Twilio sends POST requests with status updates and incoming messages
    """
    # Get Twilio data
    message_sid = request.form.get('MessageSid')
    message_status = request.form.get('MessageStatus')
    from_number = request.form.get('From')
    to_number = request.form.get('To')
    body = request.form.get('Body')
    num_media = int(request.form.get('NumMedia', 0))
    
    logger.info(f"WhatsApp webhook: {message_sid} - {message_status}")
    
    # Handle incoming WhatsApp message (reply)
    if body and from_number and from_number.startswith('whatsapp:'):
        logger.info(f"Incoming WhatsApp from {from_number}: {body}")
        
        # Extract phone number
        phone = from_number.replace('whatsapp:', '')
        
        # Find practice by phone number
        practices = db.get_practices()
        practice = next((p for p in practices if p.get('tel') in phone or phone in str(p.get('tel', ''))), None)
        
        if practice:
            # Add to communication history
            if 'communication_history' not in practice:
                practice['communication_history'] = []
            
            message_data = {
                'type': 'whatsapp',
                'direction': 'inbound',
                'message': body,
                'from': from_number,
                'to': to_number,
                'message_sid': message_sid,
                'received_at': datetime.now().isoformat()
            }
            
            # Handle media attachments
            if num_media > 0:
                media_urls = []
                for i in range(num_media):
                    media_url = request.form.get(f'MediaUrl{i}')
                    media_type = request.form.get(f'MediaContentType{i}')
                    if media_url:
                        media_urls.append({
                            'url': media_url,
                            'type': media_type
                        })
                message_data['media'] = media_urls
            
            practice['communication_history'].append(message_data)
            
            # Mark as replied in workflow
            if 'workflow' not in practice:
                practice['workflow'] = {}
            
            practice['workflow']['whatsapp_replied'] = True
            practice['workflow']['last_whatsapp_reply'] = datetime.now().isoformat()
            
            db.upsert_practice(practice)
            
            # TODO: Trigger automation (e.g., notify sales team)
            logger.info(f"Saved incoming WhatsApp from practice {practice.get('id')}: {practice.get('naam')}")
    
    # Handle status updates (delivered, read, failed, etc.)
    elif message_status:
        logger.info(f"WhatsApp status update: {message_sid} -> {message_status}")
        
        # Status values: queued, sending, sent, delivered, read, failed, undelivered
        # Update practice communication history with new status
        # TODO: Implement status tracking in database
    
    return '', 200  # Twilio expects 200 OK


@whatsapp_bp.route('/whatsapp/sandbox-instructions', methods=['GET'])
def sandbox_instructions():
    """Get instructions for WhatsApp Sandbox setup"""
    return jsonify({
        'sandbox': True,
        'instructions': {
            'step_1': 'Go to Twilio Console > Messaging > Try it out > Send a WhatsApp message',
            'step_2': 'Scan QR code or send "join <your-sandbox-keyword>" to the sandbox number',
            'step_3': f'Sandbox number: {whatsapp_service.whatsapp_number}',
            'step_4': 'Once connected, you can send/receive messages via API',
            'note': 'Sandbox is for testing only. For production, apply for WhatsApp Business API approval.'
        },
        'sandbox_number': whatsapp_service.whatsapp_number,
        'production_note': 'To go live: Apply for WhatsApp Business API through Twilio (requires Facebook Business Manager)'
    })
