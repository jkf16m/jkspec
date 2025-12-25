# jspec-test-sync

Verify that all specs are actually implemented in the codebase.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jspec-cli"].location' .jspec/source.json)
   ```

2. Get all spec IDs:
   ```bash
   $JSPEC_CLI list
   ```

3. For each spec, check implementation status:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

4. Verify location field points to existing files

5. Check status field (draft/active/deprecated)

6. Generate comprehensive implementation report

7. Suggest actions for missing implementations

## Report Format

For each spec:
- **Spec ID**: The identifier
- **Status**: draft | active | deprecated
- **Location**: File path
- **Implemented**: ✓ Yes | ✗ No | ⚠ Partial
- **Action**: Suggested next step
