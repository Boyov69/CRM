"""
Unified Inbox Service
Aggregeert alle communicatie (Email, SMS, WhatsApp) in één inbox
"""
import logging
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from backend.models.message import Message, Conversation

logger = logging.getLogger(__name__)


class InboxService:
    """Service voor unified inbox - alle channels op 1 plek"""
    
    def __init__(self, db_path: str = "data/crm.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize inbox tables"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Messages table - alle berichten van alle channels
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    practice_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT DEFAULT 'sent',
                    metadata TEXT,
                    read INTEGER DEFAULT 0,
                    attachments TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    practice_id INTEGER NOT NULL UNIQUE,
                    practice_name TEXT NOT NULL,
                    channels TEXT NOT NULL,
                    unread_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes voor snelle queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_practice ON messages(practice_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC)")
            
            conn.commit()
            conn.close()
            logger.info("✅ Inbox database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing inbox database: {e}")
            raise
    
    def add_message(
        self,
        practice_id: int,
        practice_name: str,
        channel: str,
        direction: str,
        content: str,
        sender: str,
        recipient: str,
        message_id: Optional[str] = None,
        status: str = 'sent',
        metadata: Optional[Dict] = None,
        attachments: Optional[List] = None
    ) -> Message:
        """Voeg bericht toe aan inbox"""
        import json
        import uuid
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate IDs
            msg_id = message_id or f"msg_{uuid.uuid4().hex[:12]}"
            conv_id = f"conv_{practice_id}"
            timestamp = datetime.now()
            
            # Ensure conversation exists
            cursor.execute("""
                INSERT OR IGNORE INTO conversations (id, practice_id, practice_name, channels, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conv_id, practice_id, practice_name, json.dumps([channel]), timestamp.isoformat(), timestamp.isoformat()))
            
            # Update conversation channels - add new channel if not exists
            cursor.execute("SELECT channels FROM conversations WHERE id = ?", (conv_id,))
            row = cursor.fetchone()
            if row:
                existing_channels = json.loads(row[0])
                if channel not in existing_channels:
                    existing_channels.append(channel)
                    cursor.execute("""
                        UPDATE conversations 
                        SET channels = ?, updated_at = ?
                        WHERE id = ?
                    """, (json.dumps(existing_channels), timestamp.isoformat(), conv_id))
                else:
                    cursor.execute("""
                        UPDATE conversations 
                        SET updated_at = ?
                        WHERE id = ?
                    """, (timestamp.isoformat(), conv_id))
            
            # Insert message
            cursor.execute("""
                INSERT INTO messages (
                    id, conversation_id, practice_id, channel, direction,
                    content, sender, recipient, timestamp, status,
                    metadata, read, attachments
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                msg_id, conv_id, practice_id, channel, direction,
                content, sender, recipient, timestamp.isoformat(), status,
                json.dumps(metadata or {}), 0 if direction == 'inbound' else 1,
                json.dumps(attachments or [])
            ))
            
            # Update unread count if inbound
            if direction == 'inbound':
                cursor.execute("""
                    UPDATE conversations
                    SET unread_count = unread_count + 1
                    WHERE id = ?
                """, (conv_id,))
            
            conn.commit()
            conn.close()
            
            message = Message(
                id=msg_id,
                conversation_id=conv_id,
                practice_id=practice_id,
                channel=channel,
                direction=direction,
                content=content,
                sender=sender,
                recipient=recipient,
                timestamp=timestamp,
                status=status,
                metadata=metadata,
                read=direction == 'outbound',
                attachments=attachments
            )
            
            logger.info(f"✅ Message added to inbox: {msg_id} ({channel})")
            return message
            
        except Exception as e:
            logger.error(f"❌ Error adding message to inbox: {e}")
            raise
    
    def get_conversations(
        self,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Conversation]:
        """Get all conversations met laatste berichten"""
        import json
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query conversations
            query = """
                SELECT 
                    c.id, c.practice_id, c.practice_name, c.channels,
                    c.unread_count, c.created_at, c.updated_at,
                    m.id, m.channel, m.direction, m.content, m.sender,
                    m.recipient, m.timestamp, m.status, m.metadata, m.read
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE 1=1
            """
            
            params = []
            if unread_only:
                query += " AND c.unread_count > 0"
            
            query += """
                AND m.id = (
                    SELECT id FROM messages 
                    WHERE conversation_id = c.id 
                    ORDER BY timestamp DESC LIMIT 1
                )
                ORDER BY c.updated_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                # Parse last message if exists
                last_message = None
                if row[7]:  # message id exists
                    last_message = Message(
                        id=row[7],
                        conversation_id=row[0],
                        practice_id=row[1],
                        channel=row[8],
                        direction=row[9],
                        content=row[10],
                        sender=row[11],
                        recipient=row[12],
                        timestamp=datetime.fromisoformat(row[13]),
                        status=row[14],
                        metadata=json.loads(row[15]) if row[15] else {},
                        read=bool(row[16])
                    )
                
                conversation = Conversation(
                    id=row[0],
                    practice_id=row[1],
                    practice_name=row[2],
                    channels=json.loads(row[3]),
                    unread_count=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    updated_at=datetime.fromisoformat(row[6]),
                    last_message=last_message
                )
                conversations.append(conversation)
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error getting conversations: {e}")
            return []
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get single conversation met alle berichten"""
        import json
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get conversation
            cursor.execute("""
                SELECT id, practice_id, practice_name, channels, unread_count, created_at, updated_at
                FROM conversations
                WHERE id = ?
            """, (conversation_id,))
            
            conv_row = cursor.fetchone()
            if not conv_row:
                return None
            
            # Get all messages
            cursor.execute("""
                SELECT id, channel, direction, content, sender, recipient,
                       timestamp, status, metadata, read, attachments
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))
            
            message_rows = cursor.fetchall()
            messages = []
            
            for row in message_rows:
                message = Message(
                    id=row[0],
                    conversation_id=conversation_id,
                    practice_id=conv_row[1],
                    channel=row[1],
                    direction=row[2],
                    content=row[3],
                    sender=row[4],
                    recipient=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    status=row[7],
                    metadata=json.loads(row[8]) if row[8] else {},
                    read=bool(row[9]),
                    attachments=json.loads(row[10]) if row[10] else []
                )
                messages.append(message)
            
            conversation = Conversation(
                id=conv_row[0],
                practice_id=conv_row[1],
                practice_name=conv_row[2],
                channels=json.loads(conv_row[3]),
                unread_count=conv_row[4],
                created_at=datetime.fromisoformat(conv_row[5]),
                updated_at=datetime.fromisoformat(conv_row[6]),
                messages=messages,
                last_message=messages[-1] if messages else None
            )
            
            conn.close()
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation: {e}")
            return None
    
    def mark_as_read(self, conversation_id: str) -> bool:
        """Mark alle berichten in conversation als gelezen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE messages
                SET read = 1
                WHERE conversation_id = ? AND direction = 'inbound'
            """, (conversation_id,))
            
            cursor.execute("""
                UPDATE conversations
                SET unread_count = 0
                WHERE id = ?
            """, (conversation_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Conversation marked as read: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking conversation as read: {e}")
            return False
    
    def get_unread_count(self) -> int:
        """Get totaal aantal ongelezen berichten"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(unread_count) FROM conversations")
            result = cursor.fetchone()
            
            conn.close()
            return result[0] or 0
            
        except Exception as e:
            logger.error(f"❌ Error getting unread count: {e}")
            return 0
    
    def search_messages(
        self,
        query: str,
        channel: Optional[str] = None,
        practice_id: Optional[int] = None
    ) -> List[Message]:
        """Zoek berichten"""
        import json
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sql = """
                SELECT id, conversation_id, practice_id, channel, direction,
                       content, sender, recipient, timestamp, status, metadata, read, attachments
                FROM messages
                WHERE content LIKE ?
            """
            params = [f"%{query}%"]
            
            if channel:
                sql += " AND channel = ?"
                params.append(channel)
            
            if practice_id:
                sql += " AND practice_id = ?"
                params.append(practice_id)
            
            sql += " ORDER BY timestamp DESC LIMIT 50"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = Message(
                    id=row[0],
                    conversation_id=row[1],
                    practice_id=row[2],
                    channel=row[3],
                    direction=row[4],
                    content=row[5],
                    sender=row[6],
                    recipient=row[7],
                    timestamp=datetime.fromisoformat(row[8]),
                    status=row[9],
                    metadata=json.loads(row[10]) if row[10] else {},
                    read=bool(row[11]),
                    attachments=json.loads(row[12]) if row[12] else []
                )
                messages.append(message)
            
            conn.close()
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error searching messages: {e}")
            return []
