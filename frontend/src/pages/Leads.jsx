import { useState } from 'react'
import axios from 'axios'
import { Search } from 'lucide-react'

function Leads() {
  const [gemeente, setGemeente] = useState('')
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(false)

  const searchLeads = async () => {
    if (!gemeente) return
    
    setLoading(true)
    try {
      const response = await axios.post('/api/leads/search', { gemeente })
      setLeads(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error searching leads:', error)
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Lead Discovery</h1>
        <p>Zoek nieuwe praktijken in België</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Gemeente naam (bijv. Brussel, Antwerpen)"
            value={gemeente}
            onChange={(e) => setGemeente(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchLeads()}
          />
          <button 
            className="btn btn-primary" 
            onClick={searchLeads}
            disabled={loading}
          >
            <Search size={16} style={{ marginRight: '0.5rem', display: 'inline' }} />
            {loading ? 'Zoeken...' : 'Zoeken'}
          </button>
        </div>

        {leads.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Naam</th>
                <th>Gemeente</th>
                <th>Email</th>
                <th>Telefoon</th>
                <th>Acties</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead, index) => (
                <tr key={index}>
                  <td>{lead.naam}</td>
                  <td>{lead.gemeente}</td>
                  <td>{lead.email || '-'}</td>
                  <td>{lead.tel || '-'}</td>
                  <td>
                    <button className="btn btn-sm btn-primary">
                      Toevoegen
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && leads.length === 0 && gemeente && (
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
            Geen resultaten gevonden voor "{gemeente}"
          </p>
        )}
      </div>
    </div>
  )
}

export default Leads
