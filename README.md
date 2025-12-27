# jkspec

**JSON-based specification format for rapid AI agent context retrieval**

## What is jkspec?

jkspec is a spec-driven workflow that gives AI agents an instant, queryable map of your project. The framework ships with a canonical `.jkspec/source.json` file describing the jkspec system itself, while every project that adopts jkspec keeps its own specs in `.jkspec-project/project.json`. Agents (and humans) interact with both files directly via `jq`, so there is no custom CLI layer to learn or maintain.

Think of jkspec as a structured, machine-friendly contract: it captures architecture, conventions, relationships, implementation state, and historical decisions in one place, drastically reducing the "let me explore your repo" phase.

## Vision

The vision behind jkspec stems from watching AI assistants burn time and tokens rediscovering the same project facts. Instead of re-reading directory trees each session, agents should be able to ask:

- What components already exist?
- Which specs are still drafts?
- Where are the implementations located?
- What dependencies or decisions matter here?

All of those answers are available in milliseconds with a `jq` query. Long term, the goal is **spec-driven development with AI agents**—specs act as active contracts that guide implementation, verification, and coordination across agents.

## Prototype Notice

⚠️ **This is a prototype.** Conventions are evolving, the tooling surface is intentionally minimal, and there are still rough edges. I use jkspec every day with my own agents and find the approach promising, but I expect the format and workflows to keep shifting as new lessons emerge. Feedback and constructive criticism are very welcome.

## Advantages

**✨ Instant Context**  
Agents get project-wide awareness with a single `jq` query—no exploratory crawling required.

**📋 Single Source of Truth**  
Architecture, conventions, specs, and status all live in tightly versioned JSON.

**🔍 Queryable Structure**  
Filter by type, status, tags, or any custom field using familiar `jq` expressions.

**📊 Implementation Tracking**  
Specs capture draft/active/deprecated states and can include task arrays for traceability.

**🌳 Hierarchical Specs**  
Model entire subsystems by nesting specs (children, components, endpoints, tests, etc.).

**📝 Version-Control Friendly**  
JSON diffs make spec evolution obvious during review.

**🛡 Schema-Backed Safety**  
Both `.jkspec/source.json` and `.jkspec-project/project.json` must validate against `jkspec.schema.json` via `ajv`, catching structural issues immediately.

**🤖 Agent-Optimized**  
Designed from the ground up for AI consumers rather than human-only documentation.

## Disadvantages

**⚠️ Manual Sync Required**  
Specs only stay accurate if you update them alongside code changes.

**📚 Learning Curve**  
You need basic `jq`, JSON schema, and dual-file habits to work effectively.

**📄 JSON Verbosity**  
Large projects can make the spec files lengthy and harder to scan manually.

**👥 Not Human-Optimized**  
Raw JSON is less comfortable to read than prose docs (agents don’t mind, people might).

**🚧 Prototype Limitations**  
Conventions, templates, and automation hooks are still settling.

**🔀 Merge Pressure**  
Centralized specs can create conflicts if many teammates touch the files simultaneously.

**🧪 Validation Workflow Overhead**  
Running `ajv` on both spec files after every change adds a required (but important) extra step.

## Quick Start

1. **Clone the framework template** into your project without git history:
   ```bash
   npx degit jkf16m/jkspec .jkspec
   ```

2. **Create (or let your agent create) `.jkspec-project/project.json`.** All user/project specs belong here, separate from the framework file. A minimal template looks like:
   ```json
   {
     "project": {
       "name": "your-project-name",
       "description": "Your project description",
       "version": "0.1.0",
       "architecture": {
         "style": "Define your architecture style",
         "pattern": "Define your patterns"
       },
       "conventions": {
         "spec_location": ".jkspec-project/project.json"
       },
       "decisions": []
     },
     "specs": {}
   }
   ```
   Agents should auto-create this file if it’s missing, but you can bootstrap it yourself as well.

3. **Add or update specs** with direct `jq` commands. Use kebab-case identifiers (`feature-x`, `auth-service`, etc.). Specs prefixed with `__` are reserved for the framework and stay in `.jkspec/source.json`.

4. **Validate both files** after every change:
   ```bash
   ajv validate -s .jkspec/jkspec.schema.json -d .jkspec/source.json --spec=draft2020 --strict=false
   ajv validate -s .jkspec/jkspec.schema.json -d .jkspec-project/project.json --spec=draft2020 --strict=false
   ```

