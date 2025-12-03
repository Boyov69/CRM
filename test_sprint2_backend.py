"""
Sprint 2 Backend Test Suite
Tests SMS, WhatsApp, and Inbox functionality
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_services():
    """Test backend services"""
    print("=" * 60)
    print("🧪 TESTING SPRINT 2 BACKEND SERVICES")
    print("=" * 60)
    
    # Test 1: SMS Service
    print("\n1️⃣ Testing SMS Service...")
    try:
        from backend.services.sms_service import SMSService, SMS_COST_PER_SEGMENT_EUR
        sms = SMSService()
        print(f"   ✅ SMS Service initialized")
        print(f"   ✅ Cost constant: €{SMS_COST_PER_SEGMENT_EUR} per segment")
        print(f"   ✅ Available: {sms.is_available()}")
        
        # Test cost estimation
        result = sms.estimate_cost("Test message", recipients=1)
        print(f"   ✅ Cost estimation: {result}")
    except Exception as e:
        print(f"   ❌ SMS Service failed: {e}")
    
    # Test 2: WhatsApp Service
    print("\n2️⃣ Testing WhatsApp Service...")
    try:
        from backend.services.whatsapp_service import WhatsAppService
        whatsapp = WhatsAppService()
        print(f"   ✅ WhatsApp Service initialized")
        print(f"   ✅ Available: {whatsapp.is_available()}")
    except Exception as e:
        print(f"   ❌ WhatsApp Service failed: {e}")
    
    # Test 3: Inbox Service
    print("\n3️⃣ Testing Inbox Service...")
    try:
        from backend.services.inbox_service import InboxService
        inbox = InboxService("data/test_sprint2.db")
        print(f"   ✅ Inbox Service initialized")
        
        # Add test message
        msg = inbox.add_message(
            practice_id=1,
            practice_name="Test Praktijk",
            channel="sms",
            direction="outbound",
            content="Sprint 2 test bericht",
            sender="System",
            recipient="+32471234567"
        )
        print(f"   ✅ Message added: {msg.id}")
        
        # Get conversations
        convs = inbox.get_conversations()
        print(f"   ✅ Conversations: {len(convs)}")
        
        # Get unread count
        unread = inbox.get_unread_count()
        print(f"   ✅ Unread count: {unread}")
    except Exception as e:
        print(f"   ❌ Inbox Service failed: {e}")
    
    # Test 4: Message Models
    print("\n4️⃣ Testing Message Models...")
    try:
        from backend.models.message import Message, Conversation
        from datetime import datetime
        
        msg = Message(
            id="test_msg_1",
            conversation_id="conv_1",
            practice_id=1,
            channel="sms",
            direction="outbound",
            content="Test",
            sender="System",
            recipient="+32471234567",
            timestamp=datetime.now()
        )
        print(f"   ✅ Message model created: {msg.id}")
        
        msg_dict = msg.to_dict()
        print(f"   ✅ Message to_dict(): {len(msg_dict)} fields")
    except Exception as e:
        print(f"   ❌ Message Models failed: {e}")
    
    print("\n" + "=" * 60)
    print("✨ BACKEND SERVICES TEST COMPLETE")
    print("=" * 60)


def test_api_structure():
    """Test API blueprints structure"""
    print("\n" + "=" * 60)
    print("🧪 TESTING API BLUEPRINTS")
    print("=" * 60)
    
    # We'll test without importing (to avoid dependencies)
    import os
    
    print("\n📁 Checking API files...")
    api_files = [
        'backend/api/sms_api.py',
        'backend/api/whatsapp_api.py',
        'backend/api/inbox_api.py'
    ]
    
    for file in api_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size} bytes)")
        else:
            print(f"   ❌ {file} not found")
    
    print("\n" + "=" * 60)
    print("✨ API STRUCTURE TEST COMPLETE")
    print("=" * 60)


def test_phone_normalization():
    """Test phone number normalization"""
    print("\n" + "=" * 60)
    print("🧪 TESTING PHONE NORMALIZATION")
    print("=" * 60)
    
    try:
        from backend.api.sms_api import normalize_phone_number
        
        test_cases = [
            ("0471234567", "+32471234567"),
            ("+32471234567", "+32471234567"),
            ("471234567", "+32471234567"),
            ("", ""),
        ]
        
        print("\n📞 Testing normalization...")
        for input_num, expected in test_cases:
            result = normalize_phone_number(input_num)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{input_num}' → '{result}' (expected: '{expected}')")
    
    except Exception as e:
        print(f"   ❌ Phone normalization failed: {e}")
    
    print("\n" + "=" * 60)
    print("✨ PHONE NORMALIZATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_services()
    test_api_structure()
    test_phone_normalization()
    
    print("\n🎉 ALL TESTS COMPLETE! 🎉\n")
