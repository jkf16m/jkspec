# Dual-File Architecture Tests

This directory contains tests to verify the dual-file architecture behavior of jkspec agents.

## Test Files

### `test_file_selection.sh`
Tests the core file selection logic:
- Verifies source.json contains only `__` prefixed specs
- Verifies project.json is created/accessible
- Validates both files against schema
- Checks worker guidelines include dual-file rules

### `test_project_discovery.sh`
Tests project.json discovery and initialization:
- Checks if project.json exists at expected location
- Verifies project.json has required structure (project, specs keys)
- Ensures CLI scripts reference project.json
- Validates worker knows about auto-creation

### `test_agent_behavior.sh`
Tests agent behavior with dual-file setup:
- Verifies agent defaults to project.json for queries
- Checks new spec creation targets correct file
- Ensures __jkspec components are hidden by default
- Validates dual-file validation is mandatory
- Checks command files document file selection

## Running Tests

Run all tests:
```bash
cd .jkspec/tests/dual-file-architecture
./test_file_selection.sh
./test_project_discovery.sh
./test_agent_behavior.sh
```

Or run the master test suite:
```bash
cd .jkspec/tests
./run_all_tests.sh
```

## Test Requirements

- `jq` installed and available in PATH
- `ajv-cli` installed for schema validation
- Bash shell (Linux/macOS/WSL)

## Expected Results

All tests should pass when:
1. Dual-file architecture is properly implemented
2. Worker guidelines correctly reference both files
3. Command documentation includes file selection logic
4. Schema validation works for both files

## Test Philosophy

These tests verify **specification compliance** rather than implementation details. They check:
- Configuration correctness (guidelines, rules in source.json)
- File structure adherence (naming, location, schema)
- Documentation completeness (command files, README)

They do NOT test:
- Runtime agent behavior (would require AI agent execution)
- Complex jq query correctness (covered by integration tests)
- Error handling edge cases (covered by unit tests if needed)
