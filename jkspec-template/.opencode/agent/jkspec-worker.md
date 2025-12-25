# jkspec-worker Agent

## Bootstrap Instructions

**FIRST COMMAND YOU MUST RUN:**

```bash
jq '.worker' .jkspec/source.json
```

All your operational definitions, guidelines, and behaviors are defined in the `worker` object within `.jkspec/source.json`. You MUST read this object before performing any operations.

## What the Worker Object Contains

The `worker` object in `.jkspec/source.json` is the **single source of truth** for all jkspec-worker agent behavior. It contains:

### `worker.bootstrap`
- **`first_command`**: The exact command to run on initialization
- **`description`**: Why you need to read the worker object
- **`cli_fetch`**: How to fetch the CLI tool location

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

1. **On initialization**: Run `jq '.worker' .jkspec/source.json`
2. **Read the worker object**: Understand all configuration, policies, and guidelines
3. **Access commands**: Read command files from `.opencode/commands/` as needed
4. **Execute commands**: Follow the steps defined in each command's markdown file
5. **Follow policies**: Adhere to `worker.reading_policy` rules
6. **Apply guidelines**: Follow all items in `worker.guidelines`

## Command Structure

All commands are defined in `.opencode/commands/` directory as individual markdown files:

- `jkspec-extend.md` - Add new specs
- `jkspec-update.md` - Update existing specs
- `jkspec-validate.md` - Validate jkspec structure
- `jkspec-analyze.md` - Analyze and provide recommendations
- `jkspec-suggest-specs.md` - Suggest missing specs
- `jkspec-sync.md` - Sync specs with codebase
- `jkspec-test-sync.md` - Verify implementations exist
- `jkspec-implement.md` - Implement a spec
- `jkspec-explain.md` - Explain a spec's details
- `jkspec-verify.md` - Verify implementation correctness

Each command file contains:
- Description of what the command does
- Step-by-step execution instructions
- Additional context (checks, formats, strategies, etc.)

## Why This Design?

This design ensures:
- **Self-documenting**: All behavior is defined in version-controlled files
- **Modular**: Each command is independent and easy to update
- **Queryable**: Easy to inspect and understand agent behavior
- **Maintainable**: Single source of truth, no duplication
- **Extensible**: Add new commands by creating new markdown files
- **OpenCode Compatible**: Follows OpenCode conventions for command definitions

## Example: How to Execute a Command

When a user runs `/jkspec-worker explain jkspec-format`:

1. You've already read `worker` object during bootstrap
2. Look up command location: `.opencode/commands/jkspec-explain.md`
3. Read the command file
4. Execute each step in order
5. Follow the additional context and guidelines

The command file tells you **exactly** what to do.
