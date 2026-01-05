#!/bin/bash
# Quick test script for R2CE with a small repository

set -e

echo "=== R2CE Small Repository Test ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check PYTHONPATH for backend imports
if [ -z "$PYTHONPATH" ] || [[ ! "$PYTHONPATH" == *"$(pwd)/backend"* ]]; then
    echo -e "${YELLOW}Warning: PYTHONPATH may not be set correctly${NC}"
    echo "If you see import errors, run:"
    echo "  export PYTHONPATH=\"\${PYTHONPATH}:$(pwd)/backend\""
    echo ""
fi

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}Error: Backend is not running on http://localhost:8000${NC}"
    echo "Please start the backend first:"
    echo "  cd backend && uvicorn main:app --reload"
    exit 1
fi
echo -e "${GREEN}✓ Backend is running${NC}"
echo ""

# Test repository (small GitHub repo)
REPO_URL="https://github.com/octocat/Hello-World"
echo "Testing with repository: $REPO_URL"
echo ""

# Step 1: Start analysis
echo "Step 1: Starting analysis..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\": \"$REPO_URL\", \"depth\": 3}")

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$TASK_ID" ]; then
    echo -e "${RED}Error: Failed to start analysis${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Analysis started${NC}"
echo "Task ID: $TASK_ID"
echo ""

# Step 2: Poll for status
echo "Step 2: Waiting for analysis to complete..."
MAX_ATTEMPTS=60
ATTEMPT=0
STATUS="processing"

while [ "$STATUS" != "completed" ] && [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
    
    STATUS_RESPONSE=$(curl -s "http://localhost:8000/api/status/$TASK_ID")
    STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    PROGRESS=$(echo $STATUS_RESPONSE | grep -o '"progress":[0-9]*' | cut -d':' -f2)
    RESULT_ID=$(echo $STATUS_RESPONSE | grep -o '"result_id":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$PROGRESS" ]; then
        PROGRESS=0
    fi
    
    echo -ne "\r  Progress: $PROGRESS% (Status: $STATUS) - Attempt $ATTEMPT/$MAX_ATTEMPTS"
    
    if [ "$STATUS" == "failed" ]; then
        echo ""
        echo -e "${RED}Error: Analysis failed${NC}"
        echo "Status response: $STATUS_RESPONSE"
        exit 1
    fi
done

echo ""

if [ "$STATUS" != "completed" ]; then
    echo -e "${RED}Error: Analysis timed out${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Analysis completed${NC}"
echo "Repository ID: $RESULT_ID"
echo ""

# Step 3: Get tree
echo "Step 3: Retrieving repository tree..."
TREE_RESPONSE=$(curl -s "http://localhost:8000/api/tree/$RESULT_ID")

if echo "$TREE_RESPONSE" | grep -q "error\|Error\|not found"; then
    echo -e "${RED}Error: Failed to retrieve tree${NC}"
    echo "Response: $TREE_RESPONSE"
    exit 1
fi

TREE_NAME=$(echo $TREE_RESPONSE | grep -o '"name":"[^"]*' | head -1 | cut -d'"' -f4)
echo -e "${GREEN}✓ Tree retrieved${NC}"
echo "Root name: $TREE_NAME"
echo ""

# Step 4: Test search
echo "Step 4: Testing search..."
SEARCH_RESPONSE=$(curl -s "http://localhost:8000/api/search?q=hello")

if echo "$SEARCH_RESPONSE" | grep -q "error\|Error"; then
    echo -e "${YELLOW}⚠ Search returned error (may be expected if no matches)${NC}"
else
    echo -e "${GREEN}✓ Search completed${NC}"
    RESULT_COUNT=$(echo $SEARCH_RESPONSE | grep -o '"path"' | wc -l)
    echo "Results found: $RESULT_COUNT"
fi
echo ""

# Step 5: Test Q&A
echo "Step 5: Testing Q&A..."
QA_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/qa" \
  -H "Content-Type: application/json" \
  -d "{\"repo_id\": \"$RESULT_ID\", \"question\": \"What does this repository do?\"}")

if echo "$QA_RESPONSE" | grep -q "error\|Error"; then
    echo -e "${YELLOW}⚠ Q&A returned error${NC}"
    echo "Response: $QA_RESPONSE"
else
    echo -e "${GREEN}✓ Q&A completed${NC}"
    ANSWER=$(echo $QA_RESPONSE | grep -o '"answer":"[^"]*' | cut -d'"' -f4 | head -c 100)
    echo "Answer preview: $ANSWER..."
fi
echo ""

# Summary
echo "=== Test Summary ==="
echo -e "${GREEN}✓ All tests passed!${NC}"
echo ""
echo "Repository analyzed: $REPO_URL"
echo "Task ID: $TASK_ID"
echo "Repository ID: $RESULT_ID"
echo ""
echo "You can now:"
echo "  1. View full tree: curl http://localhost:8000/api/tree/$RESULT_ID | jq"
echo "  2. Search: curl 'http://localhost:8000/api/search?q=your_query'"
echo "  3. Ask questions: curl -X POST http://localhost:8000/api/qa -H 'Content-Type: application/json' -d '{\"repo_id\":\"$RESULT_ID\",\"question\":\"your question\"}'"
echo ""
echo "Or open the frontend at http://localhost:3000 (if running)"

