import React from 'react'
import './Sidebar.css'

export type ViewType = 'analyze' | 'view' | 'search' | 'ask'

interface CachedRepo {
  id: string
  url: string
  status: string
  cache_path: string
}

interface SidebarProps {
  currentView: ViewType
  onViewChange: (view: ViewType) => void
  selectedRepoId: string | null
  cachedRepos: CachedRepo[]
  onSelectRepo: (repoId: string) => void
  onRefreshRepos?: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ 
  currentView, 
  onViewChange, 
  selectedRepoId, 
  cachedRepos,
  onSelectRepo,
  onRefreshRepos
}) => {
  const getRepoName = (url: string) => {
    const urlParts = url.split('/')
    return urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2] || url
  }

  return (
    <div className="Sidebar">
      <div className="Sidebar-header">
        <h2>R2CE</h2>
      </div>
      <nav className="Sidebar-nav">
        <button
          className={`Sidebar-item ${currentView === 'analyze' ? 'active' : ''}`}
          onClick={() => onViewChange('analyze')}
        >
          📥 Analyze New Repository
        </button>
        
        <div className="Sidebar-section">
          <div className="Sidebar-section-header">
            <div className="Sidebar-section-title">📂 View Repository</div>
            {onRefreshRepos && (
              <button 
                className="Sidebar-refresh-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  onRefreshRepos()
                }}
                title="Refresh repository list"
              >
                🔄
              </button>
            )}
          </div>
          {cachedRepos.length === 0 ? (
            <div className="Sidebar-repo-empty">No repositories cached</div>
          ) : (
            <div className="Sidebar-repo-list">
              {cachedRepos.map((repo) => (
                <button
                  key={repo.id}
                  className={`Sidebar-repo-item ${selectedRepoId === repo.id ? 'active' : ''} ${currentView === 'view' && selectedRepoId === repo.id ? 'view-active' : ''}`}
                  onClick={() => {
                    onSelectRepo(repo.id)
                    onViewChange('view')
                  }}
                  title={repo.url}
                >
                  <span className="Sidebar-repo-name">{getRepoName(repo.url)}</span>
                  <span className={`Sidebar-repo-status Sidebar-repo-status-${repo.status.toLowerCase()}`}>
                    {repo.status}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <button
          className={`Sidebar-item ${currentView === 'search' ? 'active' : ''}`}
          onClick={() => onViewChange('search')}
          disabled={!selectedRepoId}
        >
          🔍 Search
        </button>
        <button
          className={`Sidebar-item ${currentView === 'ask' ? 'active' : ''}`}
          onClick={() => onViewChange('ask')}
          disabled={!selectedRepoId}
        >
          💬 Ask
        </button>
      </nav>
    </div>
  )
}

export default Sidebar

