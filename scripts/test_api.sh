#!/bin/bash
# Comprehensive API Testing Script

BASE_URL="http://localhost:8000"
EMAIL="testuser_$(date +%s)@example.com"
PASSWORD="SecurePassword123!"

echo "======================================"
echo "TALORA API COMPREHENSIVE TEST SUITE"
echo "======================================"
echo ""

# Test 1: Health Check
echo "TEST 1: Health Check"
curl -s "$BASE_URL/health" | python -m json.tool
echo -e "\n"

# Test 2: User Registration
echo "TEST 2: User Registration"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
echo "$REGISTER_RESPONSE" | python -m json.tool
TOKEN=$(echo "$REGISTER_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
echo "Token: $TOKEN"
echo -e "\n"

# Test 3: User Login
echo "TEST 3: User Login"
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | python -m json.tool
echo -e "\n"

# Test 4: Job Search
echo "TEST 4: Job Search (keywords=python, limit=5)"
curl -s "$BASE_URL/api/jobs/search?keywords=python&limit=5" | python -m json.tool | head -50
echo -e "\n"

echo "======================================"
echo "TESTS COMPLETE"
echo "======================================"
