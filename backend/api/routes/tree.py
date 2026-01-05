"""Tree endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.node import RepoNode
from backend.db.base import get_db
from backend.models.repository import Repository
from backend.models.node import Node
from typing import List, Dict

router = APIRouter()


def build_tree(nodes: List[Node], parent_id: str | None = None) -> List[RepoNode]:
    """Build recursive tree structure."""
    children = [n for n in nodes if n.parent_id == parent_id]
    result = []
    
    for node in children:
        child_nodes = build_tree(nodes, node.id)
        result.append(RepoNode(
            name=node.name,
            type=node.type,
            path=node.path,
            summary=node.summary or "",
            children=child_nodes,
        ))
    
    return result


@router.get("/tree/{repo_id}", response_model=RepoNode)
async def get_tree(repo_id: str, db: Session = Depends(get_db)):
    """Get the recursive summary tree."""
    # Check if repository exists
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get all nodes for this repository
    nodes = db.query(Node).filter(Node.repo_id == repo_id).all()
    
    if not nodes:
        raise HTTPException(status_code=404, detail="Repository tree not found")
    
    # Find root node explicitly (path="" and parent_id=None)
    root_node = None
    for node in nodes:
        if node.path == "" and node.parent_id is None:
            root_node = node
            break
    
    if not root_node:
        # Fallback: find any node with parent_id=None (should be root)
        root_nodes = [n for n in nodes if n.parent_id is None]
        if root_nodes:
            root_node = root_nodes[0]
    
    if not root_node:
        raise HTTPException(status_code=404, detail="Root node not found")
    
    # Build full tree starting from root
    tree_nodes = build_tree(nodes, root_node.id)
    
    # Return root node with children
    return RepoNode(
        name=root_node.name,
        type=root_node.type,
        path=root_node.path,
        summary=root_node.summary or "",
        children=tree_nodes,
    )

