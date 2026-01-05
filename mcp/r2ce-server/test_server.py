#!/usr/bin/env python3
"""Quick test to verify MCP server can be imported and initialized."""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from server import app
    print("✓ MCP server imports successfully")
    print(f"✓ Server name: {app.name}")
    
    # Test that we can list tools (async, so we'll just check the function exists)
    import inspect
    if hasattr(app, 'list_tools'):
        print("✓ list_tools method exists")
    if hasattr(app, 'call_tool'):
        print("✓ call_tool method exists")
    
    print("\n✓ MCP server is ready!")
    print("\nTo use with MCP client, configure:")
    print(f"  Command: {os.path.abspath('venv/bin/python')}")
    print(f"  Args: [{os.path.abspath('server.py')}]")
    print(f"  Env: R2CE_API_URL=http://localhost:8000/api")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure virtual environment is activated:")
    print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

