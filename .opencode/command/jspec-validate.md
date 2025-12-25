# jspec-validate

Validate the jspec structure and check for inconsistencies.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jspec-cli"].location' .jspec/source.json)
   ```

2. Get all spec IDs:
   ```bash
   $JSPEC_CLI list
   ```

3. Check required project fields exist (use jq for project metadata):
   ```bash
   jq '.project' .jspec/source.json
   ```

4. For each spec, validate required fields:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

5. Check for kebab-case naming in spec IDs

6. Verify no duplicate spec IDs

7. Report any issues found or confirm validity

## Validation Checks

- All spec IDs follow kebab-case convention
- No duplicate spec IDs
- Required fields present (type, description)
- Project metadata is complete
- References to files/locations exist
