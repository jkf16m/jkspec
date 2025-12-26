# jkspec-update

Update an existing spec field.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jkspec-cli"].location' .jkspec/source.json)
   ```

2. Verify the spec exists:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

3. Use CLI to update the field:
   ```bash
   $JSPEC_CLI update-spec <spec-id> <field> <value>
   ```

4. Validate the modified file against schema:
   ```bash
   ajv validate -s .jkspec/jkspec.schema.json -d <target-file> --spec=draft2020 --strict=false
   ```
   Where `<target-file>` is either `.jkspec/source.json` or `.jkspec-project/project.json` depending on spec prefix.

5. Show the updated spec:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```
