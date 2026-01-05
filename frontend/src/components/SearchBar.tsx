import React, { useState } from 'react'
import { apiClient } from '../services/api'
import { SearchResult } from '../types'
import './SearchBar.css'

interface SearchBarProps {
  repoId: string | null
  onResultClick?: (filePath: string) => void
}

const SearchBar: React.FC<SearchBarProps> = ({ repoId, onResultClick }) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query')
      return
    }

    if (!repoId) {
      setError('Please select a repository first')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.search(query, repoId)
      setResults(response.data)
      if (response.data.length === 0) {
        setError('No results found')
      }
    } catch (error: any) {
      console.error('Search error:', error)
      setError(error.response?.data?.detail || 'Search failed')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="SearchBar">
      <div className="SearchBar-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search repository summaries..."
          className="SearchBar-input"
          disabled={!repoId}
        />
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim() || !repoId}
          className="SearchBar-button"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      {error && (
        <div className="SearchBar-error">{error}</div>
      )}
      {results.length > 0 && (
        <div className="SearchBar-results">
          <h3>Found {results.length} result(s)</h3>
          {results.map((result, index) => (
            <div 
              key={index} 
              className="SearchBar-result"
              onClick={() => {
                if (onResultClick && result.path) {
                  onResultClick(result.path)
                }
              }}
              style={{ cursor: onResultClick && result.path ? 'pointer' : 'default' }}
            >
              <div className="SearchBar-result-header">
                <span className="SearchBar-result-path">{result.path || '(root)'}</span>
                <span className="SearchBar-result-score">Score: {result.score.toFixed(2)}</span>
              </div>
              <div className="SearchBar-result-snippet">{result.summary_snippet}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchBar

