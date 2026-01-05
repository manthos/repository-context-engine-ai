import React, { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { apiClient } from '../services/api'
import { RepoNode } from '../types'
import './TreeView.css'

interface TreeViewProps {
  repoId: string
}

const TreeView: React.FC<TreeViewProps> = ({ repoId }) => {
  const [tree, setTree] = useState<RepoNode | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadTree()
  }, [repoId])

  const loadTree = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getTree(repoId)
      setTree(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load tree')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const toggleExpanded = (path: string) => {
    const newExpanded = new Set(expanded)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpanded(newExpanded)
  }

  const renderNode = (node: RepoNode, level: number = 0) => {
    const isExpanded = expanded.has(node.path)
    const hasChildren = node.children && node.children.length > 0

    return (
      <div key={node.path} className="TreeView-node" style={{ marginLeft: `${level * 20}px` }}>
        <div
          className="TreeView-node-header"
          onClick={() => hasChildren && toggleExpanded(node.path)}
        >
          <span className="TreeView-node-icon">
            {hasChildren ? (isExpanded ? '📂' : '📁') : '📄'}
          </span>
          <span className="TreeView-node-name">{node.name}</span>
          <span className="TreeView-node-type">{node.type}</span>
        </div>
        {node.summary && (
          <div className="TreeView-node-summary">
            <ReactMarkdown>{node.summary}</ReactMarkdown>
          </div>
        )}
        {hasChildren && isExpanded && (
          <div className="TreeView-node-children">
            {node.children.map((child) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  if (loading) return <div>Loading tree...</div>
  if (error) return <div className="error">{error}</div>
  if (!tree) return <div>No tree data available</div>

  return (
    <div className="TreeView">
      <h2>Repository Tree</h2>
      {renderNode(tree)}
    </div>
  )
}

export default TreeView

