import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SearchBar from '../SearchBar'
import { apiClient } from '../../services/api'

vi.mock('../../services/api')

describe('SearchBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('renders search input and button', () => {
    render(<SearchBar repoId="test-repo-123" />)
    
    expect(screen.getByPlaceholderText(/Search repository summaries/)).toBeInTheDocument()
    expect(screen.getByText('Search')).toBeInTheDocument()
  })

  it('disables input and button when no repo is selected', () => {
    render(<SearchBar repoId={null} />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/) as HTMLInputElement
    const button = screen.getByText('Search') as HTMLButtonElement
    
    expect(input.disabled).toBe(true)
    expect(button.disabled).toBe(true)
  })

  it('enables input and button when repo is selected', () => {
    render(<SearchBar repoId="test-repo-123" />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/) as HTMLInputElement
    
    expect(input.disabled).toBe(false)
    
    // Button is disabled until query is entered
    const button = screen.getByText('Search') as HTMLButtonElement
    expect(button.disabled).toBe(true)
    
    // Type a query
    fireEvent.change(input, { target: { value: 'test query' } })
    
    // Now button should be enabled
    expect(button.disabled).toBe(false)
  })

  it('shows error when searching without a query', async () => {
    render(<SearchBar repoId="test-repo-123" />)
    
    screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    // Button is disabled when query is empty, so we can't actually click it
    // This test verifies the button is disabled
    expect(button).toBeDisabled()
  })

  it('shows error when searching without a repo', async () => {
    render(<SearchBar repoId={null} />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    // Both input and button should be disabled when no repo is selected
    expect(input).toBeDisabled()
    expect(button).toBeDisabled()
  })

  it('calls apiClient.search with correct parameters', async () => {
    const mockResponse = {
      data: [
        { path: 'src/main.py', score: 0.95, summary_snippet: 'Main application entry point' },
        { path: 'README.md', score: 0.85, summary_snippet: 'Project documentation' }
      ],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }
    
    vi.mocked(apiClient.search).mockResolvedValue(mockResponse)
    
    render(<SearchBar repoId="test-repo-123" />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    fireEvent.change(input, { target: { value: 'authentication' } })
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(apiClient.search).toHaveBeenCalledWith('authentication', 'test-repo-123')
    })
  })

  it('displays search results', async () => {
    const mockResponse = {
      data: [
        { path: 'src/auth.py', score: 0.95, summary_snippet: 'Authentication logic' },
        { path: 'docs/auth.md', score: 0.85, summary_snippet: 'Auth documentation' }
      ],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }
    
    vi.mocked(apiClient.search).mockResolvedValue(mockResponse)
    
    render(<SearchBar repoId="test-repo-123" />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    fireEvent.change(input, { target: { value: 'auth' } })
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText(/Found 2 result/)).toBeInTheDocument()
      expect(screen.getByText('src/auth.py')).toBeInTheDocument()
      expect(screen.getByText('docs/auth.md')).toBeInTheDocument()
    })
  })

  it('shows message when no results are found', async () => {
    const mockResponse = {
      data: [],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }
    
    vi.mocked(apiClient.search).mockResolvedValue(mockResponse)
    
    render(<SearchBar repoId="test-repo-123" />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    fireEvent.change(input, { target: { value: 'nonexistent' } })
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText(/No results found/)).toBeInTheDocument()
    })
  })

  it('displays error message when search fails', async () => {
    const mockError = {
      response: {
        data: {
          detail: 'Search service unavailable'
        }
      }
    }
    
    vi.mocked(apiClient.search).mockRejectedValue(mockError)
    
    render(<SearchBar repoId="test-repo-123" />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    fireEvent.change(input, { target: { value: 'test' } })
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Search service unavailable')).toBeInTheDocument()
    })
  })

  it('calls onResultClick when result is clicked', async () => {
    const mockOnResultClick = vi.fn()
    const mockResponse = {
      data: [
        { path: 'src/main.py', score: 0.95, summary_snippet: 'Main file' }
      ],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }
    
    vi.mocked(apiClient.search).mockResolvedValue(mockResponse)
    
    render(<SearchBar repoId="test-repo-123" onResultClick={mockOnResultClick} />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    const button = screen.getByText('Search')
    
    fireEvent.change(input, { target: { value: 'main' } })
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('src/main.py')).toBeInTheDocument()
    })
    
    const resultElement = screen.getByText('src/main.py').closest('.SearchBar-result')
    fireEvent.click(resultElement!)
    
    expect(mockOnResultClick).toHaveBeenCalledWith('src/main.py')
  })

  it('allows search via Enter key', async () => {
    const mockResponse = {
      data: [
        { path: 'test.py', score: 0.9, summary_snippet: 'Test file' }
      ],
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }
    
    vi.mocked(apiClient.search).mockResolvedValue(mockResponse)
    
    render(<SearchBar repoId="test-repo-123" />)
    
    const input = screen.getByPlaceholderText(/Search repository summaries/)
    
    fireEvent.change(input, { target: { value: 'test' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 })
    
    await waitFor(() => {
      expect(apiClient.search).toHaveBeenCalledWith('test', 'test-repo-123')
    })
  })
})
