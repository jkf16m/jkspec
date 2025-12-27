#!/bin/bash
# Test agent behavior with dual-file architecture

set -e

TESTS_PASSED=0
TESTS_FAILED=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Testing Dual-File Architecture: Agent Behavior"
echo "=============================================="
echo

pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test 1: Agent queries should default to project.json
echo "Test 1: Verify default query target is project.json"
if jq -e '.specs.__jkspec.components.worker.guidelines[] | select(contains("Default spec queries MUST target") and contains("project.json"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "Agent defaults to project.json for queries"
else
    fail "Agent does not default to project.json"
fi

# Test 2: New specs should go to project.json unless __ prefixed
echo "Test 2: Verify new spec creation targets project.json"
if jq -e '.specs.__jkspec.components.worker.guidelines[] | select(contains("New spec creation") and contains("project.json"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "New specs default to project.json"
else
    fail "New spec creation rule not found"
fi

# Test 3: Agent should not expose __jkspec components unless prompted
echo "Test 3: Verify agent hides internal components by default"
if jq -e '.specs.__jkspec.components.worker.guidelines[] | select(contains("Do not mention meta-specs or __jkspec"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "Agent hides __jkspec components unless requested"
else
    fail "Agent visibility rule not found"
fi

# Test 4: Both files must validate after modifications
echo "Test 4: Verify validation is mandatory after modifications"
if jq -e '.specs.__jkspec.components.worker.guidelines[] | select(contains("IMMEDIATELY validate") and contains("source.json") and contains("project.json"))' .jkspec/source.json > /dev/null 2>&1; then
    pass "Agent must validate both files after modifications"
else
    fail "Dual-file validation rule not found"
fi

# Test 5: Command files document file selection
echo "Test 5: Verify command files include file selection docs"
COMMAND_FILES=(.opencode/command/*.md)
DOCS_FOUND=0
for file in "${COMMAND_FILES[@]}"; do
    if grep -q "File Selection Logic" "$file" 2>/dev/null; then
        ((DOCS_FOUND++))
    fi
done

if [ $DOCS_FOUND -ge 3 ]; then
    pass "Command files document file selection ($DOCS_FOUND files)"
else
    fail "Only $DOCS_FOUND command files have file selection docs"
fi

# Test 6: CLI scripts handle both files
echo "Test 6: Check CLI scripts for dual-file awareness"
if ls .jkspec/cli/*.py > /dev/null 2>&1; then
    warn "CLI scripts exist - manual verification needed for dual-file support"
else
    warn "No Python CLI scripts found"
fi

# Summary
echo
echo "=============================================="
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "=============================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
