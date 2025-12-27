#!/bin/bash
# Test file selection logic for dual-file architecture

set -e

TESTS_PASSED=0
TESTS_FAILED=0

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing Dual-File Architecture: File Selection Logic"
echo "====================================================="
echo

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

# Test 1: source.json contains __ prefixed specs
echo "Test 1: Verify source.json contains framework specs (__ prefix)"
if jq -e '.specs | keys[] | select(startswith("__"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "source.json contains __ prefixed specs"
else
    fail "source.json does not contain __ prefixed specs"
fi

# Test 2: source.json does NOT contain non-__ prefixed specs
echo "Test 2: Verify source.json only has framework specs"
NON_FRAMEWORK=$(jq -r '.specs | keys[] | select(startswith("__") | not)' .jkspec/source.json 2>/dev/null | wc -l)
if [ "$NON_FRAMEWORK" -eq 0 ]; then
    pass "source.json contains only __ prefixed specs"
else
    fail "source.json contains $NON_FRAMEWORK non-framework specs"
fi

# Test 3: project.json exists or can be created
echo "Test 3: Verify project.json exists or template is valid"
if [ -f .jkspec-project/project.json ]; then
    pass "project.json exists"
elif [ -f .jkspec/templates/project.json ]; then
    pass "project.json template exists for auto-creation"
else
    fail "Neither project.json nor template exists"
fi

# Test 4: Both files validate against schema
echo "Test 4: Validate source.json against schema"
if ajv validate -s .jkspec/jkspec.schema.json -d .jkspec/source.json --spec=draft2020 --strict=false > /dev/null 2>&1; then
    pass "source.json validates against schema"
else
    fail "source.json fails schema validation"
fi

if [ -f .jkspec-project/project.json ]; then
    echo "Test 5: Validate project.json against schema"
    if ajv validate -s .jkspec/jkspec.schema.json -d .jkspec-project/project.json --spec=draft2020 --strict=false > /dev/null 2>&1; then
        pass "project.json validates against schema"
    else
        fail "project.json fails schema validation"
    fi
fi

# Test 6: Worker guidelines reference dual-file architecture
echo "Test 6: Verify worker guidelines include dual-file rules"
if jq -e '.specs.__jkspec.components.worker.guidelines[] | select(contains("dual-file") or contains("Dual-file"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "Worker guidelines include dual-file architecture rules"
else
    fail "Worker guidelines missing dual-file architecture rules"
fi

# Summary
echo
echo "====================================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "====================================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
