# jkspec-implement

Implement a spec according to its requirements.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jkspec-cli"].location' .jkspec/source.json)
   ```

2. Read the spec:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

3. Understand requirements:
   - Type (api, model, component, service, etc.)
   - Description and purpose
   - Location (where to implement)
   - Dependencies (other specs it relies on)

4. Check for child specs or sub-components

5. Break down complex specs into implementation tasks

6. Implement code/files according to spec

7. Update spec status if needed:
   ```bash
   $JSPEC_CLI update-spec <spec-id> status active
   ```

8. Validate the modified file against schema:
   ```bash
   ajv validate -s .jkspec/jkspec.schema.json -d <target-file> --spec=draft2020 --strict=false
   ```
   Where `<target-file>` is either `.jkspec/source.json` or `.jkspec-project/project.json` depending on spec prefix.

9. Report what was implemented

## Implementation Strategy

- **Simple Specs**: Implement directly as single unit
- **Complex Specs**: Break into sub-tasks, implement systematically
- **Dependencies**: Implement dependencies first
- **Testing**: Add tests if specified in spec
