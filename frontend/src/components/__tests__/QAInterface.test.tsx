import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import QAInterface from '../QAInterface'
import { apiClient } from '../../services/api'

vi.mock('../../services/api')

describe('QAInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Suppress console logs in tests
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('renders the Q&A form with question and passphrase inputs', () => {
    render(<QAInterface repoId="test-repo-123" />)
    
    expect(screen.getByPlaceholderText(/Ask a question about the repository/)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Enter your passphrase/)).toBeInTheDocument()
    expect(screen.getByText('Ask')).toBeInTheDocument()
  })

  it('clears form when repoId changes', () => {
    const { rerender } = render(<QAInterface repoId="repo-1" />)
    
    const questionInput = screen.getByPlaceholderText(/Ask a question about the repository/) as HTMLInputElement
    const passphraseInput = screen.getByPlaceholderText(/Enter your passphrase/) as HTMLInputElement
    
    // Set some values
    fireEvent.change(questionInput, { target: { value: 'What does this do?' } })
    fireEvent.change(passphraseInput, { target: { value: 'secret123' } })
    
    expect(questionInput.value).toBe('What does this do?')
    expect(passphraseInput.value).toBe('secret123')
    
    // Change repoId - should clear form
    rerender(<QAInterface repoId="repo-2" />)
    
    expect(questionInput.value).toBe('')
    expect(passphraseInput.value).toBe('')
  })

  it('disables button when question or passphrase is empty', () => {
    render(<QAInterface repoId="test-repo-123" />)
    
    const askButton = screen.getByText('Ask')
    
    // Button should be disabled when inputs are empty
    expect(askButton).toBeDisabled()
  })

  it('calls apiClient.askQuestion with correct parameters', async () => {
    const mockResponse = {
      data: {
        answer: 'This is a test repository for demonstration purposes.',
        sources: ['README.md', 'docs/overview.md']
      }
    }
    
    vi.mocked(apiClient.askQuestion).mockResolvedValue(mockResponse)
    
    render(<QAInterface repoId="test-repo-123" />)
    
    const questionInput = screen.getByPlaceholderText(/Ask a question about the repository/)
    const passphraseInput = screen.getByPlaceholderText(/Enter your passphrase/)
    const askButton = screen.getByText('Ask')
    
    fireEvent.change(questionInput, { target: { value: 'What is this repo about?' } })
    fireEvent.change(passphraseInput, { target: { value: 'mypassphrase' } })
    fireEvent.click(askButton)
    
    await waitFor(() => {
      expect(apiClient.askQuestion).toHaveBeenCalledWith(
        'test-repo-123',
        'What is this repo about?',
        'mypassphrase'
      )
    })
  })

  it('displays answer when API call succeeds', async () => {
    const mockResponse = {
      data: {
        answer: 'This is a test repository.',
        sources: ['README.md']
      }
    }
    
    vi.mocked(apiClient.askQuestion).mockResolvedValue(mockResponse)
    
    render(<QAInterface repoId="test-repo-123" />)
    
    const questionInput = screen.getByPlaceholderText(/Ask a question about the repository/)
    const passphraseInput = screen.getByPlaceholderText(/Enter your passphrase/)
    const askButton = screen.getByText('Ask')
    
    fireEvent.change(questionInput, { target: { value: 'What is this?' } })
    fireEvent.change(passphraseInput, { target: { value: 'pass' } })
    fireEvent.click(askButton)
    
    await waitFor(() => {
      expect(screen.getByText('This is a test repository.')).toBeInTheDocument()
    })
  })

  it('displays error message when API call fails', async () => {
    const mockError = {
      response: {
        data: {
          detail: 'Invalid passphrase'
        }
      }
    }
    
    vi.mocked(apiClient.askQuestion).mockRejectedValue(mockError)
    
    render(<QAInterface repoId="test-repo-123" />)
    
    const questionInput = screen.getByPlaceholderText(/Ask a question about the repository/)
    const passphraseInput = screen.getByPlaceholderText(/Enter your passphrase/)
    const askButton = screen.getByText('Ask')
    
    fireEvent.change(questionInput, { target: { value: 'What is this?' } })
    fireEvent.change(passphraseInput, { target: { value: 'wrongpass' } })
    fireEvent.click(askButton)
    
    await waitFor(() => {
      expect(screen.getByText('Invalid passphrase')).toBeInTheDocument()
    })
  })

  it('disables inputs while loading', async () => {
    // Mock a slow API call
    vi.mocked(apiClient.askQuestion).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    )
    
    render(<QAInterface repoId="test-repo-123" />)
    
    const questionInput = screen.getByPlaceholderText(/Ask a question about the repository/) as HTMLInputElement
    const passphraseInput = screen.getByPlaceholderText(/Enter your passphrase/) as HTMLInputElement
    const askButton = screen.getByText('Ask') as HTMLButtonElement
    
    fireEvent.change(questionInput, { target: { value: 'Test question' } })
    fireEvent.change(passphraseInput, { target: { value: 'pass' } })
    fireEvent.click(askButton)
    
    // Check that inputs are disabled during loading
    expect(questionInput.disabled).toBe(true)
    expect(passphraseInput.disabled).toBe(true)
    expect(askButton.disabled).toBe(true)
  })
})
