#!/bin/bash

# Schema Validation Test Suite
# Tests ajv validation against jkspec.schema.json

SCHEMA=".jkspec/jkspec.schema.json"
TEST_DIR=".jkspec/tests/schema-validation"

echo "================================"
echo "Schema Validation Test Suite"
echo "================================"
echo ""

# Test counter
PASSED=0
FAILED=0

# Test 1: Valid spec should pass
echo "Test 1: Valid spec should PASS validation"
if ajv validate -s "$SCHEMA" -d "$TEST_DIR/valid-spec.json" --spec=draft2020 --strict=false > /dev/null 2>&1; then
    echo "✓ PASS: valid-spec.json validated successfully"
    ((PASSED++))
else
    echo "✗ FAIL: valid-spec.json should have passed validation"
    ((FAILED++))
fi
echo ""

# Test 2: Invalid spec (missing meta) should fail
echo "Test 2: Invalid spec (missing __meta) should FAIL validation"
if ajv validate -s "$SCHEMA" -d "$TEST_DIR/invalid-spec-missing-meta.json" --spec=draft2020 --strict=false > /dev/null 2>&1; then
    echo "✗ FAIL: invalid-spec-missing-meta.json should have failed validation"
    ((FAILED++))
else
    echo "✓ PASS: invalid-spec-missing-meta.json correctly failed validation"
    ((PASSED++))
fi
echo ""

# Test 3: Invalid spec (bad status) should fail
echo "Test 3: Invalid spec (bad status) should FAIL validation"
if ajv validate -s "$SCHEMA" -d "$TEST_DIR/invalid-spec-bad-status.json" --spec=draft2020 --strict=false > /dev/null 2>&1; then
    echo "✗ FAIL: invalid-spec-bad-status.json should have failed validation"
    ((FAILED++))
else
    echo "✓ PASS: invalid-spec-bad-status.json correctly failed validation"
    ((PASSED++))
fi
echo ""

# Test 4: Source.json should validate
echo "Test 4: source.json should PASS validation"
if ajv validate -s "$SCHEMA" -d ".jkspec/source.json" --spec=draft2020 --strict=false > /dev/null 2>&1; then
    echo "✓ PASS: source.json validated successfully"
    ((PASSED++))
else
    echo "✗ FAIL: source.json should validate"
    ((FAILED++))
fi
echo ""

# Summary
echo "================================"
echo "Test Results"
echo "================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
