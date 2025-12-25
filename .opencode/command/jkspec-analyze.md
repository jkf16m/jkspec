# jkspec-analyze

Analyze the current jkspec structure and provide recommendations.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jkspec-cli"].location' .jkspec/source.json)
   ```

2. Get all spec IDs:
   ```bash
   $JSPEC_CLI list
   ```

3. Count total specs by type by reading each:
   ```bash
   $JSPEC_CLI get <spec-id>
   ```

4. Identify specs with draft status

5. Check for missing descriptions or empty fields

6. Analyze tag usage and suggest consolidation if needed

7. Check if project metadata is complete

8. Provide actionable recommendations

## Analysis Areas

- **Coverage**: Spec count by type (api, model, component, service, etc.)
- **Completeness**: Missing or incomplete fields
- **Status**: Distribution of draft/active/deprecated specs
- **Tags**: Tag usage patterns and suggestions
- **Project Health**: Overall project metadata quality
