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
      const response = await axios.get('/api/campaign/stats')
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
        <h1>
          Dashboard
          <span className="header-ai-badge">AI-Powered</span>
        </h1>
        <p>Real-time overzicht van je omnichannel CRM activiteiten</p>
      </div>

      <div className="card-container grid-4">
        <div className="premium-card">
          <div className="stat-display">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: 'var(--gradient-primary)',
                borderRadius: 'var(--radius-lg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-md)'
              }}>
                <Users size={24} color="white" />
              </div>
              <span className="stat-label">Praktijken</span>
            </div>
            <div className="stat-value">{stats?.overview?.total_practices || 0}</div>
            <div className="stat-change positive">
              ↑ 12% deze maand
            </div>
          </div>
        </div>

        <div className="premium-card">
          <div className="stat-display">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                borderRadius: 'var(--radius-lg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-md)'
              }}>
                <Mail size={24} color="white" />
              </div>
              <span className="stat-label">Berichten</span>
            </div>
            <div className="stat-value">{stats?.overview?.contacted || 0}</div>
            <div className="stat-change positive">
              ↑ 23% deze week
            </div>
          </div>
        </div>

        <div className="premium-card">
          <div className="stat-display">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                borderRadius: 'var(--radius-lg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-md)'
              }}>
                <CheckCircle size={24} color="white" />
              </div>
              <span className="stat-label">Responses</span>
            </div>
            <div className="stat-value">{stats?.overview?.replied || 0}</div>
            <div className="stat-change positive">
              ↑ 8 nieuwe leads
            </div>
          </div>
        </div>

        <div className="premium-card">
          <div className="stat-display">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{
                width: '48px',
                height: '48px',
                background: 'var(--gradient-cool)',
                borderRadius: 'var(--radius-lg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-md)'
              }}>
                <TrendingUp size={24} color="white" />
              </div>
              <span className="stat-label">Conversie</span>
            </div>
            <div className="stat-value">
              {stats?.overview?.rates?.conversion_rate
                ? `${stats.overview.rates.conversion_rate}%`
                : '0%'}
            </div>
            <div className="stat-change positive">
              ↑ 2.3% hoger
            </div>
          </div>
        </div>
      </div>

      <div className="card-container grid-2">
        <div className="premium-card">
          <h3 className="card-title">📊 Recent Activiteiten</h3>
          <div className="empty-state" style={{ padding: '2rem 1rem' }}>
            <div className="empty-state-icon">🎯</div>
            <div className="empty-state-title">Geen recente activiteiten</div>
            <div className="empty-state-description">
              Start je eerste campagne om activiteiten te zien
            </div>
          </div>
        </div>

        <div className="premium-card">
          <h3 className="card-title">✨ AI Insights</h3>
          <div className="empty-state" style={{ padding: '2rem 1rem' }}>
            <div className="empty-state-icon">🤖</div>
            <div className="empty-state-title">AI analyseert je data</div>
            <div className="empty-state-description">
              Binnenkort krijg je slimme aanbevelingen op basis van je CRM data
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
