#!/bin/bash
# Complete End-to-End API Testing Script

BASE_URL="http://localhost:8000"
EMAIL="e2e_test_$(date +%s)@example.com"
PASSWORD="SecureTestPass123!"

echo "=========================================="
echo "END-TO-END API TESTING - COMPLETE SUITE"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "TEST 1: Health Check"
HEALTH=$(curl -s "$BASE_URL/health")
echo "$HEALTH" | python -m json.tool
echo ""

# Test 2: User Registration
echo "TEST 2: User Registration"
REG_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
echo "$REG_RESPONSE" | python -m json.tool
TOKEN=$(echo "$REG_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
echo "Token obtained: ${TOKEN:0:30}..."
echo ""

# Test 3: User Login
echo "TEST 3: User Login"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
echo "$LOGIN_RESPONSE" | python -m json.tool
echo ""

# Test 4: Resume Upload
echo "TEST 4: Resume Upload"
RESUME_PATH="/home/ravi/Documents/projects/TaloraV2/data/resumes/ravi_resume_9608676321.pdf"
if [ -f "$RESUME_PATH" ]; then
    UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/resume/upload" \
      -F "file=@$RESUME_PATH")
    echo "$UPLOAD_RESPONSE" | python -m json.tool
    JOB_ID=$(echo "$UPLOAD_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null)
    echo "Job ID: $JOB_ID"
else
    echo "Resume file not found"
fi
echo ""

# Test 5: Resume Parsing Status
if [ ! -z "$JOB_ID" ]; then
    echo "TEST 5: Resume Parsing Status (polling 3 times)"
    for i in 1 2 3; do
        echo "  Poll $i/3..."
        STATUS=$(curl -s "$BASE_URL/api/resume/status/$JOB_ID")
        echo "$STATUS" | python -m json.tool | head -20
        sleep 5
    done
else
    echo "TEST 5: SKIPPED (No job ID)"
fi
echo ""

# Test 6: Job Search
echo "TEST 6: Job Search (keywords='data scientist')"
JOB_SEARCH=$(curl -s "$BASE_URL/api/jobs/search?keywords=data+scientist&limit=5")
echo "$JOB_SEARCH" | python -m json.tool
FIRST_JOB_ID=$(echo "$JOB_SEARCH" | python -c "import sys, json; jobs=json.load(sys.stdin).get('jobs', []); print(jobs[0]['job_id'] if jobs else '')" 2>/dev/null)
echo ""

# Test 7: Get Job by ID
if [ ! -z "$FIRST_JOB_ID" ]; then
    echo "TEST 7: Get Job Details (ID: $FIRST_JOB_ID)"
    JOB_DETAIL=$(curl -s "$BASE_URL/api/jobs/$FIRST_JOB_ID")
    echo "$JOB_DETAIL" | python -m json.tool | head -30
else
    echo "TEST 7: SKIPPED (No job ID)"
fi
echo ""

# Test 8: List Resumes
echo "TEST 8: List User Resumes"
RESUME_LIST=$(curl -s "$BASE_URL/api/resume/list" \
  -H "Authorization: Bearer $TOKEN")
echo "$RESUME_LIST" | python -m json.tool | head -30
RESUME_ID=$(echo "$RESUME_LIST" | python -c "import sys, json; resumes=json.load(sys.stdin).get('resumes', []); print(resumes[0]['resume_id'] if resumes else '')" 2>/dev/null)
echo ""

# Test 9: Resume Matching
if [ ! -z "$RESUME_ID" ]; then
    echo "TEST 9: Resume-to-Job Matching (Resume ID: $RESUME_ID)"
    MATCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/match" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{\"resume_id\":\"$RESUME_ID\",\"job_filters\":{},\"top_n\":5}")
    echo "$MATCH_RESPONSE" | python -m json.tool | head -50
else
    echo "TEST 9: SKIPPED (No resume ID)"
fi
echo ""

echo "=========================================="
echo "END-TO-END TESTING COMPLETE"
echo "=========================================="
