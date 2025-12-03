import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MessageComposer = ({ 
  practice, 
  onClose, 
  onSent,
  defaultChannel = 'sms' 
}) => {
  const [channel, setChannel] = useState(defaultChannel);
  const [message, setMessage] = useState('');
  const [template, setTemplate] = useState('');
  const [templates, setTemplates] = useState([]);
  const [mediaUrl, setMediaUrl] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [charCount, setCharCount] = useState(0);
  const [smsSegments, setSmsSegments] = useState(1);
  const [cost, setCost] = useState(0);

  useEffect(() => {
    loadTemplates();
  }, [channel]);

  useEffect(() => {
    // Calculate SMS metrics
    if (channel === 'sms') {
      setCharCount(message.length);
      const segments = calculateSegments(message);
      setSmsSegments(segments);
      setCost(segments * 0.0075); // €0.0075 per segment
    }
  }, [message, channel]);

  const calculateSegments = (text) => {
    const length = text.length;
    if (length <= 160) return 1;
    return Math.ceil((length - 160) / 153) + 1;
  };

  const loadTemplates = async () => {
    try {
      const endpoint = channel === 'sms' 
        ? '/api/sms/templates'
        : '/api/whatsapp/templates?approved_only=true';
      
      const response = await axios.get(endpoint);
      setTemplates(Object.entries(response.data.templates || {}));
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const handleTemplateSelect = (templateId, templateData) => {
    setTemplate(templateId);
    let content = templateData.content;
    
    // Replace variables with practice data
    if (practice) {
      content = content.replace('{naam}', practice.naam || '');
      content = content.replace('{gemeente}', practice.gemeente || '');
      content = content.replace('{praktijk}', practice.praktijk || practice.naam || '');
      content = content.replace('{{1}}', practice.naam || '');
      content = content.replace('{{2}}', 'Uw naam'); // Placeholder for sender
      content = content.replace('{{3}}', practice.gemeente || '');
    }
    
    setMessage(content);
  };

  const handleSend = async () => {
    if (!message.trim()) {
      setError('Bericht mag niet leeg zijn');
      return;
    }

    if (!practice?.tel) {
      setError('Praktijk heeft geen telefoonnummer');
      return;
    }

    setSending(true);
    setError('');

    try {
      const endpoint = channel === 'sms' ? '/api/sms/send' : '/api/whatsapp/send';
      const payload = {
        to_number: practice.tel,
        message: message,
        practice_id: practice.id
      };

      if (channel === 'whatsapp' && mediaUrl) {
        payload.media_url = mediaUrl;
      }

      const response = await axios.post(endpoint, payload);

      if (response.data.success) {
        onSent && onSent(response.data);
        setMessage('');
        setTemplate('');
        setMediaUrl('');
        onClose && onClose();
      } else {
        setError(response.data.message || 'Fout bij verzenden');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Fout bij verzenden');
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={styles.composer}>
      {/* Channel Selector */}
      <div style={styles.channelSelector}>
        <button
          style={{
            ...styles.channelBtn,
            ...(channel === 'sms' ? styles.channelBtnActive : {})
          }}
          onClick={() => setChannel('sms')}
        >
          📱 SMS
        </button>
        <button
          style={{
            ...styles.channelBtn,
            ...(channel === 'whatsapp' ? styles.channelBtnActive : {})
          }}
          onClick={() => setChannel('whatsapp')}
        >
          💬 WhatsApp
        </button>
      </div>

      {/* Practice Info */}
      {practice && (
        <div style={styles.recipientInfo}>
          <strong>{practice.naam}</strong>
          <span>{practice.tel}</span>
        </div>
      )}

      {/* Template Selector */}
      {templates.length > 0 && (
        <div style={styles.templateSelector}>
          <label>Kies een template:</label>
          <select 
            value={template}
            onChange={(e) => {
              const [templateId, templateData] = templates.find(([id]) => id === e.target.value) || [];
              if (templateId) handleTemplateSelect(templateId, templateData);
            }}
            style={styles.select}
          >
            <option value="">-- Geen template --</option>
            {templates.map(([id, data]) => (
              <option key={id} value={id}>
                {data.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Message Input */}
      <div style={styles.messageInput}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={`Typ je ${channel === 'sms' ? 'SMS' : 'WhatsApp'} bericht...`}
          rows={6}
          maxLength={channel === 'sms' ? 1600 : undefined}
          style={styles.textarea}
        />
        
        {/* SMS Metrics */}
        {channel === 'sms' && (
          <div style={styles.smsMetrics}>
            <span>{charCount} tekens</span>
            <span>{smsSegments} segment{smsSegments > 1 ? 'en' : ''}</span>
            <span>~€{cost.toFixed(4)}</span>
          </div>
        )}
      </div>

      {/* Media URL (WhatsApp only) */}
      {channel === 'whatsapp' && (
        <div style={styles.mediaInput}>
          <label>Media URL (optioneel):</label>
          <input
            type="url"
            value={mediaUrl}
            onChange={(e) => setMediaUrl(e.target.value)}
            placeholder="https://voorbeeld.com/image.jpg"
            style={styles.input}
          />
          <small style={styles.small}>Ondersteund: images, PDFs, documents</small>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div style={styles.errorMessage}>
          ⚠️ {error}
        </div>
      )}

      {/* Actions */}
      <div style={styles.actions}>
        {onClose && (
          <button onClick={onClose} style={styles.btnSecondary}>
            Annuleren
          </button>
        )}
        <button 
          onClick={handleSend} 
          style={{
            ...styles.btnPrimary,
            ...(sending || !message.trim() ? styles.btnDisabled : {})
          }}
          disabled={sending || !message.trim()}
        >
          {sending ? 'Verzenden...' : `Verstuur ${channel === 'sms' ? 'SMS' : 'WhatsApp'}`}
        </button>
      </div>
    </div>
  );
};

const styles = {
  composer: {
    background: 'white',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  channelSelector: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
    borderBottom: '2px solid #eee',
    paddingBottom: '10px',
  },
  channelBtn: {
    flex: 1,
    padding: '10px 20px',
    border: '2px solid #e0e0e0',
    background: 'white',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    transition: 'all 0.2s',
  },
  channelBtnActive: {
    background: '#4CAF50',
    color: 'white',
    borderColor: '#4CAF50',
  },
  recipientInfo: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px',
    background: '#f5f5f5',
    borderRadius: '6px',
    marginBottom: '15px',
  },
  templateSelector: {
    marginBottom: '15px',
  },
  select: {
    width: '100%',
    padding: '8px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
  },
  messageInput: {
    marginBottom: '15px',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  smsMetrics: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '5px',
    fontSize: '12px',
    color: '#666',
  },
  mediaInput: {
    marginBottom: '15px',
  },
  input: {
    width: '100%',
    padding: '8px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
  },
  small: {
    display: 'block',
    marginTop: '5px',
    color: '#666',
    fontSize: '12px',
  },
  errorMessage: {
    padding: '10px',
    background: '#ffebee',
    color: '#c62828',
    borderRadius: '6px',
    marginBottom: '15px',
  },
  actions: {
    display: 'flex',
    gap: '10px',
    justifyContent: 'flex-end',
  },
  btnPrimary: {
    padding: '10px 20px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
    background: '#4CAF50',
    color: 'white',
  },
  btnSecondary: {
    padding: '10px 20px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
    background: '#f5f5f5',
    color: '#333',
  },
  btnDisabled: {
    background: '#ccc',
    cursor: 'not-allowed',
  },
};

export default MessageComposer;
