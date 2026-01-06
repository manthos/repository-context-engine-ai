"""Recursive analyzer for repository summarization."""
import os
import uuid
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from backend.models.repository import Repository, RepositoryStatus
from backend.models.node import Node
from backend.models.task import Task, TaskStatus
from backend.services.git_service import (
    clone_repository, get_file_tree, read_file_content, cleanup_repository,
    get_repo_cache_path, get_folder_structure
)
from backend.services.llm_service import get_llm_service
from backend.services.embedding_service import create_embedding
from backend.services.summary_files import (
    summary_exists, read_summary, write_summary, get_summary_file_path
)
from backend.services.passphrase_service import record_repository_crawl

# Configure logging
logger = logging.getLogger(__name__)


def start_analysis(task_id: str, repo_url: str, depth: int, db: Session, passphrase: str = None):
    """
    Start recursive analysis of a repository.
    
    This function runs in the background and updates task status.
    """
    repo_path = None
    repo = None
    repo_id = None
    try:
        logger.info(f"Starting analysis for task {task_id}, repo: {repo_url}")
        print(f"[ANALYZER] Starting analysis: {repo_url}, task: {task_id}")  # Backup logging
        
        # Create or get repository
        repo = db.query(Repository).filter(Repository.url == repo_url).first()
        if not repo:
            repo_id = str(uuid.uuid4())
            repo = Repository(id=repo_id, url=repo_url, status=RepositoryStatus.PROCESSING)
            db.add(repo)
            db.commit()
        else:
            repo_id = repo.id
            # Update status to processing
            repo.status = RepositoryStatus.PROCESSING
            db.commit()
        
        # Create task
        task = Task(
            id=task_id,
            repo_id=repo_id,
            status=TaskStatus.PROCESSING.value,
            progress=0,
            status_message="Getting repository...",
        )
        db.add(task)
        db.commit()
        
        # Clone repository
        task.status_message = "Cloning repository..."
        db.commit()
        logger.info(f"Cloning repository from {repo_url}")
        repo_path = clone_repository(repo_url)
        logger.info(f"Repository cloned to {repo_path}")
        
        # Get repository name for root summary naming
        cache_path = get_repo_cache_path(repo_url)
        repo_name = cache_path.name
        
        # Get file tree
        file_tree = get_file_tree(repo_path)
        total_files = len([f for f in file_tree if f["type"] == "file"])
        logger.info(f"Found {total_files} files in repository")
        
        # Handle empty repository
        if not file_tree or total_files == 0:
            # Create a minimal root node
            root_summary = f"This repository ({repo_url}) appears to be empty or contains no analyzable files."
            # Save root summary to file with repo name
            root_summary_path = get_summary_file_path(repo_path, "", "folder", repo_name)
            root_summary_path.parent.mkdir(parents=True, exist_ok=True)
            root_summary_path.write_text(root_summary, encoding="utf-8")
            
            root_node = Node(
                id=str(uuid.uuid4()),
                repo_id=repo_id,
                path="",
                name=os.path.basename(repo_url.rstrip("/")) or "root",
                type="folder",
                summary=root_summary,
                parent_id=None,
            )
            db.add(root_node)
            repo.status = RepositoryStatus.COMPLETED
            task.status = TaskStatus.COMPLETED.value
            task.progress = 100
            task.result_id = repo_id
            db.commit()
            
            # Record passphrase usage for successful crawl
            if passphrase:
                record_repository_crawl(db, passphrase, repo_id)
            
            return
        
        # Process files (leaves first)
        processed = 0
        llm_service = get_llm_service()
        
        task.status_message = f"Processing {total_files} files..."
        db.commit()
        
        for item in file_tree:
            if item["type"] == "file":
                try:
                    file_path = os.path.join(repo_path, item["path"])
                    content = read_file_content(file_path)
                    
                    if content:
                        # Update status message
                        task.status_message = f"Processing file: {item['path']}"
                        db.commit()
                        logger.info(f"Processing file: {item['path']}, size: {len(content)} chars")
                        
                        # Filesystem cache takes precedence: check if summary file exists
                        # If file doesn't exist, re-summarize even if DB has entry
                        existing_summary = read_summary(repo_path, item["path"], "file", repo_name)
                        
                        if existing_summary:
                            # Use existing summary from filesystem
                            logger.info(f"Using cached summary for {item['path']}")
                            summary = existing_summary
                        else:
                            # Generate new summary
                            logger.info(f"Generating new summary for {item['path']}")
                            import asyncio
                            try:
                                loop = asyncio.get_event_loop()
                            except RuntimeError:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                            
                            logger.info(f"Calling LLM service for {item['path']}")
                        print(f"[ANALYZER] Calling LLM for: {item['path']}")  # Backup logging
                        summary = loop.run_until_complete(
                            llm_service.generate_summary(content, item_type="file")
                        )
                        logger.info(f"LLM returned summary for {item['path']}, length: {len(summary)} chars")
                        print(f"[ANALYZER] LLM returned summary, length: {len(summary)}")  # Backup logging
                        
                        # Save summary to file
                        write_summary(repo_path, item["path"], "file", summary, repo_name)
                        logger.info(f"Saved summary to filesystem for {item['path']}")
                            Node.path == item["path"]
                        ).first()
                        
                        if existing_node:
                            # Update existing node
                            existing_node.summary = summary
                            existing_node.embedding = embedding
                        else:
                            # Create new node
                            node_id = str(uuid.uuid4())
                            node = Node(
                                id=node_id,
                                repo_id=repo_id,
                                path=item["path"],
                                name=os.path.basename(item["path"]),
                                type="file",
                                summary=summary,
                                embedding=embedding,
                            )
                            db.add(node)
                        
                        processed += 1
                        
                        # Update progress (avoid division by zero)
                        if total_files > 0:
                            progress = int((processed / total_files) * 80)  # Files take 80% of progress
                        else:
                            progress = 80
                        task.progress = progress
                        db.commit()
                        logger.info(f"Successfully processed and committed {item['path']}")
                
                except Exception as file_error:
                    logger.error(f"Error processing file {item['path']}: {str(file_error)}", exc_info=True)
                    db.rollback()
                    # Continue with next file
                    continue
        
        # Process folders bottom-up
        folders = [f for f in file_tree if f["type"] == "folder"]
        folders.sort(key=lambda x: x["path"].count("/"), reverse=True)  # Deepest first
        
        task.status_message = f"Processing {len(folders)} folders..."
        db.commit()
        
        for folder in folders:
            # Update status message
            folder_display = folder["path"] if folder["path"] else "root"
            task.status_message = f"Processing folder: {folder_display}"
            db.commit()
            
            # Filesystem cache takes precedence: check if summary file exists
            # If file doesn't exist, re-summarize even if DB has entry
            existing_summary = read_summary(repo_path, folder["path"], "folder", repo_name)
            
            if existing_summary:
                # Use existing summary
                folder_summary = existing_summary
            else:
                # Get folder structure (list of files/subfolders)
                folder_structure = get_folder_structure(repo_path, folder["path"])
                
                # Get child summaries (from DB or files)
                child_nodes = db.query(Node).filter(
                    Node.repo_id == repo_id,
                    Node.path.like(f"{folder['path']}/%")
                ).all()
                
                # Build context with folder structure and child summaries
                context_parts = []
                
                if folder_structure:
                    context_parts.append(f"Folder Structure:\n{folder_structure}")
                
                # Also check for child summaries in files
                child_summaries_list = []
                for child_node in child_nodes:
                    if child_node.summary:
                        child_summaries_list.append(f"{child_node.path}: {child_node.summary}")
                    else:
                        # Try reading from file
                        file_summary = read_summary(repo_path, child_node.path, child_node.type, repo_name)
                        if file_summary:
                            child_summaries_list.append(f"{child_node.path}: {file_summary}")
                
                if child_summaries_list:
                    context_parts.append("Child Summaries:\n" + "\n".join(child_summaries_list))
                
                folder_context = "\n\n".join(context_parts) if context_parts else f"Folder: {folder['path']}"
                
                # Generate folder summary
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                folder_summary = loop.run_until_complete(
                    llm_service.generate_summary(
                        folder_context,
                        context=None,
                        item_type="folder"
                    )
                )
                
                # Save summary to file (in parent directory)
                write_summary(repo_path, folder["path"], "folder", folder_summary, repo_name)
            
            # Check if node already exists in DB
            existing_node = db.query(Node).filter(
                Node.repo_id == repo_id,
                Node.path == folder["path"]
            ).first()
            
            if existing_node:
                # Update existing node
                existing_node.summary = folder_summary
            else:
                # Create folder node
                node_id = str(uuid.uuid4())
                node = Node(
                    id=node_id,
                    repo_id=repo_id,
                    path=folder["path"],
                    name=os.path.basename(folder["path"]) or "root",
                    type="folder",
                    summary=folder_summary,
                )
                db.add(node)
        
        # Generate root summary
        task.status_message = "Generating repository summary..."
        task.progress = 90
        db.commit()
        
        root_summary_path = get_summary_file_path(repo_path, "", "folder", repo_name)
        existing_root_summary = None
        if root_summary_path.exists():
            try:
                existing_root_summary = root_summary_path.read_text(encoding="utf-8")
            except Exception:
                pass
        
        if existing_root_summary:
            root_summary = existing_root_summary
        else:
            # Get root folder structure
            root_structure = get_folder_structure(repo_path, "")
            
            # Get ALL summaries (files and folders)
            all_nodes = db.query(Node).filter(
                Node.repo_id == repo_id,
                Node.path != ""  # Exclude root itself
            ).all()
            
            # Organize summaries by type
            folder_summaries = []
            file_summaries = []
            
            for n in all_nodes:
                summary_text = n.summary
                if not summary_text:
                    # Try reading from file
                    file_summary = read_summary(repo_path, n.path, n.type, repo_name)
                    if file_summary:
                        summary_text = file_summary
                
                if summary_text:
                    if n.type == "folder":
                        folder_summaries.append(f"## Folder: {n.path}\n{summary_text}")
                    else:
                        file_summaries.append(f"### File: {n.path}\n{summary_text}")
            
            # Build comprehensive root context
            context_parts = []
            
            if root_structure:
                context_parts.append(f"Repository Structure:\n{root_structure}")
            
            if folder_summaries:
                context_parts.append("## Folder Summaries:\n" + "\n\n".join(folder_summaries))
            
            if file_summaries:
                context_parts.append("## File Summaries:\n" + "\n\n".join(file_summaries))
            
            root_context = "\n\n".join(context_parts)
            
            # Handle case where no summaries exist
            if not root_context.strip():
                root_context = "This repository structure and its contents."
            
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            root_summary = loop.run_until_complete(
                llm_service.generate_summary(
                    root_context,
                    context=None,
                    item_type="folder"
                )
            )
            
            # Save root summary to file with repo name
            root_summary_path.parent.mkdir(parents=True, exist_ok=True)
            root_summary_path.write_text(root_summary, encoding="utf-8")
        
        # Check if root node exists
        existing_root = db.query(Node).filter(
            Node.repo_id == repo_id,
            Node.path == "",
            Node.parent_id.is_(None)
        ).first()
        
        if existing_root:
            existing_root.summary = root_summary
            existing_root.name = repo_name or os.path.basename(repo_url.rstrip("/")) or "root"
        else:
            # Create root node
            root_node = Node(
                id=str(uuid.uuid4()),
                repo_id=repo_id,
                path="",
                name=repo_name or os.path.basename(repo_url.rstrip("/")) or "root",
                type="folder",
                summary=root_summary,
                parent_id=None,
            )
            db.add(root_node)
        
        # Update repository and task status
        repo.status = RepositoryStatus.COMPLETED
        task.status = TaskStatus.COMPLETED.value
        task.progress = 100
        task.status_message = "Analysis completed!"
        task.result_id = repo_id
        
        # Record passphrase usage for successful crawl
        if passphrase:
            record_repository_crawl(db, passphrase, repo_id)
        db.commit()
        
    except Exception as e:
        logger.error(f"Analysis failed for task {task_id}: {str(e)}", exc_info=True)
        # Rollback any pending transaction
        db.rollback()
        
        # Update task status to failed
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = TaskStatus.FAILED.value
                task.error_message = str(e)
                db.commit()
            
            # Update repository status
            if repo and repo_id:
                repo = db.query(Repository).filter(Repository.id == repo_id).first()
                if repo:
                    repo.status = RepositoryStatus.FAILED
                    db.commit()
        except Exception as cleanup_error:
            logger.error(f"Cleanup failed: {str(cleanup_error)}")
            db.rollback()
    finally:
        # No cleanup - repositories are cached permanently
        pass

