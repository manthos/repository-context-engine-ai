import React, { useState, useEffect } from 'react'
import RepoAnalyzer from './components/RepoAnalyzer'
import SearchBar from './components/SearchBar'
import QAInterface from './components/QAInterface'
import BrowseView from './components/BrowseView'
import CacheBrowser from './components/CacheBrowser'
import Sidebar, { ViewType } from './components/Sidebar'
import { apiClient } from './services/api'
import './App.css'

interface CachedRepo {
  id: string
  url: string
  status: string
  cache_path: string
}

function App() {
  const [selectedRepoId, setSelectedRepoId] = useState<string | null>(null)
  const [currentView, setCurrentView] = useState<ViewType>('analyze')
  const [cachedRepos, setCachedRepos] = useState<CachedRepo[]>([])
  const [repoName, setRepoName] = useState<string>('')
  const [browsePath, setBrowsePath] = useState<string>('')

  // Load cached repos on mount
  useEffect(() => {
    loadCachedRepos()
  }, [])

  // Update repo name when selectedRepoId changes
  useEffect(() => {
    if (selectedRepoId) {
      const repo = cachedRepos.find(r => r.id === selectedRepoId)
      if (repo) {
        // Extract repo name from URL (e.g., "https://github.com/user/repo" -> "user-repo")
        const urlParts = repo.url.split('/')
        const name = urlParts[urlParts.length - 1] || urlParts[urlParts.length - 2] || 'Repository'
        setRepoName(name)
      }
    }
  }, [selectedRepoId, cachedRepos])

  const loadCachedRepos = async () => {
    try {
      const response = await apiClient.listCachedRepos()
      setCachedRepos(response.data.repositories || [])
    } catch (error) {
      console.error('Failed to load cached repos:', error)
    }
  }

  const handleAnalysisComplete = (repoId: string) => {
    setSelectedRepoId(repoId)
    setCurrentView('view')
    loadCachedRepos() // Refresh list
  }

  const handleSelectRepo = (repoId: string) => {
    setSelectedRepoId(repoId)
    setCurrentView('view')
    setBrowsePath('') // Reset path when selecting new repo
  }

  const handleViewChange = (view: ViewType) => {
    setCurrentView(view)
    // If switching to view/search/ask without a repo, try to use first cached repo
    if ((view === 'view' || view === 'search' || view === 'ask') && !selectedRepoId && cachedRepos.length > 0) {
      setSelectedRepoId(cachedRepos[0].id)
    }
  }

  const handleSearchResultClick = (filePath: string) => {
    // Navigate to view and set the path
    setCurrentView('view')
    setBrowsePath(filePath)
  }

  const renderContent = () => {
    switch (currentView) {
      case 'analyze':
        return (
          <div className="App-content-section">
            <h1 className="App-content-title">Analyze New Repository</h1>
            <RepoAnalyzer onAnalysisComplete={handleAnalysisComplete} />
          </div>
        )
      case 'view':
        return selectedRepoId ? (
          <div className="App-content-section">
            <h1 className="App-content-title">{repoName || 'View Repository'}</h1>
            <BrowseView repoId={selectedRepoId} initialPath={browsePath} />
          </div>
        ) : (
          <div className="App-content-section">
            <h1 className="App-content-title">View Repository</h1>
            <CacheBrowser onSelectRepo={handleSelectRepo} />
          </div>
        )
      case 'search':
        return selectedRepoId ? (
          <div className="App-content-section">
            <h1 className="App-content-title">Search {repoName || 'Repository'}</h1>
            <SearchBar repoId={selectedRepoId} onResultClick={handleSearchResultClick} />
          </div>
        ) : (
          <div className="App-content-section">
            <h1 className="App-content-title">Search</h1>
            <p>Please select a repository first.</p>
          </div>
        )
      case 'ask':
        return selectedRepoId ? (
          <div className="App-content-section">
            <h1 className="App-content-title">Ask {repoName || 'Repository'}</h1>
            <QAInterface key={selectedRepoId} repoId={selectedRepoId} />
          </div>
        ) : (
          <div className="App-content-section">
            <h1 className="App-content-title">Ask</h1>
            <p>Please select a repository first.</p>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="App">
      <Sidebar
        currentView={currentView}
        onViewChange={handleViewChange}
        selectedRepoId={selectedRepoId}
        cachedRepos={cachedRepos}
        onSelectRepo={handleSelectRepo}
        onRefreshRepos={loadCachedRepos}
      />
      <main className="App-main">
        {renderContent()}
      </main>
    </div>
  )
}

export default App

