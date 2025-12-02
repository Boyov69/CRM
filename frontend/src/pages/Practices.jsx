import { useEffect, useState } from 'react'
import axios from 'axios'
import { Plus, Edit, Trash2 } from 'lucide-react'

function Practices() {
  const [practices, setPractices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPractices()
  }, [])

  const fetchPractices = async () => {
    try {
      const response = await axios.get('/api/practices')
      setPractices(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching practices:', error)
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Praktijken</h1>
            <p>Beheer je praktijken database</p>
          </div>
          <button className="btn btn-primary">
            <Plus size={16} style={{ marginRight: '0.5rem', display: 'inline' }} />
            Nieuwe Praktijk
          </button>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Naam</th>
              <th>Gemeente</th>
              <th>Email</th>
              <th>Telefoon</th>
              <th>Status</th>
              <th>Acties</th>
            </tr>
          </thead>
          <tbody>
            {practices.map((practice) => (
              <tr key={practice.nr}>
                <td>{practice.naam}</td>
                <td>{practice.gemeente}</td>
                <td>{practice.email || '-'}</td>
                <td>{practice.tel || '-'}</td>
                <td>
                  <span className={`badge ${
                    practice.status === 'Lead' ? 'badge-success' :
                    practice.status === 'Contacted' ? 'badge-warning' :
                    'badge-info'
                  }`}>
                    {practice.status || 'Nieuw'}
                  </span>
                </td>
                <td>
                  <button className="btn btn-sm" style={{ marginRight: '0.5rem' }}>
                    <Edit size={14} />
                  </button>
                  <button className="btn btn-sm btn-danger">
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Practices
