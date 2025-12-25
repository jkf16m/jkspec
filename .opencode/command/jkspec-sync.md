# jkspec-sync

Ensure jkspec is in sync with actual codebase structure.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jkspec-cli"].location' .jkspec/source.json)
   ```

2. Get all spec IDs:
   ```bash
   $JSPEC_CLI list
   ```

3. For each spec, read details:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

4. Verify referenced code/files still exist

5. Check for deprecated or removed code references

6. Look for new code that should have specs

7. Report discrepancies and offer updates

## Sync Checks

- **File Existence**: Verify location fields point to existing files
- **Deprecated Code**: Check if referenced code has been removed
- **New Code**: Find new code without specs
- **Status Accuracy**: Ensure active/deprecated status matches reality
