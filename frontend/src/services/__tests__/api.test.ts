import { describe, it, expect } from 'vitest'

describe('API Client', () => {
  it('exports apiClient with all required methods', async () => {
    // Dynamic import to avoid axios mock issues during module initialization
    const { apiClient } = await import('../api')
    
    expect(apiClient).toBeDefined()
    expect(apiClient.analyze).toBeDefined()
    expect(apiClient.getStatus).toBeDefined()
    expect(apiClient.getTree).toBeDefined()
    expect(apiClient.search).toBeDefined()
    expect(apiClient.askQuestion).toBeDefined()
    expect(apiClient.browse).toBeDefined()
    expect(apiClient.listCachedRepos).toBeDefined()
  })
})
