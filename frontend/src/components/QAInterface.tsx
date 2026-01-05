import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { apiClient } from '../services/api'
import { QAResponse } from '../types'
import './QAInterface.css'

interface QAInterfaceProps {
  repoId: string
}

const QAInterface: React.FC<QAInterfaceProps> = ({ repoId }) => {
  // Debug: Log what props we receive
  console.log('QAInterface rendering with props:', { repoId })
  
  const [question, setQuestion] = useState(() => {
    console.log('Initializing question state to empty string')
    return ''
  })
  const [passphrase, setPassphrase] = useState('')
  const [answer, setAnswer] = useState<QAResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Debug: Log current state
  console.log('Current question state:', question)

  // Clear form when repo changes
  useEffect(() => {
    console.log('QAInterface useEffect triggered - clearing form')
    setQuestion('')
    setPassphrase('')
    setAnswer(null)
    setError(null)
  }, [repoId])

  const handleAsk = async () => {
    if (!question.trim() || !passphrase.trim()) {
      setError('Please enter both question and passphrase')
      return
    }

    setLoading(true)
    setAnswer(null)
    setError(null)

    try {
      const response = await apiClient.askQuestion(repoId, question, passphrase)
      setAnswer(response.data)
    } catch (error: any) {
      console.error('Q&A error:', error)
      const errorMessage = error?.response?.data?.detail || 'Error answering question'
      setError(errorMessage)
      setAnswer(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="QAInterface">
      <div className="QAInterface-form">
        <input
          type="text"
          name="qa-question"
          id="qa-question"
          autoComplete="qa-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ask a question about the repository..."
          className="QAInterface-input"
          disabled={loading}
        />
        <input
          type="password"
          name="qa-passphrase"
          id="qa-passphrase"
          autoComplete="new-password"
          value={passphrase}
          onChange={(e) => setPassphrase(e.target.value)}
          placeholder="Enter your passphrase"
          className="QAInterface-input"
          disabled={loading}
        />
        <button
          onClick={handleAsk}
          disabled={loading || !question.trim() || !passphrase.trim()}
          className="QAInterface-button"
        >
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </div>
      {error && (
        <div className="QAInterface-error">
          <strong>Error:</strong> {error}
        </div>
      )}
      {answer && (
        <div className="QAInterface-answer">
          <h3>Answer:</h3>
          <div className="QAInterface-answer-markdown">
            <ReactMarkdown>{answer.answer}</ReactMarkdown>
          </div>
          {answer.sources.length > 0 && (
            <div className="QAInterface-sources">
              <h4>Sources:</h4>
              <ul>
                {answer.sources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default QAInterface

