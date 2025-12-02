import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { TrendingUp, AlertCircle, Zap } from 'lucide-react'

// Sortable deal card component
function DealCard({ practice, stage }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: practice.nr })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    background: isDragging ? 'white' : '#ffffff',
    padding: '0.75rem',
    marginBottom: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #e5e7eb',
    boxShadow: isDragging
      ? '0 10px 30px rgba(0,0,0,0.15)'
      : '0 1px 3px rgba(0,0,0,0.1)',
    cursor: 'grab',
  }

  const getDealValue = () => practice.pipeline?.deal_value || 0
  const getProbability = () => practice.pipeline?.probability || 0

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div style={{ marginBottom: '0.5rem' }}>
        <div style={{
          fontWeight: '600',
          fontSize: '0.875rem',
          marginBottom: '0.25rem'
        }}>
          {practice.naam}
        </div>
        <div style={{
          fontSize: '0.75rem',
          color: '#6b7280'
        }}>
          {practice.gemeente}
        </div>
      </div>

      {/* Score Badge */}
      {practice.score && (
        <div style={{
          display: 'inline-block',
          padding: '0.25rem 0.5rem',
          borderRadius: '0.25rem',
          fontSize: '0.75rem',
          fontWeight: '600',
          background: practice.score.category === 'hot' ? '#fee2e2' :
                    practice.score.category === 'warm' ? '#fef3c7' : '#e0e7ff',
          color: practice.score.category === 'hot' ? '#991b1b' :
                 practice.score.category === 'warm' ? '#92400e' : '#3730a3'
        }}>
          🔥 {practice.score.total_score}
        </div>
      )}

      {/* Deal Value */}
      {getDealValue() > 0 && (
        <div style={{
          marginTop: '0.5rem',
          fontSize: '0.875rem',
          fontWeight: '600',
          color: '#059669'
        }}>
          €{getDealValue().toLocaleString()}
          <span style={{
            marginLeft: '0.25rem',
            fontSize: '0.75rem',
            color: '#6b7280'
          }}>
            ({getProbability()}%)
          </span>
        </div>
      )}
    </div>
  )
}

