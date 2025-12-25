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
    
    # Update the field and automatically set status to "draft" if updating any field other than status
    if [[ "$field" == "status" ]]; then
        # Direct status update - don't override
        jq --arg id "$spec_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$id][$field] = $value' \
           "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
    else
        # Any other field update - set status to draft automatically
        jq --arg id "$spec_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$id][$field] = $value | .specs[$id].status = "draft"' \
           "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
        warn "Spec '$spec_id' status automatically set to 'draft' due to modification"
    fi
    
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

# Add a child spec to a parent spec
cmd_add_child() {
    check_jspec
    
    local parent_id="$1"
    local child_key="$2"
    local child_id="$3"
    local type="$4"
    local description="$5"
    shift 5
    local tags=("$@")
    
    [[ -z "$parent_id" ]] && error "Parent spec ID is required. Usage: jspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$child_key" ]] && error "Child key is required (e.g., 'children', 'specs', 'tests'). Usage: jspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$child_id" ]] && error "Child spec ID is required. Usage: jspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$type" ]] && error "Type is required. Usage: jspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$description" ]] && error "Description is required. Usage: jspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    
    # Check if parent spec exists
    jq -e ".specs[\"$parent_id\"]" "$JSPEC_FILE" >/dev/null 2>&1 || error "Parent spec '$parent_id' not found"
    
    # Build tags array for jq
    local tags_json="[]"
    if [[ ${#tags[@]} -gt 0 ]]; then
        tags_json=$(printf '%s\n' "${tags[@]}" | jq -R . | jq -s .)
    fi
    
    # Add the child spec and set parent status to draft
    jq --arg parent "$parent_id" \
       --arg key "$child_key" \
       --arg child "$child_id" \
       --arg type "$type" \
       --arg desc "$description" \
       --argjson tags "$tags_json" \
       '.specs[$parent][$key] //= {} | .specs[$parent][$key][$child] = {type: $type, description: $desc, status: "draft", tags: $tags} | .specs[$parent].status = "draft"' \
       "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
    
    warn "Parent spec '$parent_id' status automatically set to 'draft' due to child addition"
    success "Added child spec '$child_id' to '$parent_id.$child_key'"
}

# Update a field in a nested child spec
cmd_update_child() {
    check_jspec
    
    local parent_id="$1"
    local child_key="$2"
    local child_id="$3"
    local field="$4"
    local value="$5"
    
    [[ -z "$parent_id" ]] && error "Parent spec ID is required. Usage: jspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$child_key" ]] && error "Child key is required. Usage: jspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$child_id" ]] && error "Child spec ID is required. Usage: jspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$field" ]] && error "Field is required. Usage: jspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$value" ]] && error "Value is required. Usage: jspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    
    # Check if parent and child exist
    jq -e ".specs[\"$parent_id\"]" "$JSPEC_FILE" >/dev/null 2>&1 || error "Parent spec '$parent_id' not found"
    jq -e ".specs[\"$parent_id\"][\"$child_key\"][\"$child_id\"]" "$JSPEC_FILE" >/dev/null 2>&1 || error "Child spec '$parent_id.$child_key.$child_id' not found"
    
    # Update the field and set both child and parent to draft (unless directly setting status)
    if [[ "$field" == "status" ]]; then
        # Direct status update on child
        jq --arg parent "$parent_id" \
           --arg key "$child_key" \
           --arg child "$child_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$parent][$key][$child][$field] = $value' \
           "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
    else
        # Any other field - set both child and parent to draft
        jq --arg parent "$parent_id" \
           --arg key "$child_key" \
           --arg child "$child_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$parent][$key][$child][$field] = $value | .specs[$parent][$key][$child].status = "draft" | .specs[$parent].status = "draft"' \
           "$JSPEC_FILE" > "$JSPEC_FILE.tmp" && mv "$JSPEC_FILE.tmp" "$JSPEC_FILE"
        warn "Both child '$child_id' and parent '$parent_id' status set to 'draft' due to modification"
    fi
    
    success "Updated child spec '$parent_id.$child_key.$child_id': $field = $value"
}

# Get a nested child spec
cmd_get_child() {
    check_jspec
    
    local parent_id="$1"
    local child_key="$2"
    local child_id="$3"
    
    [[ -z "$parent_id" ]] && error "Parent spec ID is required. Usage: jspec get-child <parent-id> <child-key> <child-id>"
    [[ -z "$child_key" ]] && error "Child key is required. Usage: jspec get-child <parent-id> <child-key> <child-id>"
    [[ -z "$child_id" ]] && error "Child spec ID is required. Usage: jspec get-child <parent-id> <child-key> <child-id>"
    
    jq ".specs[\"$parent_id\"][\"$child_key\"][\"$child_id\"]" "$JSPEC_FILE"
}

