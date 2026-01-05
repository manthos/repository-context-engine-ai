import React, { useState, useEffect } from 'react'
import { apiClient } from '../services/api'
import './CacheBrowser.css'

interface CachedRepo {
  id: string
  url: string
  status: string
  cache_path: string
}

interface CacheBrowserProps {
  onSelectRepo: (repoId: string) => void
}

const CacheBrowser: React.FC<CacheBrowserProps> = ({ onSelectRepo }) => {
  const [repos, setRepos] = useState<CachedRepo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadCachedRepos()
  }, [])

  const loadCachedRepos = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.listCachedRepos()
      setRepos(response.data.repositories || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load cached repositories')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return '#28a745'
      case 'processing':
        return '#ffc107'
      case 'failed':
        return '#dc3545'
      default:
        return '#6c757d'
    }
  }

  if (loading) return <div className="CacheBrowser-loading">Loading cached repositories...</div>
  if (error) return <div className="CacheBrowser-error">Error: {error}</div>

  return (
    <div className="CacheBrowser">
      <div className="CacheBrowser-header">
        <h2>Select Repository to View</h2>
        <button onClick={loadCachedRepos} className="CacheBrowser-refresh">
          🔄 Refresh
        </button>
      </div>
      {repos.length === 0 ? (
        <div className="CacheBrowser-empty">
          <p>No cached repositories found.</p>
          <p>Use "Analyze New Repository" to add a repository.</p>
        </div>
      ) : (
        <div className="CacheBrowser-list">
          {repos.map((repo) => (
            <div key={repo.id} className="CacheBrowser-item">
              <div className="CacheBrowser-item-header">
                <h3 className="CacheBrowser-item-title">{repo.url}</h3>
                <span
                  className="CacheBrowser-item-status"
                  style={{ color: getStatusColor(repo.status) }}
                >
                  {repo.status}
                </span>
              </div>
              <div className="CacheBrowser-item-path">{repo.cache_path}</div>
              <button
                className="CacheBrowser-item-button"
                onClick={() => onSelectRepo(repo.id)}
              >
                View Repository
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CacheBrowser

