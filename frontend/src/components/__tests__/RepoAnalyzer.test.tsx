import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import RepoAnalyzer from '../RepoAnalyzer'
import { apiClient } from '../../services/api'

vi.mock('../../services/api')

describe('RepoAnalyzer', () => {
  it('renders the analyze form', () => {
    render(<RepoAnalyzer onAnalysisComplete={vi.fn()} />)
    expect(screen.getByPlaceholderText(/Enter repository URL/)).toBeInTheDocument()
    expect(screen.getByText('Analyze')).toBeInTheDocument()
  })

  it('disables button when input is empty', () => {
    render(<RepoAnalyzer onAnalysisComplete={vi.fn()} />)
    const button = screen.getByText('Analyze')
    expect(button).toBeDisabled()
  })
})

