"""
Inbox API Endpoints
Unified inbox voor Email, SMS en WhatsApp
"""
import logging
from flask import Blueprint, request, jsonify
from backend.services.inbox_service import InboxService
from backend.services.database import get_practice_by_id

logger = logging.getLogger(__name__)

inbox_bp = Blueprint('inbox', __name__)
inbox_service = InboxService()


@inbox_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations
    
    Query params:
    - limit: number of conversations (default 50)
    - offset: pagination offset (default 0)
    - unread_only: only unread conversations (default false)
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        conversations = inbox_service.get_conversations(
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        return jsonify({
            'success': True,
            'conversations': [c.to_dict() for c in conversations],
            'count': len(conversations),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get single conversation met alle berichten"""
    try:
        conversation = inbox_service.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/conversation/<conversation_id>/mark-read', methods=['PUT'])
def mark_conversation_read(conversation_id):
    """Mark conversation als gelezen"""
    try:
        success = inbox_service.mark_as_read(conversation_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Could not mark as read'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Conversation marked as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking conversation as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get totaal aantal ongelezen berichten"""
    try:
        count = inbox_service.get_unread_count()
        
        return jsonify({
            'success': True,
            'unread_count': count
        })
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/reply', methods=['POST'])
def send_reply():
    """Send reply via specified channel
    
    Body:
    {
        "conversation_id": "conv_123",
        "practice_id": 1,
        "channel": "sms",  // or "whatsapp", "email"
        "content": "Bedankt voor je bericht!",
        "attachments": []  // optional
    }
    """
    try:
        data = request.json
        
        conversation_id = data.get('conversation_id')
        practice_id = data.get('practice_id')
        channel = data.get('channel')
        content = data.get('content')
        attachments = data.get('attachments', [])
        
        if not all([conversation_id, practice_id, channel, content]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Get practice info
        practice = get_practice_by_id(practice_id)
        if not practice:
            return jsonify({
                'success': False,
                'error': 'Practice not found'
            }), 404
        
        # Send via appropriate channel
        if channel == 'sms':
            from backend.services.sms_service import SMSService
            sms_service = SMSService()
            
            result = sms_service.send_sms(
                to_number=practice.get('phone'),
                message=content
            )
            
            if not result.get('success'):
                return jsonify(result), 500
            
            # Add to inbox
            message = inbox_service.add_message(
                practice_id=practice_id,
                practice_name=practice.get('name', ''),
                channel='sms',
                direction='outbound',
                content=content,
                sender='You',
                recipient=practice.get('phone', ''),
                message_id=result.get('message_id'),
                status='sent'
            )
            
        elif channel == 'whatsapp':
            from backend.services.whatsapp_service import WhatsAppService
            whatsapp_service = WhatsAppService()
            
            phone = practice.get('phone', '').replace('+', '').replace(' ', '')
            
            if attachments:
                result = whatsapp_service.send_media_message(
                    to_number=phone,
                    media_url=attachments[0],
                    caption=content
                )
            else:
                # For now, send as freeform (in production use templates)
                result = whatsapp_service.send_template_message(
                    to_number=phone,
                    template_name='hello_world'
                )
            
            if not result.get('success'):
                return jsonify(result), 500
            
            # Add to inbox
            message = inbox_service.add_message(
                practice_id=practice_id,
                practice_name=practice.get('name', ''),
                channel='whatsapp',
                direction='outbound',
                content=content,
                sender='You',
                recipient=phone,
                message_id=result.get('message_id'),
                status='sent',
                attachments=attachments
            )
            
        elif channel == 'email':
            from backend.services.email_service import EmailService
            email_service = EmailService()
            
            result = email_service.send_email(
                to_email=practice.get('email'),
                subject='Re: Uw bericht',
                body=content
            )
            
            if not result.get('success'):
                return jsonify(result), 500
            
            # Add to inbox
            message = inbox_service.add_message(
                practice_id=practice_id,
                practice_name=practice.get('name', ''),
                channel='email',
                direction='outbound',
                content=content,
                sender='You',
                recipient=practice.get('email', ''),
                status='sent'
            )
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported channel: {channel}'
            }), 400
        
        return jsonify({
            'success': True,
            'message': message.to_dict(),
            'channel': channel
        })
        
    except Exception as e:
        logger.error(f"Error sending reply: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/search', methods=['GET'])
def search_messages():
    """Search messages
    
    Query params:
    - q: search query
    - channel: filter by channel (optional)
    - practice_id: filter by practice (optional)
    """
    try:
        query = request.args.get('q', '')
        channel = request.args.get('channel')
        practice_id = request.args.get('practice_id', type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        messages = inbox_service.search_messages(
            query=query,
            channel=channel,
            practice_id=practice_id
        )
        
        return jsonify({
            'success': True,
            'messages': [m.to_dict() for m in messages],
            'count': len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/webhook/sms', methods=['POST'])
def sms_webhook():
    """Webhook voor inbound SMS berichten"""
    try:
        data = request.form.to_dict()
        
        from_number = data.get('From', '')
        message_body = data.get('Body', '')
        message_sid = data.get('MessageSid', '')
        
        # Find practice by phone number
        # TODO: implement phone lookup
        practice_id = 1  # Placeholder
        practice_name = "Practice"
        
        # Add to inbox
        inbox_service.add_message(
            practice_id=practice_id,
            practice_name=practice_name,
            channel='sms',
            direction='inbound',
            content=message_body,
            sender=from_number,
            recipient='You',
            message_id=message_sid,
            status='received'
        )
        
        logger.info(f"✅ Inbound SMS received from {from_number}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@inbox_bp.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook voor inbound WhatsApp berichten"""
    try:
        data = request.form.to_dict()
        
        from_number = data.get('From', '').replace('whatsapp:', '')
        message_body = data.get('Body', '')
        message_sid = data.get('MessageSid', '')
        
        # Find practice by phone number
        # TODO: implement phone lookup
        practice_id = 1  # Placeholder
        practice_name = "Practice"
        
        # Add to inbox
        inbox_service.add_message(
            practice_id=practice_id,
            practice_name=practice_name,
            channel='whatsapp',
            direction='inbound',
            content=message_body,
            sender=from_number,
            recipient='You',
            message_id=message_sid,
            status='received'
        )
        
        logger.info(f"✅ Inbound WhatsApp received from {from_number}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
