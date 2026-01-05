export interface RepoNode {
  name: string
  type: 'file' | 'folder'
  path: string
  summary: string
  children: RepoNode[]
}

export interface TaskStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result_id: string | null
}

export interface SearchResult {
  path: string
  score: number
  summary_snippet: string
}

export interface QAResponse {
  answer: string
  sources: string[]
}

