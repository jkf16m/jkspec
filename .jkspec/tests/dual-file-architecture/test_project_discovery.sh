#!/bin/bash
# Test project.json auto-discovery and creation logic

set -e

TESTS_PASSED=0
TESTS_FAILED=0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Testing Dual-File Architecture: Project Discovery"
echo "================================================="
echo

pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

# Test 1: project.json exists in expected location
echo "Test 1: Check if project.json exists"
if [ -f .jkspec-project/project.json ]; then
    pass "project.json exists at .jkspec-project/project.json"
else
    echo "⚠ project.json does not exist (will be auto-created on first use)"
fi

# Test 2: project.json has required top-level keys
if [ -f .jkspec-project/project.json ]; then
    echo "Test 2: Verify project.json structure"
    
    if jq -e '.project' .jkspec-project/project.json > /dev/null 2>&1; then
        pass "project.json has 'project' key"
    else
        fail "project.json missing 'project' key"
    fi
    
    if jq -e '.specs' .jkspec-project/project.json > /dev/null 2>&1; then
        pass "project.json has 'specs' key"
    else
        fail "project.json missing 'specs' key"
    fi
fi

# Test 3: CLI scripts can detect project.json
echo "Test 3: Check if CLI scripts reference project.json"
if grep -r "project.json" .jkspec/cli/*.py > /dev/null 2>&1; then
    pass "CLI scripts reference project.json"
else
    fail "CLI scripts do not reference project.json"
fi

# Test 4: Worker guidelines mention project.json auto-creation
echo "Test 4: Verify worker knows about auto-creation"
if jq -e '.specs.__jkspec.components.worker.guidelines[] | select(contains("project.json") and contains("auto-create"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "Worker guidelines include project.json auto-creation"
else
    fail "Worker guidelines missing project.json auto-creation rule"
fi

# Summary
echo
echo "================================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "================================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
