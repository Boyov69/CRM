import { useEffect, useState } from 'react'
import axios from 'axios'
import { Users, Mail, TrendingUp, CheckCircle } from 'lucide-react'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/campaigns/stats')
      setStats(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching stats:', error)
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overzicht van je CRM activiteiten</p>
      </div>

      <div className="grid grid-4">
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <Users size={24} color="#2563eb" />
            <span className="stat-label">Totaal Praktijken</span>
          </div>
          <div className="stat-value">{stats?.overview?.total || 0}</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <Mail size={24} color="#10b981" />
            <span className="stat-label">Emails Verzonden</span>
          </div>
          <div className="stat-value">{stats?.overview?.contacted || 0}</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <CheckCircle size={24} color="#f59e0b" />
            <span className="stat-label">Responses</span>
          </div>
          <div className="stat-value">{stats?.overview?.leads || 0}</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <TrendingUp size={24} color="#8b5cf6" />
            <span className="stat-label">Conversie Rate</span>
          </div>
          <div className="stat-value">
            {stats?.overview?.conversion_rate 
              ? `${(stats.overview.conversion_rate * 100).toFixed(1)}%` 
              : '0%'}
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Recent Activiteiten</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
            Geen recente activiteiten
          </p>
        </div>

        <div className="card">
          <h3 className="card-title">Volgende Acties</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
            Geen geplande acties
          </p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
