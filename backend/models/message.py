"""
Message model voor unified inbox
Ondersteunt Email, SMS en WhatsApp berichten
"""
from datetime import datetime
from typing import Optional, Dict, Any

class Message:
    """Unified message model voor alle communicatie channels"""
    
    def __init__(
        self,
        id: str,
        conversation_id: str,
        practice_id: int,
        channel: str,
        direction: str,
        content: str,
        sender: str,
        recipient: str,
        timestamp: datetime,
        status: str = 'sent',
        metadata: Optional[Dict[str, Any]] = None,
        read: bool = False,
        attachments: Optional[list] = None
    ):
        self.id = id
        self.conversation_id = conversation_id
        self.practice_id = practice_id
        self.channel = channel
        self.direction = direction
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp
        self.status = status
        self.metadata = metadata or {}
        self.read = read
        self.attachments = attachments or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary voor API responses"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'practice_id': self.practice_id,
            'channel': self.channel,
            'direction': self.direction,
            'content': self.content,
            'sender': self.sender,
            'recipient': self.recipient,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'metadata': self.metadata,
            'read': self.read,
            'attachments': self.attachments
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp']
        return Message(**data)


class Conversation:
    """Conversation aggregates messages per practice"""
    
    def __init__(
        self,
        id: str,
        practice_id: int,
        practice_name: str,
        channels: list,
        last_message: Optional[Message] = None,
        unread_count: int = 0,
        messages: Optional[list] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.practice_id = practice_id
        self.practice_name = practice_name
        self.channels = channels
        self.last_message = last_message
        self.unread_count = unread_count
        self.messages = messages or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'practice_id': self.practice_id,
            'practice_name': self.practice_name,
            'channels': self.channels,
            'last_message': self.last_message.to_dict() if self.last_message else None,
            'unread_count': self.unread_count,
            'messages': [m.to_dict() for m in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
