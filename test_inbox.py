"""Test script for inbox service"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.inbox_service import InboxService

def test_inbox():
    print("🧪 Testing Inbox Service...")
    
    # Initialize service
    inbox = InboxService("data/test_inbox.db")
    print("✅ Inbox service initialized")
    
    # Add test message
    msg = inbox.add_message(
        practice_id=1,
        practice_name="Test Praktijk",
        channel="sms",
        direction="outbound",
        content="Test bericht via SMS",
        sender="You",
        recipient="+32123456789"
    )
    print(f"✅ Message added: {msg.id}")
    
    # Get conversations
    conversations = inbox.get_conversations()
    print(f"✅ Found {len(conversations)} conversations")
    
    if conversations:
        conv = conversations[0]
        print(f"   - {conv.practice_name} ({len(conv.channels)} channels)")
    
    # Get unread count
    unread = inbox.get_unread_count()
    print(f"✅ Unread count: {unread}")
    
    print("\n✨ All tests passed!")

if __name__ == "__main__":
    test_inbox()
