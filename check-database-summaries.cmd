cd /space/ml-zoomcamp/aidev/R2CE
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "
from backend.db.base import SessionLocal
from backend.models.repository import Repository
from backend.models.node import Node

db = SessionLocal()
repo = db.query(Repository).filter(Repository.url == 'https://github.com/octocat/Hello-World').first()
if repo:
    print(f'Repository: {repo.url}')
    print(f'Status: {repo.status}')
    nodes = db.query(Node).filter(Node.repo_id == repo.id).all()
    print(f'Total nodes: {len(nodes)}')
    for node in nodes:
        print(f'\n{node.type.upper()}: {node.path}')
        print(f'Summary: {node.summary[:100] if node.summary else \"No summary\"}...')
db.close()
"