function Pipeline() {
  const [stages, setStages] = useState([])
  const [deals, setDeals] = useState({})
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeId, setActiveId] = useState(null)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  )

  useEffect(() => {
    fetchPipelineData()
  }, [])

  const fetchPipelineData = async () => {
    try {
      setLoading(true)
      
      // Fetch stages
      const stagesRes = await axios.get('/api/pipeline/stages')
      setStages(stagesRes.data)
      
      // Fetch deals by stage
      const dealsRes = await axios.get('/api/pipeline/deals')
      setDeals(dealsRes.data)
      
      // Fetch summary
      const summaryRes = await axios.get('/api/pipeline/summary')
      setSummary(summaryRes.data)
      
      setLoading(false)
    } catch (error) {
      console.error('Error fetching pipeline:', error)
      setLoading(false)
    }
  }

  const handleDragStart = (event) => {
    setActiveId(event.active.id)
  }

  const handleDragEnd = async (event) => {
    const { active, over } = event
    
    if (!over) {
      setActiveId(null)
      return
    }

    // Find which stage the deal is being dropped into
    const targetStage = over.id

    // Find the practice being dragged
    let sourcePractice = null
    let sourceStage = null
    
    for (const [stageId, practices] of Object.entries(deals)) {
      const found = practices.find(p => p.nr === active.id)
      if (found) {
        sourcePractice = found
        sourceStage = stageId
        break
      }
    }

    if (!sourcePractice || sourceStage === targetStage) {
      setActiveId(null)
      return
    }

    try {
      // Optimistic UI update
      const newDeals = { ...deals }
      newDeals[sourceStage] = newDeals[sourceStage].filter(p => p.nr !== active.id)
      newDeals[targetStage] = [...(newDeals[targetStage] || []), sourcePractice]
      setDeals(newDeals)

      // Update backend
      await axios.post('/api/pipeline/move', {
        practice_id: sourcePractice.nr,
        to_stage: targetStage,
        reason: 'Moved via drag & drop'
      })

      // Refresh summary
      const summaryRes = await axios.get('/api/pipeline/summary')
      setSummary(summaryRes.data)
      
    } catch (error) {
      console.error('Error moving deal:', error)
      fetchPipelineData() // Revert on error
    }
    
    setActiveId(null)
  }

  if (loading) return <div>Loading pipeline...</div>

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Sales Pipeline</h1>
            <p>Drag & drop deals door de sales funnel</p>
          </div>
          <button className="btn btn-primary" onClick={fetchPipelineData}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <TrendingUp size={24} color="#3b82f6" />
              <span className="stat-label">Total Deals</span>
            </div>
            <div className="stat-value">{summary.total_deals}</div>
          </div>

          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <Zap size={24} color="#10b981" />
              <span className="stat-label">Total Value</span>
            </div>
            <div className="stat-value">€{summary.total_value.toLocaleString()}</div>
          </div>

          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <AlertCircle size={24} color="#22c55e" />
              <span className="stat-label">Won</span>
            </div>
            <div className="stat-value">{summary.won_count}</div>
          </div>

          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
              <TrendingUp size={24} color="#f59e0b" />
              <span className="stat-label">Win Rate</span>
            </div>
            <div className="stat-value">
              {summary.win_rate ? `${summary.win_rate.toFixed(1)}%` : '0%'}
            </div>
          </div>
        </div>
      )}

      {/* Kanban Board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div style={{
          display: 'flex',
          gap: '1rem',
          overflowX: 'auto',
          paddingBottom: '1rem'
        }}>
          {stages.filter(s => s.id !== 'won' && s.id !== 'lost').map(stage => (
            <SortableContext
              key={stage.id}
              id={stage.id}
              items={deals[stage.id]?.map(p => p.nr) || []}
              strategy={verticalListSortingStrategy}
            >
              <div
                style={{
                  background: '#f9fafb',
                  padding: '1rem',
                  borderRadius: '0.75rem',
                  minWidth: '280px',
                  maxWidth: '280px',
                  border: '2px solid #e5e7eb'
                }}
              >
                {/* Stage Header */}
                <div style={{
                  marginBottom: '1rem',
                  paddingBottom: '0.75rem',
                  borderBottom: `3px solid ${stage.color}`
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '0.25rem'
                  }}>
                    <h3 style={{
                      fontSize: '0.875rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      color: stage.color
                    }}>
                      {stage.name}
                    </h3>
                    <span style={{
                      background: stage.color,
                      color: 'white',
                      padding: '0.125rem 0.5rem',
                      borderRadius: '999px',
                      fontSize: '0.75rem',
                      fontWeight: '600'
                    }}>
                      {deals[stage.id]?.length || 0}
                    </span>
                  </div>
                  {summary && summary.stages[stage.id] && (
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                      €{summary.stages[stage.id].value.toLocaleString()}
                    </div>
                  )}
                </div>

                {/* Deal Cards */}
                <div style={{ minHeight: '100px' }}>
                  {deals[stage.id]?.map((practice) => (
                    <DealCard key={practice.nr} practice={practice} stage={stage} />
                  ))}
                </div>
              </div>
            </SortableContext>
          ))}
        </div>
      </DndContext>

      {/* Won/Lost Section */}
      <div className="grid grid-2" style={{ marginTop: '2rem' }}>
        <div className="card">
          <h3 className="card-title" style={{ color: '#22c55e' }}>
            ✅ Gewonnen ({summary?.won_count || 0})
          </h3>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {deals['won']?.map(practice => (
              <div key={practice.nr} style={{
                padding: '0.75rem',
                marginBottom: '0.5rem',
                background: '#f0fdf4',
                borderRadius: '0.5rem',
                borderLeft: '4px solid #22c55e'
              }}>
                <div style={{ fontWeight: '600' }}>{practice.naam}</div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {practice.gemeente}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="card-title" style={{ color: '#ef4444' }}>
            ❌ Verloren ({summary?.lost_count || 0})
          </h3>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {deals['lost']?.map(practice => (
              <div key={practice.nr} style={{
                padding: '0.75rem',
                marginBottom: '0.5rem',
                background: '#fef2f2',
                borderRadius: '0.5rem',
                borderLeft: '4px solid #ef4444'
              }}>
                <div style={{ fontWeight: '600' }}>{practice.naam}</div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {practice.gemeente}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Pipeline
