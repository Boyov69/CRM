import { useState } from 'react'
import { Send, Zap } from 'lucide-react'

function Campaigns() {
  const [template, setTemplate] = useState('initial_outreach')
  const [useAI, setUseAI] = useState(false)

  return (
    <div>
      <div className="page-header">
        <h1>Email Campagnes</h1>
        <p>Start en beheer je email campagnes</p>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Nieuwe Campagne</h3>
          
          <div className="form-group">
            <label className="form-label">Email Template</label>
            <select 
              className="form-input"
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
            >
              <option value="initial_outreach">Initial Outreach</option>
              <option value="follow_up">Follow-up</option>
              <option value="final_reminder">Final Reminder</option>
            </select>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input 
                type="checkbox"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
              />
              <Zap size={16} color="#f59e0b" />
              <span>Gebruik AI Personalisatie</span>
            </label>
          </div>

          <button className="btn btn-primary" style={{ width: '100%' }}>
            <Send size={16} style={{ marginRight: '0.5rem', display: 'inline' }} />
            Start Campagne
          </button>
        </div>

        <div className="card">
          <h3 className="card-title">Campagne Historie</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
            Geen eerdere campagnes
          </p>
        </div>
      </div>
    </div>
  )
}

export default Campaigns