5. **Query with `jq`** to drive agents (and your own automation):
   ```bash
   jq '.specs' .jkspec/source.json
   jq '.specs' .jkspec-project/project.json
   ```

## Dual-File Architecture

jkspec separates **framework specifications** from **project specifications** using two distinct JSON files:

### `.jkspec/source.json` – Framework Specs
- Contains all jkspec framework definitions, worker behavior, and internal components
- All specs here use `__` prefix (e.g., `__jkspec`, `__jkspec.components.worker`)
- **Read-only for users** – only modify if extending the framework itself
- Shared across all projects using jkspec

### `.jkspec-project/project.json` – Your Project Specs
- Contains all user/project-specific specifications
- **Auto-created** by agents on first spec operation if it doesn't exist
- All user specs go here by default (no `__` prefix)
- Unique to your project, version-controlled with your code

### File Selection Logic
The agent determines which file to use based on spec naming:
- **Specs with `__` prefix** → `.jkspec/source.json` (framework)
- **Specs without `__` prefix** → `.jkspec-project/project.json` (project)

This separation ensures:
- ✅ Framework updates don't touch project specs
- ✅ Project specs stay isolated from framework internals
- ✅ Clear namespace boundaries (`__` = internal, no prefix = user)
- ✅ Both files validate against the same `jkspec.schema.json`

### Auto-Creation of project.json
When you (or an agent) create your first project spec, the agent will automatically initialize `.jkspec-project/project.json` with this minimal template:

```json
{
  "project": {
    "name": "your-project-name",
    "description": "Your project description",
    "version": "0.1.0",
    "architecture": {
      "style": "Define your architecture style",
      "pattern": "Define your patterns"
    },
    "conventions": {
      "spec_location": ".jkspec-project/project.json"
    },
    "decisions": []
  },
  "specs": {}
}
```

You can also create this file manually before your first spec operation.

## Core Concepts

- **Project metadata** – Each spec file starts with a `project` object describing the system that file covers (framework vs. your app).
- **Specs + `__meta`** – Every spec includes `__meta.type`, `description`, `status`, and `tags`, plus any custom fields such as `location`, `purpose`, or `dependencies`.
- **Status lifecycle** – `draft → active → deprecated` keeps implementation state explicit.
- **Hierarchical structure** – Specs can nest arbitrary components using keys such as `children`, `components`, `tests`, or `endpoints`.
- **Internal specs** – Identifiers prefixed with `__` belong to the jkspec framework itself; leave them alone unless you are modifying the framework.
- **Traceability tasks** – Specs can include `tasks` arrays (`[{ name, description, done }]`) to capture step-by-step implementation progress.
- **Direct `jq` operations** – `jq` is the interface for reading and writing specs; there is no separate CLI abstraction.

## Examples

List every spec in the framework file:
```bash
jq '.specs | keys' .jkspec/source.json
```

List user/project specs (auto-creates the file if needed before running this):
```bash
jq '.specs | keys' .jkspec-project/project.json
```

Inspect a specific spec’s metadata:
```bash
jq '.specs["spec-id"].__meta' .jkspec-project/project.json
```

Find every draft spec no matter where it lives:
```bash
jq '.specs | to_entries[] | select(.value.__meta.status == "draft")' .jkspec/source.json
jq '.specs | to_entries[] | select(.value.__meta.status == "draft")' .jkspec-project/project.json
```

Add a tag to a spec:
```bash
jq '.specs["spec-id"].__meta.tags += ["new-tag"]' .jkspec-project/project.json > tmp.json && mv tmp.json .jkspec-project/project.json
```

Validate both files:
```bash
ajv validate -s .jkspec/jkspec.schema.json -d .jkspec/source.json --spec=draft2020 --strict=false
ajv validate -s .jkspec/jkspec.schema.json -d .jkspec-project/project.json --spec=draft2020 --strict=false
```

## Use Cases

- Working with AI coding assistants that need precise context quickly
- Building spec-driven or agent-first development workflows
- Capturing architecture decisions, dependencies, and implementation state in one place
- Auditing which features are draft vs. active (and what tasks remain)
- Syncing live code against a schema-validated source of truth

## Support

If you find jkspec useful or interesting, consider buying me a coffee! This experiment is self-funded and ongoing, and every bit of support helps.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/jdfm24)
