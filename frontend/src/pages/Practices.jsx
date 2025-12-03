import { useEffect, useState } from 'react'
import axios from 'axios'
import { Plus, Edit, Trash2, X } from 'lucide-react'

function Practices() {
  const [practices, setPractices] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingPractice, setEditingPractice] = useState(null)
  const [formData, setFormData] = useState({
    naam: '',
    gemeente: '',
    email: '',
    tel: '',
    website: '',
    adres: ''
  })

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

  const handleAddNew = () => {
    setEditingPractice(null)
    setFormData({
      naam: '',
      gemeente: '',
      email: '',
      tel: '',
      website: '',
      adres: ''
    })
    setShowModal(true)
  }

  const handleEdit = (practice) => {
    setEditingPractice(practice)
    setFormData({
      naam: practice.naam || '',
      gemeente: practice.gemeente || '',
      email: practice.email || '',
      tel: practice.tel || '',
      website: practice.website || '',
      adres: practice.adres || ''
    })
    setShowModal(true)
  }

  const handleDelete = async (practice) => {
    if (!confirm(`Weet je zeker dat je "${practice.naam}" wilt verwijderen?`)) {
      return
    }

    try {
      await axios.delete(`/api/practices/${practice.nr}`)
      alert('Praktijk verwijderd!')
      fetchPractices()
    } catch (error) {
      console.error('Error deleting practice:', error)
      alert('Fout bij verwijderen: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validation
    if (!formData.naam || !formData.gemeente) {
      alert('Naam en gemeente zijn verplicht!')
      return
    }

    try {
      if (editingPractice) {
        // Update existing
        await axios.put(`/api/practices/${editingPractice.nr}`, formData)
        alert('Praktijk bijgewerkt!')
      } else {
        // Create new
        await axios.post('/api/practices', formData)
        alert('Praktijk toegevoegd!')
      }
      
      setShowModal(false)
      fetchPractices()
    } catch (error) {
      console.error('Error saving practice:', error)
      alert('Fout bij opslaan: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
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
          <button className="btn btn-primary" onClick={handleAddNew}>
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
            {practices.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                  Geen praktijken gevonden. Klik op "Nieuwe Praktijk" om te beginnen.
                </td>
              </tr>
            ) : (
              practices.map((practice) => (
                <tr key={practice.nr}>
                  <td>{practice.naam}</td>
                  <td>{practice.gemeente}</td>
                  <td>{practice.email || '-'}</td>
                  <td>{practice.tel || '-'}</td>
                  <td>
                    <span className={`badge ${
                      practice.workflow?.status === 'Lead' ? 'badge-success' :
                      practice.workflow?.status === 'Contacted' ? 'badge-warning' :
                      'badge-info'
                    }`}>
                      {practice.workflow?.status || 'Nieuw'}
                    </span>
                  </td>
                  <td>
                    <button 
                      className="btn btn-sm" 
                      style={{ marginRight: '0.5rem' }}
                      onClick={() => handleEdit(practice)}
                      title="Bewerken"
                    >
                      <Edit size={14} />
                    </button>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(practice)}
                      title="Verwijderen"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal for Add/Edit */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '0.75rem',
            padding: '2rem',
            width: '90%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <h2 style={{ margin: 0 }}>
                {editingPractice ? 'Praktijk Bewerken' : 'Nieuwe Praktijk'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '0.5rem'
                }}
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Naam *
                </label>
                <input
                  type="text"
                  name="naam"
                  value={formData.naam}
                  onChange={handleInputChange}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    fontSize: '1rem'
                  }}
                  placeholder="Praktijk naam"
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Gemeente *
                </label>
                <input
                  type="text"
                  name="gemeente"
                  value={formData.gemeente}
                  onChange={handleInputChange}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    fontSize: '1rem'
                  }}
                  placeholder="Brussel, Antwerpen, ..."
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    fontSize: '1rem'
                  }}
                  placeholder="info@praktijk.be"
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Telefoon
                </label>
                <input
                  type="tel"
                  name="tel"
                  value={formData.tel}
                  onChange={handleInputChange}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    fontSize: '1rem'
                  }}
                  placeholder="+32 2 123 45 67"
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Website
                </label>
                <input
                  type="url"
                  name="website"
                  value={formData.website}
                  onChange={handleInputChange}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    fontSize: '1rem'
                  }}
                  placeholder="https://praktijk.be"
                />
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Adres
                </label>
                <textarea
                  name="adres"
                  value={formData.adres}
                  onChange={handleInputChange}
                  rows="2"
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.375rem',
                    fontSize: '1rem',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                  placeholder="Straat 123, 1000 Brussel"
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn"
                >
                  Annuleren
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  {editingPractice ? 'Bijwerken' : 'Toevoegen'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Practices
