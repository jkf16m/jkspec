# jspec-verify

Verify if a spec is implemented correctly.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jspec-cli"].location' .jspec/source.json)
   ```

2. Read spec requirements:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

3. Check if implementation exists at specified location

4. Verify implementation matches requirements:
   - Correct type/structure
   - All required functionality present
   - Dependencies properly handled
   - Tests exist (if specified)

5. Report compliance or discrepancies

## Verification Checks

- **File Exists**: Implementation file is present
- **Structure**: Matches spec type requirements
- **Functionality**: Core features implemented
- **Dependencies**: Required dependencies satisfied
- **Tests**: Test coverage adequate
- **Documentation**: Inline docs present

## Report Format

- **Overall**: ✓ Pass | ✗ Fail | ⚠ Partial
- **Details**: Specific compliance/discrepancy notes
- **Recommendations**: Suggested improvements
