import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MessageComposer from '../components/messaging/MessageComposer';

function Messaging() {
  const [practices, setPractices] = useState([]);
  const [selectedPractices, setSelectedPractices] = useState([]);
  const [showComposer, setShowComposer] = useState(false);
  const [channel, setChannel] = useState('sms');
  const [bulkMode, setBulkMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ sms: 0, whatsapp: 0 });

  useEffect(() => {
    loadPractices();
    loadStats();
  }, []);

  const loadPractices = async () => {
    try {
      const response = await axios.get('/api/practices');
      setPractices(response.data);
    } catch (error) {
      console.error('Error loading practices:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const [smsRes, waRes] = await Promise.all([
        axios.get('/api/sms/history'),
        axios.get('/api/whatsapp/history')
      ]);
      setStats({
        sms: smsRes.data.total || 0,
        whatsapp: waRes.data.total || 0
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const togglePracticeSelection = (practiceId) => {
    setSelectedPractices(prev =>
      prev.includes(practiceId)
        ? prev.filter(id => id !== practiceId)
        : [...prev, practiceId]
    );
  };

  const selectAll = () => {
    if (selectedPractices.length === practices.length) {
      setSelectedPractices([]);
    } else {
      setSelectedPractices(practices.map(p => p.id));
    }
  };

  const handleSendBulk = async (message, mediaUrl = null) => {
    const recipients = practices
      .filter(p => selectedPractices.includes(p.id))
      .map(p => ({
        practice_id: p.id,
        phone_number: p.tel,
        naam: p.naam,
        gemeente: p.gemeente
      }));

    if (recipients.length === 0) {
      alert('Selecteer minstens één praktijk');
      return;
    }

    try {
      const endpoint = channel === 'sms' ? '/api/sms/bulk' : '/api/whatsapp/bulk';
      const payload = {
        recipients,
        message,
        ...(mediaUrl && { media_url: mediaUrl })
      };

      const response = await axios.post(endpoint, payload);
      
      alert(`✅ Verzonden: ${response.data.sent}/${response.data.total}`);
      setSelectedPractices([]);
      setShowComposer(false);
      loadStats();
    } catch (error) {
      alert('❌ Fout bij verzenden: ' + (error.response?.data?.message || error.message));
    }
  };

  if (loading) {
    return <div style={styles.loading}>Laden...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>📱 Messaging Center</h1>
        <div style={styles.stats}>
          <div style={styles.statCard}>
            <span style={styles.statLabel}>📱 SMS Verzonden</span>
            <span style={styles.statValue}>{stats.sms}</span>
          </div>
          <div style={styles.statCard}>
            <span style={styles.statLabel}>💬 WhatsApp Verzonden</span>
            <span style={styles.statValue}>{stats.whatsapp}</span>
          </div>
        </div>
      </div>

      {/* Channel & Mode Selection */}
      <div style={styles.controls}>
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

        <button
          style={styles.bulkBtn}
          onClick={() => {
            setBulkMode(true);
            setShowComposer(true);
          }}
          disabled={selectedPractices.length === 0}
        >
          Bulk Verzenden ({selectedPractices.length})
        </button>
      </div>

      {/* Practice List with Selection */}
      <div style={styles.practiceList}>
        <div style={styles.listHeader}>
          <label style={styles.selectAllLabel}>
            <input
              type="checkbox"
              checked={selectedPractices.length === practices.length}
              onChange={selectAll}
            />
            <span>Selecteer Alles ({practices.length})</span>
          </label>
          <span>{selectedPractices.length} geselecteerd</span>
        </div>

        <div style={styles.practices}>
          {practices.map(practice => (
            <div
              key={practice.id}
              style={{
                ...styles.practiceCard,
                ...(selectedPractices.includes(practice.id) ? styles.practiceCardSelected : {})
              }}
              onClick={() => togglePracticeSelection(practice.id)}
            >
              <input
                type="checkbox"
                checked={selectedPractices.includes(practice.id)}
                onChange={() => {}}
                style={styles.checkbox}
              />
              <div style={styles.practiceInfo}>
                <strong>{practice.naam}</strong>
                <span style={styles.practiceDetails}>
                  {practice.gemeente} • {practice.tel || 'Geen nummer'}
                </span>
              </div>
              <button
                style={styles.sendOneBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedPractices([practice.id]);
                  setBulkMode(false);
                  setShowComposer(true);
                }}
              >
                Verstuur
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Message Composer Modal */}
      {showComposer && (
        <div style={styles.modal} onClick={() => setShowComposer(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2>
              {bulkMode
                ? `Bulk ${channel === 'sms' ? 'SMS' : 'WhatsApp'} naar ${selectedPractices.length} praktijken`
                : `${channel === 'sms' ? 'SMS' : 'WhatsApp'} versturen`}
            </h2>
            
            {bulkMode ? (
              <BulkComposer
                channel={channel}
                recipientCount={selectedPractices.length}
                onSend={handleSendBulk}
                onClose={() => setShowComposer(false)}
              />
            ) : (
              <MessageComposer
                practice={practices.find(p => p.id === selectedPractices[0])}
                defaultChannel={channel}
                onClose={() => setShowComposer(false)}
                onSent={() => {
                  setShowComposer(false);
                  loadStats();
                }}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Bulk Composer Component
const BulkComposer = ({ channel, recipientCount, onSend, onClose }) => {
  const [message, setMessage] = useState('');
  const [mediaUrl, setMediaUrl] = useState('');
  const [templates, setTemplates] = useState([]);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, [channel]);

  const loadTemplates = async () => {
    try {
      const endpoint = channel === 'sms' 
        ? '/api/sms/templates'
        : '/api/whatsapp/templates';
      const response = await axios.get(endpoint);
      setTemplates(Object.entries(response.data.templates || {}));
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const handleSend = async () => {
    if (!message.trim()) return;
    setSending(true);
    try {
      await onSend(message, mediaUrl || null);
    } finally {
      setSending(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '15px' }}>
        <label>Template:</label>
        <select
          onChange={(e) => {
            const [, templateData] = templates.find(([id]) => id === e.target.value) || [];
            if (templateData) setMessage(templateData.content);
          }}
          style={{ width: '100%', padding: '8px', marginTop: '5px' }}
        >
          <option value="">-- Kies template --</option>
          {templates.map(([id, data]) => (
            <option key={id} value={id}>{data.name}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Bericht... Gebruik {naam}, {gemeente} voor personalisatie"
          rows={6}
          style={{ width: '100%', padding: '10px' }}
        />
      </div>

      {channel === 'whatsapp' && (
        <div style={{ marginBottom: '15px' }}>
          <input
            type="url"
            value={mediaUrl}
            onChange={(e) => setMediaUrl(e.target.value)}
            placeholder="Media URL (optioneel)"
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
      )}

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
        <button onClick={onClose} style={styles.btnSecondary}>
          Annuleren
        </button>
        <button
          onClick={handleSend}
          disabled={sending || !message.trim()}
          style={styles.btnPrimary}
        >
          {sending ? 'Verzenden...' : `Verstuur naar ${recipientCount} praktijken`}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  loading: {
    padding: '40px',
    textAlign: 'center',
    fontSize: '18px',
  },
  header: {
    marginBottom: '30px',
  },
  stats: {
    display: 'flex',
    gap: '20px',
    marginTop: '20px',
  },
  statCard: {
    flex: 1,
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '20px',
    borderRadius: '10px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  statLabel: {
    fontSize: '14px',
    opacity: 0.9,
  },
  statValue: {
    fontSize: '32px',
    fontWeight: 'bold',
  },
  controls: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    padding: '20px',
    background: 'white',
    borderRadius: '10px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  channelSelector: {
    display: 'flex',
    gap: '10px',
  },
  channelBtn: {
    padding: '10px 20px',
    border: '2px solid #e0e0e0',
    background: 'white',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  channelBtnActive: {
    background: '#4CAF50',
    color: 'white',
    borderColor: '#4CAF50',
  },
  bulkBtn: {
    padding: '10px 20px',
    background: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
  },
  practiceList: {
    background: 'white',
    borderRadius: '10px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  listHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px 20px',
    background: '#f5f5f5',
    borderBottom: '1px solid #e0e0e0',
  },
  selectAllLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
  },
  practices: {
    maxHeight: '500px',
    overflowY: 'auto',
  },
  practiceCard: {
    display: 'flex',
    alignItems: 'center',
    padding: '15px 20px',
    borderBottom: '1px solid #f0f0f0',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  practiceCardSelected: {
    background: '#e3f2fd',
  },
  checkbox: {
    marginRight: '15px',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  practiceInfo: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  practiceDetails: {
    fontSize: '14px',
    color: '#666',
  },
  sendOneBtn: {
    padding: '8px 16px',
    background: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalContent: {
    background: 'white',
    borderRadius: '10px',
    padding: '30px',
    maxWidth: '600px',
    width: '90%',
    maxHeight: '90vh',
    overflowY: 'auto',
  },
  btnPrimary: {
    padding: '10px 20px',
    background: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
  btnSecondary: {
    padding: '10px 20px',
    background: '#f5f5f5',
    color: '#333',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
};

export default Messaging;
