"""Voice API endpoints"""
from flask import Blueprint, jsonify, request, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.rest import Client
import logging
import os

from backend.config import Config
from backend.services.voice_service import VoiceService

voice_bp = Blueprint('voice', __name__)
logger = logging.getLogger(__name__)

# Initialize Twilio Client
twilio_client = None
if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
    twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

voice_service = VoiceService()

@voice_bp.route('/call', methods=['POST'])
def make_call():
    """Initiate an outbound call"""
    to_number = request.json.get('to')
    practice_id = request.json.get('practice_id')
    
    if not to_number:
        return jsonify({"error": "Phone number required"}), 400
        
    try:
        # Determine the host for the WebSocket connection
        # Important: This must be publicly accessible (e.g. ngrok)
        host = request.host
        
        call = twilio_client.calls.create(
            to=to_number,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            url=f"https://{host}/api/voice/twiml"
        )
        
        return jsonify({
            "status": "initiated",
            "call_sid": call.sid
        })
    except Exception as e:
        logger.error(f"Call initiation error: {e}")
        return jsonify({"error": str(e)}), 500

@voice_bp.route('/twiml', methods=['POST'])
def voice_twiml():
    """Return TwiML instructions for the call"""
    response = VoiceResponse()
    
    # 1. Speak a greeting
    response.say("Connecting you to ZorgCore AI Assistant.")
    
    # 2. Connect to WebSocket Stream
    # Uses request.host to determine dynamic ngrok URL
    host = request.host
    connect = Connect()
    stream = Stream(url=f"wss://{host}/api/voice/stream")
    connect.append(stream)
    response.append(connect)
    
    return Response(str(response), mimetype='text/xml')

# Note: The WebSocket endpoint is registered in app.py using sock.route
