# jspec-explain

Read and explain a specific spec's details.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jspec-cli"].location' .jspec/source.json)
   ```

2. Read the spec:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

3. Extract and explain all relevant details:
   - **ID**: The spec identifier
   - **Type**: Category (api, model, component, etc.)
   - **Description**: What it does
   - **Location**: Where it's implemented
   - **Status**: Current state (draft/active/deprecated)
   - **Tags**: Associated labels
   - **Dependencies**: Other specs it relies on
   - **Children**: Sub-components or related specs

4. Provide comprehensive explanation

## Explanation Format

Present the information in a clear, structured format that's easy to understand.
