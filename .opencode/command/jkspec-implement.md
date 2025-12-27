IMPLEMENT ALL PENDING DRAFTS:

**File Selection Logic:**
- Specs with `__` prefix → `.jkspec/source.json` (framework internals)
- Specs without `__` prefix → `.jkspec-project/project.json` (user project specs)
- Default: All new user specs go to `project.json` unless explicitly prefixed with `__`

jq '.specs.__jkspec.components.worker.commands_definitions.implement' .jkspec/source.json