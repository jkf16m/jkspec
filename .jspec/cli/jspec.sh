#!/bin/bash

# jspec - Simple shell script to manage .jspec/source.json

set -e

JSPEC_FILE=".jspec/source.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}$1${NC}"
}

warn() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if jq is installed
command -v jq >/dev/null 2>&1 || error "jq is required but not installed. Install it with: apt-get install jq / brew install jq"

# Check if .jspec/source.json exists
check_jspec() {
    [[ -f "$JSPEC_FILE" ]] || error ".jspec/source.json not found. Run 'jspec init' first."
}

# Initialize a new jspec project
cmd_init() {
    if [[ -f "$JSPEC_FILE" ]]; then
        warn ".jspec/source.json already exists. Skipping initialization."
        exit 0
    fi
    
    mkdir -p .jspec
    
    cat > "$JSPEC_FILE" <<'EOF'
{
  "project": {
    "name": "",
    "description": "",
    "version": "0.1.0",
    "architecture": {},
    "conventions": {},
    "decisions": []
  },
  "specs": {}
}
EOF
    
    success "Initialized .jspec/source.json"
}

# Add a new spec
cmd_add_spec() {
    check_jspec
    
    local spec_id="$1"
    local type="$2"
    local description="$3"
    shift 3
    local tags=("$@")
    
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jspec add-spec <spec-id> <type> <description> [tags...]"
    [[ -z "$type" ]] && error "Type is required. Usage: jspec add-spec <spec-id> <type> <description> [tags...]"
    [[ -z "$description" ]] && error "Description is required. Usage: jspec add-spec <spec-id> <type> <description> [tags...]"
    
    # Check if spec already exists
    if jq -e ".specs[\"$spec_id\"]" "$JSPEC_FILE" >/dev/null 2>&1; then
        error "Spec '$spec_id' already exists. Use 'jspec update-spec' to modify it."
    fi
    
    # Build tags array for jq
    local tags_json="[]"
    if [[ ${#tags[@]} -gt 0 ]]; then
        tags_json=$(printf '%s\n' "${tags[@]}" | jq -R . | jq -s .)
    fi
    
    # Add the spec
    jq --arg id "$spec_id" \
       --arg type "$type" \
       --arg desc "$description" \
       --argjson tags "$tags_json" \
       '.specs[$id] = {type: $type, description: $desc, status: "draft", tags: $tags}' \
       "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
    
    success "Added spec '$spec_id'"
}

# Update a spec field
cmd_update_spec() {
    check_jspec
    
    local spec_id="$1"
    local field="$2"
    local value="$3"
    
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jspec update-spec <spec-id> <field> <value>"
    [[ -z "$field" ]] && error "Field is required. Usage: jspec update-spec <spec-id> <field> <value>"
    [[ -z "$value" ]] && error "Value is required. Usage: jspec update-spec <spec-id> <field> <value>"
    
    # Check if spec exists
    jq -e ".specs[\"$spec_id\"]" "$JSPEC_FILE" >/dev/null 2>&1 || error "Spec '$spec_id' not found"
    
    jq --arg id "$spec_id" \
       --arg field "$field" \
       --arg value "$value" \
       '.specs[$id][$field] = $value' \
       "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
    
    success "Updated spec '$spec_id': $field = $value"
}

# Remove a spec
cmd_remove_spec() {
    check_jspec
    
    local spec_id="$1"
    
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jspec remove-spec <spec-id>"
    
    # Check if spec exists
    jq -e ".specs[\"$spec_id\"]" "$JSPEC_FILE" >/dev/null 2>&1 || error "Spec '$spec_id' not found"
    
    jq --arg id "$spec_id" 'del(.specs[$id])' "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
    
    success "Removed spec '$spec_id'"
}

# List all specs
cmd_list() {
    check_jspec
    jq -r '.specs | keys[]' "$JSPEC_FILE"
}

# Get a specific spec
cmd_get() {
    check_jspec
    
    local spec_id="$1"
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jspec get <spec-id>"
    
    jq ".specs[\"$spec_id\"]" "$JSPEC_FILE"
}

# Show usage
cmd_help() {
    cat <<EOF
jspec - Manage .jspec/source.json specifications

Usage:
  jspec init                                    Initialize a new jspec project
  jspec add-spec <id> <type> <desc> [tags...]   Add a new spec
  jspec update-spec <id> <field> <value>        Update a spec field
  jspec remove-spec <id>                        Remove a spec
  jspec list                                    List all spec IDs
  jspec get <id>                                Get a specific spec
  jspec help                                    Show this help message

Examples:
  jspec init
  jspec add-spec auth-api api "Authentication API endpoints" authentication backend
  jspec update-spec auth-api status active
  jspec get auth-api
  jspec list
  jspec remove-spec auth-api
EOF
}

# Main command dispatcher
case "${1:-help}" in
    init)
        cmd_init
        ;;
    add-spec)
        shift
        cmd_add_spec "$@"
        ;;
    update-spec)
        shift
        cmd_update_spec "$@"
        ;;
    remove-spec)
        shift
        cmd_remove_spec "$@"
        ;;
    list)
        cmd_list
        ;;
    get)
        shift
        cmd_get "$@"
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        error "Unknown command: $1. Run 'jspec help' for usage."
        ;;
esac
