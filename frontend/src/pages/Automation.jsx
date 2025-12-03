import { useEffect, useState } from 'react'
import axios from 'axios'
import { Zap, AlertCircle, Clock, CheckCircle, TrendingUp } from 'lucide-react'

function Automation() {
  const [hotLeads, setHotLeads] = useState([])
  const [attentionLeads, setAttentionLeads] = useState([])
  const [pendingActions, setPendingActions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAutomationData()
  }, [])

  const fetchAutomationData = async () => {
    try {
      setLoading(true)
      
      // Fetch hot leads
      const hotRes = await axios.get('/api/leads/hot')
      setHotLeads(hotRes.data.leads || [])
      
      // Fetch leads needing attention
      const attentionRes = await axios.get('/api/leads/attention')
      setAttentionLeads(attentionRes.data.leads || [])
      
      // Fetch pending automations
      const pendingRes = await axios.get('/api/automation/pending')
      setPendingActions(pendingRes.data.actions || [])
      
      setLoading(false)
    } catch (error) {
      console.error('Error fetching automation data:', error)
      setLoading(false)
    }
  }

  const executeAction = async (action, practiceId) => {
    try {
      await axios.post('/api/automation/execute', {
        practice_id: practiceId,
        action: action
      })
      
      alert('Automation executed successfully!')
      fetchAutomationData()
    } catch (error) {
      console.error('Error executing automation:', error)
      alert('Failed to execute automation')
    }
  }

  const triggerFollowUp = async (practiceId) => {
    try {
      await axios.post('/api/automation/trigger', {
        practice_id: practiceId,
        event: 'manual_trigger'
      })
      
      alert('Follow-up triggered!')
      fetchAutomationData()
    } catch (error) {
      console.error('Error triggering follow-up:', error)
    }
  }

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: '#ef4444',
      high: '#f59e0b',
      medium: '#3b82f6',
      low: '#6b7280'
    }
    return colors[priority] || colors.low
  }

  const getScoreBadge = (score) => {
    const total = score?.total_score || 0
    const category = score?.category || 'cold'
    
    const colors = {
      hot: { bg: '#fee2e2', text: '#991b1b' },
      warm: { bg: '#fef3c7', text: '#92400e' },
      cold: { bg: '#e0e7ff', text: '#3730a3' }
    }
    
    const color = colors[category] || colors.cold
    
    return (
      <span style={{
        padding: '0.25rem 0.75rem',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: '600',
        background: color.bg,
        color: color.text
      }}>
        {category === 'hot' ? '🔥' : category === 'warm' ? '⚡' : '❄️'} {total}
      </span>
    )
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <div className="page-header">
        <h1>🤖 Intelligente Automatisering</h1>
        <p>AI-driven follow-ups en lead prioritering</p>
      </div>

      {/* Hot Leads Section */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={20} color="#ef4444" />
            Hot Leads - Bel NU!
          </h3>
          <span className="badge badge-warning">{hotLeads.length}</span>
        </div>
        
        {hotLeads.length > 0 ? (
          <div className="grid grid-3">
            {hotLeads.map(lead => (
              <div key={lead.nr} style={{
                padding: '1rem',
                border: '2px solid #fee2e2',
                borderRadius: '0.75rem',
                background: '#fef2f2'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'start',
                  marginBottom: '0.5rem'
                }}>
                  <div>
                    <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>
                      {lead.naam}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {lead.gemeente}
                    </div>
                  </div>
                  {getScoreBadge(lead.score)}
                </div>

                <div style={{
                  fontSize: '0.875rem',
                  color: '#374151',
                  marginBottom: '0.75rem',
                  padding: '0.5rem',
                  background: 'white',
                  borderRadius: '0.5rem'
                }}>
                  {lead.score?.next_action || 'Bel onmiddellijk'}
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="btn btn-sm btn-primary"
                    style={{ flex: 1, fontSize: '0.75rem' }}
                    onClick={() => triggerFollowUp(lead.nr)}
                  >
                    📧 Follow-up
                  </button>
                  <button
                    className="btn btn-sm btn-success"
                    style={{ flex: 1, fontSize: '0.75rem' }}
                  >
                    📞 Bellen
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>
            Geen hot leads op dit moment
          </p>
        )}
      </div>

      {/* Leads Needing Attention */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} color="#f59e0b" />
            Needs Attention
          </h3>
          <span className="badge badge-warning">{attentionLeads.length}</span>
        </div>

        {attentionLeads.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Praktijk</th>
                <th>Score</th>
                <th>Reden</th>
                <th>Actie</th>
              </tr>
            </thead>
            <tbody>
              {attentionLeads.map(lead => (
                <tr key={lead.nr}>
                  <td>
                    <div style={{ fontWeight: '600' }}>{lead.naam}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {lead.gemeente}
                    </div>
                  </td>
                  <td>{getScoreBadge(lead.score)}</td>
                  <td style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    {lead.attention_reason}
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => triggerFollowUp(lead.nr)}
                    >
                      Actie
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>
            Alle leads zijn up-to-date!
          </p>
        )}
      </div>

      {/* Pending Automations */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={20} color="#3b82f6" />
            Geplande Automatiseringen
          </h3>
          <span className="badge badge-info">{pendingActions.length}</span>
        </div>

        {pendingActions.length > 0 ? (
          <div>
            {pendingActions.map((action, index) => (
              <div key={index} style={{
                padding: '1rem',
                marginBottom: '0.75rem',
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem',
                borderLeft: `4px solid ${getPriorityColor(action.priority)}`
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.5rem'
                    }}>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        textTransform: 'uppercase',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        background: getPriorityColor(action.priority),
                        color: 'white'
                      }}>
                        {action.priority}
                      </span>
                      <span style={{ fontWeight: '600' }}>
                        {action.action_type}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.25rem' }}>
                      Rule: {action.rule}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {action.reason}
                    </div>
                  </div>
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => executeAction(action, action.practice_id)}
                  >
                    <CheckCircle size={14} /> Uitvoeren
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>
            Geen geplande automaties
          </p>
        )}
      </div>
    </div>
  )
}

export default Automation
