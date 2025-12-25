# jkspec-suggest-specs

Suggest missing specs based on codebase analysis.

## Steps

1. Fetch CLI location:
   ```bash
   JSPEC_CLI=$(jq -r '.specs["jkspec-cli"].location' .jkspec/source.json)
   ```

2. Get existing spec IDs:
   ```bash
   $JSPEC_CLI list
   ```

3. Analyze the codebase structure:
   - Search for API endpoints
   - Find model/schema definitions
   - Locate component files
   - Identify service modules

4. Look for undocumented APIs, models, components, services

5. Compare against existing specs

6. Suggest new specs with ready-to-run commands

## Suggestion Format

For each missing spec, provide:
- Spec ID (kebab-case)
- Type (api, model, component, service, etc.)
- Description
- Location (file path)
- Suggested command to add it
