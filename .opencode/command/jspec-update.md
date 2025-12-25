# jspec-update

Update an existing spec field.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jspec-cli"].location' .jspec/source.json)
   ```

2. Verify the spec exists:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

3. Use CLI to update the field:
   ```bash
   $JSPEC_CLI update-spec <spec-id> <field> <value>
   ```

4. Show the updated spec:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```
