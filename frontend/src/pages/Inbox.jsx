import React, { useState, useEffect } from 'react';
import {
  Container, Row, Col, Card, ListGroup, Badge, Form,
  InputGroup, Button, Alert, Spinner
} from 'react-bootstrap';
import { FaEnvelope, FaSms, FaWhatsapp, FaSearch, FaPaperPlane } from 'react-icons/fa';

const Inbox = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [replyText, setReplyText] = useState('');
  const [replyChannel, setReplyChannel] = useState('sms');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadConversations();
    loadUnreadCount();
    // Poll for updates every 10 seconds
    const interval = setInterval(() => {
      loadConversations();
      loadUnreadCount();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadConversations = async () => {
    try {
      const response = await fetch('/api/inbox/conversations');
      const data = await response.json();
      if (data.success) {
        setConversations(data.conversations);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to load conversations');
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const response = await fetch('/api/inbox/unread-count');
      const data = await response.json();
      if (data.success) {
        setUnreadCount(data.unread_count);
      }
    } catch (err) {
      console.error('Failed to load unread count:', err);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await fetch(`/api/inbox/conversation/${conversationId}`);
      const data = await response.json();
      if (data.success) {
        setSelectedConversation(data.conversation);
        setMessages(data.conversation.messages || []);
        // Mark as read
        await fetch(`/api/inbox/conversation/${conversationId}/mark-read`, {
          method: 'PUT'
        });
        loadConversations();
        loadUnreadCount();
      }
    } catch (err) {
      setError('Failed to load conversation');
    }
  };

  const sendReply = async () => {
    if (!replyText.trim() || !selectedConversation) return;

    setSending(true);
    try {
      const response = await fetch('/api/inbox/reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: selectedConversation.id,
          practice_id: selectedConversation.practice_id,
          channel: replyChannel,
          content: replyText
        })
      });

      const data = await response.json();
      if (data.success) {
        setReplyText('');
        // Reload conversation
        loadConversation(selectedConversation.id);
      } else {
        setError(data.error || 'Failed to send reply');
      }
    } catch (err) {
      setError('Failed to send reply');
    }
    setSending(false);
  };

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'email': return <FaEnvelope className="text-primary" />;
      case 'sms': return <FaSms className="text-success" />;
      case 'whatsapp': return <FaWhatsapp className="text-success" />;
      default: return null;
    }
  };

  const getChannelBadge = (channel) => {
    const colors = { email: 'primary', sms: 'success', whatsapp: 'success' };
    return <Badge bg={colors[channel]} className="ms-1">{channel.toUpperCase()}</Badge>;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
        <p>Loading inbox...</p>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      <Row className="mb-3">
        <Col>
          <h2>
            📬 Unified Inbox
            {unreadCount > 0 && (
              <Badge bg="danger" className="ms-2">{unreadCount}</Badge>
            )}
          </h2>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Row style={{ height: '75vh' }}>
        {/* Conversations List */}
        <Col md={4} className="border-end" style={{ height: '100%', overflowY: 'auto' }}>
          <InputGroup className="mb-3">
            <InputGroup.Text><FaSearch /></InputGroup.Text>
            <Form.Control
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </InputGroup>

          {conversations.length === 0 ? (
            <Alert variant="info">No conversations yet</Alert>
          ) : (
            <ListGroup>
              {conversations
                .filter(c => c.practice_name.toLowerCase().includes(searchQuery.toLowerCase()))
                .map(conv => (
                  <ListGroup.Item
                    key={conv.id}
                    action
                    active={selectedConversation?.id === conv.id}
                    onClick={() => loadConversation(conv.id)}
                    className="d-flex justify-content-between align-items-start"
                  >
                    <div className="flex-grow-1">
                      <div className="d-flex justify-content-between">
                        <strong>{conv.practice_name}</strong>
                        {conv.unread_count > 0 && (
                          <Badge bg="danger" pill>{conv.unread_count}</Badge>
                        )}
                      </div>
                      <div className="text-muted small">
                        {conv.channels.map(ch => getChannelIcon(ch))}
                        {conv.last_message && (
                          <>
                            <span className="ms-2">{conv.last_message.content.substring(0, 50)}...</span>
                          </>
                        )}
                      </div>
                      {conv.last_message && (
                        <div className="text-muted small">
                          {formatTimestamp(conv.last_message.timestamp)}
                        </div>
                      )}
                    </div>
                  </ListGroup.Item>
                ))}
            </ListGroup>
          )}
        </Col>

        {/* Message Thread */}
        <Col md={8} className="d-flex flex-column" style={{ height: '100%' }}>
          {!selectedConversation ? (
            <div className="d-flex align-items-center justify-content-center h-100 text-muted">
              Select a conversation to view messages
            </div>
          ) : (
            <>
              {/* Conversation Header */}
              <Card className="mb-2">
                <Card.Body className="py-2">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{selectedConversation.practice_name}</strong>
                      <div className="small text-muted">
                        Channels: {selectedConversation.channels.map(ch => getChannelBadge(ch))}
                      </div>
                    </div>
                  </div>
                </Card.Body>
              </Card>

              {/* Messages */}
              <div className="flex-grow-1 overflow-auto mb-3" style={{ maxHeight: 'calc(100% - 180px)' }}>
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`mb-3 d-flex ${msg.direction === 'outbound' ? 'justify-content-end' : 'justify-content-start'}`}
                  >
                    <Card
                      className={msg.direction === 'outbound' ? 'bg-primary text-white' : ''}
                      style={{ maxWidth: '70%' }}
                    >
                      <Card.Body className="py-2 px-3">
                        <div className="d-flex align-items-center mb-1">
                          {getChannelIcon(msg.channel)}
                          <small className="ms-2">
                            {msg.direction === 'outbound' ? 'You' : msg.sender}
                          </small>
                          <small className="ms-auto text-muted">
                            {formatTimestamp(msg.timestamp)}
                          </small>
                        </div>
                        <div>{msg.content}</div>
                        {msg.attachments && msg.attachments.length > 0 && (
                          <div className="mt-2">
                            📎 {msg.attachments.length} attachment(s)
                          </div>
                        )}
                      </Card.Body>
                    </Card>
                  </div>
                ))}
              </div>

              {/* Reply Box */}
              <Card>
                <Card.Body>
                  <Form.Group className="mb-2">
                    <Form.Label>Reply via:</Form.Label>
                    <div>
                      {selectedConversation.channels.includes('sms') && (
                        <Form.Check
                          inline
                          type="radio"
                          label="SMS"
                          value="sms"
                          checked={replyChannel === 'sms'}
                          onChange={(e) => setReplyChannel(e.target.value)}
                        />
                      )}
                      {selectedConversation.channels.includes('whatsapp') && (
                        <Form.Check
                          inline
                          type="radio"
                          label="WhatsApp"
                          value="whatsapp"
                          checked={replyChannel === 'whatsapp'}
                          onChange={(e) => setReplyChannel(e.target.value)}
                        />
                      )}
                      {selectedConversation.channels.includes('email') && (
                        <Form.Check
                          inline
                          type="radio"
                          label="Email"
                          value="email"
                          checked={replyChannel === 'email'}
                          onChange={(e) => setReplyChannel(e.target.value)}
                        />
                      )}
                    </div>
                  </Form.Group>
                  <InputGroup>
                    <Form.Control
                      as="textarea"
                      rows={2}
                      placeholder="Type your message..."
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          sendReply();
                        }
                      }}
                    />
                    <Button
                      variant="primary"
                      onClick={sendReply}
                      disabled={!replyText.trim() || sending}
                    >
                      {sending ? <Spinner size="sm" /> : <FaPaperPlane />}
                    </Button>
                  </InputGroup>
                  <small className="text-muted">Press Enter to send, Shift+Enter for new line</small>
                </Card.Body>
              </Card>
            </>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Inbox;
