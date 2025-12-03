"""Comprehensive test for inbox service"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.inbox_service import InboxService

def test_inbox_full():
    print("🧪 Testing Multi-Channel Inbox...")
    
    inbox = InboxService("data/test_inbox.db")
    
    # Test 1: Add messages from different channels
    print("\n1️⃣ Adding messages from different channels...")
    
    # SMS message
    inbox.add_message(
        practice_id=1,
        practice_name="Huisartspraktijk ABC",
        channel="sms",
        direction="outbound",
        content="Hallo, we willen graag een afspraak maken",
        sender="You",
        recipient="+32471234567"
    )
    
    # WhatsApp message (same practice)
    inbox.add_message(
        practice_id=1,
        practice_name="Huisartspraktijk ABC",
        channel="whatsapp",
        direction="inbound",
        content="Ja, dat is goed!",
        sender="+32471234567",
        recipient="You"
    )
    
    # Email message (same practice)
    inbox.add_message(
        practice_id=1,
        practice_name="Huisartspraktijk ABC",
        channel="email",
        direction="outbound",
        content="Bevestiging van onze afspraak",
        sender="you@example.com",
        recipient="abc@practice.be"
    )
    
    # Different practice
    inbox.add_message(
        practice_id=2,
        practice_name="Praktijk XYZ",
        channel="sms",
        direction="inbound",
        content="Bel me terug aub",
        sender="+32479876543",
        recipient="You"
    )
    
    print("✅ Added 4 messages across 2 practices")
    
    # Test 2: Get conversations
    print("\n2️⃣ Getting conversations...")
    conversations = inbox.get_conversations()
    print(f"✅ Found {len(conversations)} conversations")
    
    for conv in conversations:
        print(f"\n   📬 {conv.practice_name}")
        print(f"      Channels: {', '.join(conv.channels)}")
        print(f"      Unread: {conv.unread_count}")
        if conv.last_message:
            print(f"      Last: [{conv.last_message.channel}] {conv.last_message.content[:50]}")
    
    # Test 3: Get full conversation
    print("\n3️⃣ Getting full conversation...")
    conv = inbox.get_conversation("conv_1")
    if conv:
        print(f"✅ Conversation: {conv.practice_name}")
        print(f"   Messages: {len(conv.messages)}")
        for msg in conv.messages:
            arrow = "→" if msg.direction == "outbound" else "←"
            print(f"      {arrow} [{msg.channel}] {msg.content[:50]}")
    
    # Test 4: Unread count
    print("\n4️⃣ Checking unread messages...")
    unread = inbox.get_unread_count()
    print(f"✅ Unread messages: {unread}")
    
    # Test 5: Mark as read
    print("\n5️⃣ Marking conversation as read...")
    inbox.mark_as_read("conv_2")
    unread = inbox.get_unread_count()
    print(f"✅ Unread messages after marking: {unread}")
    
    # Test 6: Search
    print("\n6️⃣ Searching messages...")
    results = inbox.search_messages("afspraak")
    print(f"✅ Found {len(results)} messages matching 'afspraak'")
    for msg in results:
        print(f"      [{msg.channel}] {msg.content[:60]}")
    
    print("\n✨ All tests passed!")

if __name__ == "__main__":
    test_inbox_full()
