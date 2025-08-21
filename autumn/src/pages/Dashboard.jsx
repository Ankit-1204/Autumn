import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import RunButton from '../components/RunButton'

export default function Dashboard() {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedRunLog, setSelectedRunLog] = useState(null)

  useEffect(() => {
    let mounted = true
    
    async function load() {
      try {
        const res = await api.get('/workflows')
        if (mounted) {
          setWorkflows(res.data || [])
        }
      } catch (err) {
        console.error(err)
        if (mounted) {
          setError('Failed to fetch workflows')
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }
    
    load()
    return () => { mounted = false }
  }, [])

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div className="container dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Your Workflows</h1>
        <p className="dashboard-subtitle">Manage and monitor your workflow executions</p>
      </div>

      {error && <div className="error mb-4">{error}</div>}

      <div className="workflow-grid">
        {workflows.length === 0 ? (
          <div className="text-center text-secondary">
            You have no workflows yet.
          </div>
        ) : (
          workflows.map(wf => (
            <div key={wf.id} className="workflow-card">
              <div className="workflow-header">
                <div>
                  <h3 className="workflow-title">{wf.name}</h3>
                  <p className="workflow-date">
                    Created: {new Date(wf.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="workflow-actions">
                  <RunButton workflowId={wf.id} onOpenLog={(log) => setSelectedRunLog(log)} />
                  <Link to={`/workflows/${wf.id}`} className="btn btn-secondary">
                    Open
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedRunLog && (
        <div className="workflow-card mt-4">
          <h3 className="workflow-title mb-4">Run Logs</h3>
          <pre style={{ whiteSpace: 'pre-wrap', background: '#f8fafc', padding: '1rem', borderRadius: '0.375rem' }}>
            {selectedRunLog}
          </pre>
          <button 
            onClick={() => setSelectedRunLog(null)} 
            className="btn btn-secondary mt-4"
          >
            Close
          </button>
        </div>
      )}
    </div>
  )
}