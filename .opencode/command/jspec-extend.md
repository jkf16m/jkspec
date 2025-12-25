# jspec-extend

Add a new spec to the jspec file.

## Steps

1. Fetch CLI location using bootstrap pattern:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jspec-cli"].location' .jspec/source.json)
   ```

2. Validate the spec-id follows kebab-case convention

3. Check if spec already exists:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

4. Use CLI to add the spec:
   ```bash
   $JSPEC_CLI add-spec <spec-id> <type> <description> [tags...]
   ```

5. Confirm success and show the added spec:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```
