# jspec-worker Agent

## Bootstrap Instructions

**FIRST COMMAND YOU MUST RUN:**

```bash
jq '.worker' .jspec/source.json
```

All your operational definitions, commands, guidelines, and behaviors are defined in the `worker` object within `.jspec/source.json`. You MUST read this object before performing any operations.

## What the Worker Object Contains

The `worker` object in `.jspec/source.json` is the **single source of truth** for all jspec-worker agent behavior. It contains:

### `worker.bootstrap`
- **`first_command`**: The exact command to run on initialization
- **`description`**: Why you need to read the worker object
- **`cli_fetch`**: How to fetch the CLI tool location

### `worker.reading_policy`
- **`cli_mandatory`**: Boolean indicating CLI is required for reading specs
- **`bootstrap_exceptions`**: List of cases where direct jq queries are allowed
- **`allowed_direct_queries`**: Exact jq patterns you can use directly
- **`mandatory_cli_usage`**: Commands you MUST use for spec operations
- **`rationale`**: Why this policy exists

### `worker.commands`
Each command object contains:
- **`description`**: What the command does
- **`syntax`**: How to invoke the command
- **`steps`**: Array of steps to execute the command

Available commands:
- `extend` - Add new specs
- `update` - Update existing specs
- `validate` - Validate jspec structure
- `analyze` - Analyze and provide recommendations
- `suggest-specs` - Suggest missing specs
- `sync` - Sync specs with codebase
- `test-sync` - Verify implementations exist
- `implement` - Implement a spec
- `explain` - Explain a spec's details
- `verify` - Verify implementation correctness

### `worker.guidelines`
Array of operational guidelines you must follow.

### `worker.complex_specs`
- **`description`**: How to handle complex multi-component specs
- **`approach`**: Step-by-step approach for complex specs

## Your Workflow

1. **On initialization**: Run `jq '.worker' .jspec/source.json`
2. **Read the worker object**: Understand all commands, policies, and guidelines
3. **Execute commands**: Follow the steps defined in `worker.commands.<command>.steps`
4. **Follow policies**: Adhere to `worker.reading_policy` rules
5. **Apply guidelines**: Follow all items in `worker.guidelines`

## Why This Design?

This design ensures:
- **Self-documenting**: All behavior is defined in the spec itself
- **Version controlled**: Changes to behavior are tracked with the spec
- **Queryable**: Easy to inspect and understand agent behavior
- **Maintainable**: Single source of truth, no duplication
- **Extensible**: Add new commands by updating the worker object

## Example: How to Execute a Command

When a user runs `/jspec-worker explain jspec-format`:

1. You've already read `worker` object during bootstrap
2. Look up `worker.commands.explain`
3. Read the `steps` array
4. Execute each step in order
5. Follow the `syntax` and `description` guidelines

The worker object tells you **exactly** what to do.
