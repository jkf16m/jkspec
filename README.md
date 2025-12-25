# jkspec

**JSON-based specification format for rapid AI agent context retrieval**

## What is jkspec?

jkspec is a single-file, JSON-based specification format designed to eliminate the context-gathering overhead AI agents face when working with codebases. Instead of agents spending time exploring directories, reading multiple files, and piecing together project structure, jkspec provides a centralized `.jkspec/source.json` file that agents can query instantly using `jq`.

Think of it as a "map" for AI agents - a structured, queryable source of truth about your project's architecture, components, conventions, and implementation status.

## Vision

The vision of jkspec emerged from observing a consistent pattern: AI agents waste significant time and tokens exploring codebases before they can start actual work. Every conversation begins with "let me look at your project structure" followed by multiple file reads and questions.

jkspec flips this paradigm. What if agents could instantly access:
- Project architecture and conventions
- What exists and what doesn't
- Implementation status of features
- Dependencies and relationships
- Historical decisions and rationale

All queryable in milliseconds with simple `jq` commands.

The broader vision is **spec-driven development with AI agents** - where specifications aren't just documentation, but active, queryable contracts that guide agent behavior and reduce ambiguity.

## Prototype Notice

⚠️ **This is a prototype.** jkspec is an experiment in improving AI agent workflows. It's rough around the edges, the conventions are still evolving, and there are likely better ways to solve some of these problems.

That said, I've found it genuinely useful in my own agent-assisted development, and I believe the core idea has potential. If you're interested in exploring new ways to work with AI coding assistants, give it a try. Feedback, ideas, and constructive criticism are welcome.

## Advantages

**✨ Instant Context**  
Agents get full project context in a single jq query - no exploration needed

**📋 Single Source of Truth**  
One file contains architecture, conventions, specs, and status - no scattered documentation

**🔍 Queryable Structure**  
Use jq to filter by type, status, tags - agents can find exactly what they need

**📊 Implementation Tracking**  
Track what's draft vs active vs deprecated - clear visibility into project state

**🌳 Hierarchical Specs**  
Nest specs arbitrarily deep to match your architecture - from high-level features down to specific validations

**📝 Version Control Friendly**  
JSON file diffs clearly show spec changes - easy to review and track evolution

**🚀 No External Dependencies**  
Just JSON and jq - no special tools or frameworks required

**🤖 Agent-Optimized**  
Designed specifically for AI agent consumption, not just human documentation

## Disadvantages

**⚠️ Manual Sync Required**  
Specs don't automatically update when code changes - requires discipline to keep in sync

**📚 Learning Curve**  
Requires learning jq syntax and understanding the jkspec structure conventions

**📄 JSON Verbosity**  
JSON can be verbose - large projects might have unwieldy source.json files

**👥 Not Human-Optimized**  
Reading raw JSON isn't as pleasant as markdown docs for humans (though agents don't mind)

**🚧 Prototype Limitations**  
Conventions still evolving, tooling is minimal, edge cases not fully explored

**🔀 Single File Bottleneck**  
All specs in one file can cause merge conflicts in team environments

**✅ No Schema Validation Yet**  
While a schema exists, enforcement and validation tooling is minimal

## Quick Start

1. Clone jkspec into your project (without git history):
   ```bash
   npx degit jkf16m/jkspec your-project/.jkspec-base
   ```

2. Copy the template to your project root:
   ```bash
   cp your-project/.jkspec-base/jkspec-template/.jkspec/source.json your-project/.jkspec/source.json
   ```

3. Update the `project` section in `.jkspec/source.json` with your project details
4. Add your own specs to the `specs` object using kebab-case keys
5. Query with jq: `jq '.specs' .jkspec/source.json`

For AI agents: Point your agent to `.jkspec/source.json` and give it access to `jq`.

## Core Concepts

**Specs**  
Each spec has a `__meta` object (type, description, status, tags) plus any custom fields

**Status Lifecycle**  
draft → active → deprecated

**Hierarchical Structure**  
Specs can nest using keys like children, components, endpoints, tests, etc.

**Internal Specs**  
Specs prefixed with `__` are internal/meta specs (like `__jkspec` itself)

**jq Queries**  
Direct JSON manipulation using jq for all read/write operations

## Examples

**List all specs:**
```bash
jq '.specs | keys' .jkspec/source.json
```

**Get a specific spec:**
```bash
jq '.specs["spec-name"]' .jkspec/source.json
```

**Find all draft specs:**
```bash
jq '.specs | to_entries[] | select(.value.__meta.status == "draft")' .jkspec/source.json
```

**Filter by type:**
```bash
jq '.specs | to_entries[] | select(.value.__meta.type == "api")' .jkspec/source.json
```

## Use Cases

When jkspec might be useful:

- Working with AI coding agents frequently
- Want to reduce agent context-gathering overhead
- Need structured, queryable project documentation
- Exploring spec-driven development approaches
- Building agent-first development workflows

## Support

If you find jkspec useful or interesting, consider buying me a coffee! This is a personal experiment and any support helps me continue exploring ideas like this.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/jdfm24)
