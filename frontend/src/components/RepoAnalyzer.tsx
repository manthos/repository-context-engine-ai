import React, { useState } from 'react'
import { apiClient } from '../services/api'
import './RepoAnalyzer.css'

interface RepoAnalyzerProps {
  onAnalysisComplete: (repoId: string) => void
}

const RepoAnalyzer: React.FC<RepoAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [repoUrl, setRepoUrl] = useState('')
  const [passphrase, setPassphrase] = useState('')
  const [, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!repoUrl.trim() || !passphrase.trim()) {
      setError('Please enter both repository URL and passphrase')
      return
    }

    setLoading(true)
    setStatus('Starting analysis...')
    setError(null)
    setProgress(0)

    try {
      const response = await apiClient.analyze(repoUrl, 3, passphrase)
      const { task_id } = response.data
      setTaskId(task_id)

      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await apiClient.getStatus(task_id)
          const taskStatus = statusResponse.data
          // Use status_message if available, otherwise use status
          setStatus(taskStatus.status_message || taskStatus.status)
          setProgress(taskStatus.progress)

          if (taskStatus.status === 'completed' && taskStatus.result_id) {
            clearInterval(pollInterval)
            setLoading(false)
            onAnalysisComplete(taskStatus.result_id)
            setStatus('Analysis completed!')
            setError(null)
          } else if (taskStatus.status === 'failed') {
            clearInterval(pollInterval)
            setLoading(false)
            setError(taskStatus.error_message || 'Analysis failed')
            setStatus('')
          }
        } catch (error) {
          console.error('Error polling status:', error)
          clearInterval(pollInterval)
          setLoading(false)
          setError('Error checking analysis status')
        }
      }, 2000)
    } catch (error: any) {
      // Only log unexpected errors (5xx, network errors) to console
      // 4xx errors (validation) are expected and handled gracefully in UI
      const status = error?.response?.status
      if (!status || status >= 500) {
        console.error('Unexpected error starting analysis:', error)
      }
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error'
      setLoading(false)
      setError(errorMessage)
      setStatus('')
    }
  }

  return (
    <div className="RepoAnalyzer">
      <div className="RepoAnalyzer-form">
        <input
          type="text"
          name="repo-url"
          id="repo-url"
          autoComplete="url"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter repository URL (e.g., https://github.com/user/repo)"
          disabled={loading}
          className="RepoAnalyzer-input"
        />
        <input
          type="password"
          name="repo-passphrase"
          id="repo-passphrase"
          autoComplete="current-password"
          value={passphrase}
          onChange={(e) => setPassphrase(e.target.value)}
          placeholder="Enter your passphrase"
          disabled={loading}
          className="RepoAnalyzer-input"
        />
        <p className="RepoAnalyzer-passphrase-help">
          Type your passphrase to be able to crawl a GitHub repository (under 10KB). 
          The passphrases for evaluators are the name of our class repository followed by the number 1, 2 or 3 
          (one of these numbers will work for you only, so try each).
        </p>
        <div className="RepoAnalyzer-form-row">
          <button
            onClick={handleAnalyze}
            disabled={loading || !repoUrl.trim() || !passphrase.trim()}
            className="RepoAnalyzer-button"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>
      {error && (
        <div className="RepoAnalyzer-error">
          <strong>Error:</strong> {error}
        </div>
      )}
      {status && !error && (
        <div className="RepoAnalyzer-status">
          <p>Status: {status}</p>
          {progress > 0 && (
            <div className="RepoAnalyzer-progress">
              <div
                className="RepoAnalyzer-progress-bar"
                style={{ '--progress-width': `${progress}%` } as React.CSSProperties}
              />
              <span>{progress}%</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default RepoAnalyzer

