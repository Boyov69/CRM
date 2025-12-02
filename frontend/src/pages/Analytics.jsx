import { useEffect, useState } from 'react'
import axios from 'axios'

function Analytics() {
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
        <h1>Analytics</h1>
        <p>Diepgaande inzichten in je campagnes</p>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Funnel Analyse</h3>
          {stats?.funnel ? (
            <div style={{ marginTop: '1rem' }}>
              {Object.entries(stats.funnel).map(([stage, count]) => (
                <div key={stage} style={{ marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span style={{ textTransform: 'capitalize' }}>{stage}</span>
                    <span style={{ fontWeight: '600' }}>{count}</span>
                  </div>
                  <div style={{ 
                    height: '8px', 
                    background: 'var(--border)', 
                    borderRadius: '4px',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      width: `${(count / stats.overview.total * 100)}%`,
                      height: '100%',
                      background: 'var(--primary)',
                      transition: 'width 0.3s'
                    }}></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
              Geen data beschikbaar
            </p>
          )}
        </div>

        <div className="card">
          <h3 className="card-title">ROI Projectie</h3>
          {stats?.roi ? (
            <div style={{ marginTop: '1rem' }}>
              <div style={{ marginBottom: '1rem' }}>
                <div className="stat-label">Verwachte Conversies</div>
                <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                  {stats.roi.expected_conversions || 0}
                </div>
              </div>
              <div>
                <div className="stat-label">Potentiële Omzet</div>
                <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                  €{stats.roi.potential_revenue?.toLocaleString() || '0'}
                </div>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
              Geen data beschikbaar
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Analytics