# Validate spec structure
cmd_validate() {
    check_jspec
    
    local errors=0
    
    echo "Validating jspec structure..."
    echo
    
    # Check JSON syntax
    if ! jq empty "$JSPEC_FILE" 2>/dev/null; then
        error "Invalid JSON syntax in $JSPEC_FILE"
    fi
    success "✓ JSON syntax valid"
    
    # Check required project fields
    if ! jq -e '.project.name' "$JSPEC_FILE" >/dev/null 2>&1 || [[ "$(jq -r '.project.name' "$JSPEC_FILE")" == "" ]]; then
        warn "✗ project.name is missing or empty"
        ((errors++))
    else
        success "✓ project.name present"
    fi
    
    if ! jq -e '.project.version' "$JSPEC_FILE" >/dev/null 2>&1; then
        warn "✗ project.version is missing"
        ((errors++))
    else
        success "✓ project.version present"
    fi
    
    # Check specs object exists
    if ! jq -e '.specs' "$JSPEC_FILE" >/dev/null 2>&1; then
        error "specs object is missing"
    fi
    success "✓ specs object present"
    
    # Validate each spec
    local spec_ids=$(jq -r '.specs | keys[]' "$JSPEC_FILE")
    local spec_count=0
    
    for spec_id in $spec_ids; do
        ((spec_count++))
        
        # Check kebab-case
        if [[ ! "$spec_id" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
            warn "✗ Spec '$spec_id' does not follow kebab-case convention"
            ((errors++))
        fi
        
        # Check required fields
        if ! jq -e ".specs[\"$spec_id\"].type" "$JSPEC_FILE" >/dev/null 2>&1; then
            warn "✗ Spec '$spec_id' missing 'type' field"
            ((errors++))
        fi
        
        if ! jq -e ".specs[\"$spec_id\"].description" "$JSPEC_FILE" >/dev/null 2>&1; then
            warn "✗ Spec '$spec_id' missing 'description' field"
            ((errors++))
        fi
        
        if ! jq -e ".specs[\"$spec_id\"].status" "$JSPEC_FILE" >/dev/null 2>&1; then
            warn "✗ Spec '$spec_id' missing 'status' field"
            ((errors++))
        else
            local status=$(jq -r ".specs[\"$spec_id\"].status" "$JSPEC_FILE")
            if [[ "$status" != "draft" && "$status" != "active" && "$status" != "deprecated" ]]; then
                warn "✗ Spec '$spec_id' has invalid status '$status' (must be draft, active, or deprecated)"
                ((errors++))
            fi
        fi
    done
    
    success "✓ Validated $spec_count specs"
    
    echo
    if [[ $errors -eq 0 ]]; then
        success "Validation passed! No issues found."
    else
        warn "Validation completed with $errors issue(s) found."
        exit 1
    fi
}

# Show usage
cmd_help() {
    cat <<EOF
jspec - Manage .jspec/source.json specifications

Usage:
  jspec init                                         Initialize a new jspec project
  jspec add-spec <id> <type> <desc> [tags...]        Add a new spec
  jspec update-spec <id> <field> <value>             Update a spec field (auto-drafts)
  jspec remove-spec <id>                             Remove a spec
  jspec list                                         List all spec IDs
  jspec get <id>                                     Get a specific spec
  jspec add-child <parent> <key> <child> <type> <desc> [tags...]
                                                     Add a nested child spec
  jspec update-child <parent> <key> <child> <field> <value>
                                                     Update a child spec field (auto-drafts parent)
  jspec get-child <parent> <key> <child>             Get a nested child spec
  jspec validate                                     Validate jspec structure
  jspec help                                         Show this help message

Examples:
  jspec init
  jspec add-spec auth-api api "Authentication API endpoints" authentication backend
  jspec update-spec auth-api status active
  jspec add-child auth-api endpoints login api "Login endpoint" authentication
  jspec update-child auth-api endpoints login method POST
  jspec get-child auth-api endpoints login
  jspec get auth-api
  jspec list
  jspec validate
  jspec remove-spec auth-api

Notes:
  - Any update (except direct status changes) automatically sets status to "draft"
  - Updating child specs sets both child AND parent to "draft"
  - Child key can be anything (e.g., 'children', 'specs', 'tests', 'endpoints')
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
    add-child)
        shift
        cmd_add_child "$@"
        ;;
    update-child)
        shift
        cmd_update_child "$@"
        ;;
    get-child)
        shift
        cmd_get_child "$@"
        ;;
    validate)
        cmd_validate
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        error "Unknown command: $1. Run 'jspec help' for usage."
        ;;
esac
