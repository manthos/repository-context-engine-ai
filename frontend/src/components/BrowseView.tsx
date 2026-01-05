import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { apiClient } from '../services/api'
import './BrowseView.css'

interface BrowseViewProps {
  repoId: string
  initialPath?: string
}

interface BrowseItem {
  name: string
  type: 'file' | 'folder'
  path: string
  has_summary: boolean
}

interface BrowseResponse {
  type: 'file' | 'folder'
  path: string
  name?: string
  items?: BrowseItem[]
  content?: string
  summary?: string
  summary_exists?: boolean
}

const BrowseView: React.FC<BrowseViewProps> = ({ repoId, initialPath }) => {
  const [currentPath, setCurrentPath] = useState<string>(initialPath || '')
  const [selectedItem, setSelectedItem] = useState<BrowseResponse | null>(null)
  const [data, setData] = useState<BrowseResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pathHistory, setPathHistory] = useState<string[]>([])

  const loadFileForSummary = async (path: string) => {
    try {
      const response = await apiClient.browse(repoId, path)
      setSelectedItem(response.data)
    } catch (err) {
      console.error('Error loading file/folder for summary:', err)
    }
  }

  useEffect(() => {
    loadPath(currentPath)
  }, [repoId, currentPath])

  // Handle initial path when component mounts or initialPath changes
  useEffect(() => {
    if (initialPath !== undefined) {
      const pathParts = initialPath.split('/').filter(p => p)
      
      // Always load the file/folder for summary display immediately
      loadFileForSummary(initialPath)
      
      if (pathParts.length > 0) {
        // Check if it's likely a file (has extension)
        const lastPart = pathParts[pathParts.length - 1]
        const isFile = lastPart.includes('.')
        
        if (isFile && pathParts.length > 1) {
          // Navigate to parent directory to show folder structure
          const parentPath = pathParts.slice(0, -1).join('/')
          if (parentPath !== currentPath) {
            setCurrentPath(parentPath)
          }
        } else {
          // It's a folder or root file, navigate to it
          if (initialPath !== currentPath) {
            setCurrentPath(initialPath)
          }
        }
      } else {
        // Empty path means root
        if (currentPath !== '') {
          setCurrentPath('')
        }
      }
    }
  }, [initialPath, repoId])

  // When data changes, select it for summary display (unless we have a pending file selection)
  useEffect(() => {
    if (data && !initialPath) {
      setSelectedItem(data)
    } else if (data && initialPath) {
      // If we have initialPath, check if current data matches it
      // If not, we'll load it separately via loadFileForSummary
      if (data.path === initialPath) {
        setSelectedItem(data)
      }
    }
  }, [data, initialPath])

  const loadPath = async (path: string) => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.browse(repoId, path)
      setData(response.data)
      
      // If we don't have an initialPath or the current path matches initialPath,
      // select the current data for summary
      if (!initialPath || path === initialPath) {
        setSelectedItem(response.data)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load path')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const navigateToPath = async (path: string) => {
    // Special handling for parent directory ".."
    if (path === ".." || path === "") {
      navigateToParent()
      return
    }
    setPathHistory([...pathHistory, currentPath])
    
    // Check if it's a file or folder
    const pathParts = path.split('/').filter(p => p)
    const lastPart = pathParts[pathParts.length - 1]
    const isFile = lastPart.includes('.')
    
    if (isFile) {
      // For files, stay in current directory but load file for summary
      try {
        const response = await apiClient.browse(repoId, path)
        setSelectedItem(response.data)
      } catch (err) {
        console.error('Error loading file:', err)
      }
    } else {
      // For folders, navigate to them
      setCurrentPath(path)
    }
  }

  const navigateBack = () => {
    if (pathHistory.length > 0) {
      const previousPath = pathHistory[pathHistory.length - 1]
      setPathHistory(pathHistory.slice(0, -1))
      setCurrentPath(previousPath)
    }
  }

  const navigateToParent = () => {
    if (currentPath) {
      const parts = currentPath.split('/').filter(p => p)
      if (parts.length > 0) {
        parts.pop()
        setPathHistory([...pathHistory, currentPath])
        setCurrentPath(parts.join('/'))
      } else {
        setPathHistory([...pathHistory, currentPath])
        setCurrentPath('')
      }
    }
  }

  if (loading && !data) return <div className="BrowseView-loading">Loading...</div>
  if (error && !data) return <div className="BrowseView-error">Error: {error}</div>
  if (!data) return <div>No data available</div>

  return (
    <div className="BrowseView">
      <div className="BrowseView-container">
        {/* Left Column: File Explorer */}
        <div className="BrowseView-explorer">
          <div className="BrowseView-explorer-header">
            <div className="BrowseView-navigation">
              <button onClick={navigateBack} disabled={pathHistory.length === 0}>
                ← Back
              </button>
              <button onClick={navigateToParent} disabled={!currentPath}>
                ↑ Parent
              </button>
            </div>
            <div className="BrowseView-path">/{currentPath || 'root'}</div>
          </div>
          
          {data.type === 'folder' && data.items && data.items.length > 0 ? (
            <div className="BrowseView-items">
              <ul>
                {data.items.map((item, index) => {
                  const isSelected = selectedItem && (
                    selectedItem.path === item.path || 
                    (selectedItem.type === 'file' && selectedItem.path === item.path)
                  )
                  return (
                  <li 
                    key={item.path || `item-${index}`} 
                    className={`BrowseView-item ${isSelected ? 'selected' : ''}`}
                  >
                    <span
                      className={`BrowseView-item-icon ${item.type === 'folder' ? 'folder' : 'file'}`}
                    >
                      {item.name === '..' ? '⬆️' : item.type === 'folder' ? '📁' : '📄'}
                    </span>
                    <button
                      className="BrowseView-item-button"
                      onClick={() => navigateToPath(item.path)}
                    >
                      {item.name}
                    </button>
                    {item.has_summary && (
                      <span className="BrowseView-item-badge" title="Has summary">
                        ✓
                      </span>
                    )}
                  </li>
                  )
                })}
              </ul>
            </div>
          ) : data.type === 'folder' ? (
            <div className="BrowseView-empty">Folder is empty</div>
          ) : null}
        </div>

        {/* Right Column: Summary Display */}
        <div className="BrowseView-summary-panel">
          {selectedItem && (
            <>
              <div className="BrowseView-summary-header">
                <h2 className="BrowseView-summary-title">
                  {selectedItem.type === 'file' ? selectedItem.name : selectedItem.path || 'root'}
                </h2>
                {selectedItem.type === 'file' && (
                  <div className="BrowseView-summary-path">{selectedItem.path}</div>
                )}
              </div>
              
              <div className="BrowseView-summary-content-wrapper">
                {selectedItem.summary ? (
                  <div className="BrowseView-markdown">
                    <ReactMarkdown>{selectedItem.summary}</ReactMarkdown>
                  </div>
                ) : selectedItem.type === 'file' && selectedItem.summary_exists === false ? (
                  <div className="BrowseView-summary-missing">
                    Summary has not been generated for this file yet.
                  </div>
                ) : selectedItem.type === 'folder' ? (
                  <div className="BrowseView-summary-missing">
                    Select a file or folder to view its summary.
                  </div>
                ) : (
                  <div className="BrowseView-summary-missing">
                    No summary available.
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default BrowseView

