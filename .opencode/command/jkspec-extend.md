# jkspec-extend

Add a new spec to the jkspec file.

## Steps

1. Fetch CLI location using bootstrap pattern:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jkspec-cli"].location' .jkspec/source.json)
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

5. Validate the modified file against schema:
   ```bash
   ajv validate -s .jkspec/jkspec.schema.json -d <target-file> --spec=draft2020 --strict=false
   ```
   Where `<target-file>` is either `.jkspec/source.json` or `.jkspec-project/project.json` depending on spec prefix.

6. Confirm success and show the added spec:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```
