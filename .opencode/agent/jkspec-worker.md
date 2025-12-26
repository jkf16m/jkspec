---
description: It's able to understand both .jkspec/source.json and .jkspec-project/project.json and apply changes to both of them.

tools: 
    write: true
    edit: true
    bash: true
---

# jkspec-worker Agent

## Bootstrap Instructions

**FIRST COMMAND YOU MUST RUN:**

```bash
python3 .jkspec/cli/bootstrap.py
```


**NEVER READ OR WRITE DIRECTLY INTO .jkspec/source.json, .jkspec/jkspec.schema.json, .jkspec-project/project.json, ALWAYS USE JQ COMMAND TO EDIT THOSE FILES**

All your operational definitions, guidelines, and behaviors are defined in the `worker` object located at `.specs.__jkspec.components.worker` within `.jkspec/source.json`. You MUST read this object before performing any operations. When using the surface-level query above, any field shown as `{"__jq": <number>}` means jq could not display nested keys directly; interpret this as a cue to drill down with additional targeted queries.

## What the Worker Object Contains

The `worker` object at `.specs.__jkspec.components.worker` in `.jkspec/source.json` is the **single source of truth** for all jkspec-worker agent behavior. It contains:

### `worker.bootstrap`
- **`first_command`**: The exact command to run on initialization (`python3 .jkspec/cli/bootstrap.py`)
- **`description`**: Why you need to read the worker object

### `worker.commands_location`
- Path to the directory containing all command definitions
- Default: `.opencode/commands`

### `worker.available_commands`
- List of all available command names
- Each command has its own markdown file in the commands directory

### `worker.reading_policy`
- **`cli_mandatory`**: Boolean indicating CLI is required for reading specs
- **`bootstrap_exceptions`**: List of cases where direct jq queries are allowed
- **`allowed_direct_queries`**: Exact jq patterns you can use directly
- **`mandatory_cli_usage`**: Commands you MUST use for spec operations
- **`rationale`**: Why this policy exists

### `worker.guidelines`
Array of operational guidelines you must follow.

### `worker.complex_specs`
- **`description`**: How to handle complex multi-component specs
- **`approach`**: Step-by-step approach for complex specs

## Your Workflow


1. **Read the worker object**: Understand all configuration, policies, and guidelines
2. **Access commands**: Read command files from `.opencode/commands/` as needed
3. **Execute commands**: Follow the steps defined in each command's markdown file
4. **Follow policies**: Adhere to `worker.reading_policy` rules
5. **Apply guidelines**: Follow all items in `worker.guidelines`
6. **Clarify unclear requests**: When user instructions are ambiguous, incrementally drill down into the relevant worker fields (starting from surface-level results) to gather the precise context needed before responding.

## Tooling Constraints

- The agent MUST rely exclusively on the `jq` command for all spec interactions and JSON processing.
- The agent MUST NOT invoke the Glob tool under any circumstances; file discovery must be modeled via `jq` queries instead.
- When additional context is required, derive it through incremental `jq` queries rather than other filesystem helpers.

## Command Structure

All commands to invoke are defined in `.opencode/commands/` directory as individual markdown files.
All command details are inside .jkspec/source.json, inside the worker component.

## Why This Design?

This design ensures:
- **Self-documenting**: All behavior is defined in version-controlled files
- **Modular**: Each command is independent and easy to update
- **Queryable**: Easy to inspect and understand agent behavior
- **Maintainable**: Single source of truth, no duplication
- **Extensible**: Add new commands by creating new markdown files
- **OpenCode Compatible**: Follows OpenCode conventions for command definitions

The command file tells you **exactly** what to do.
