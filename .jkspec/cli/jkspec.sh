#!/bin/bash

# jkspec - Simple shell script to manage .jkspec/source.json

set -e

JKSPEC_FILE=".jkspec/source.json"

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

# Check if .jkspec/source.json exists
check_jkspec() {
    [[ -f "$JKSPEC_FILE" ]] || error ".jkspec/source.json not found. Run 'jkspec init' first."
}

# Initialize a new jkspec project
cmd_init() {
    if [[ -f "$JKSPEC_FILE" ]]; then
        warn ".jkspec/source.json already exists. Skipping initialization."
        exit 0
    fi
    
    mkdir -p .jkspec
    
    cat > "$JKSPEC_FILE" <<'EOF'
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
    
    success "Initialized .jkspec/source.json"
}

# Add a new spec
cmd_add_spec() {
    check_jkspec
    
    local spec_id="$1"
    local type="$2"
    local description="$3"
    shift 3
    local tags=("$@")
    
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jkspec add-spec <spec-id> <type> <description> [tags...]"
    [[ -z "$type" ]] && error "Type is required. Usage: jkspec add-spec <spec-id> <type> <description> [tags...]"
    [[ -z "$description" ]] && error "Description is required. Usage: jkspec add-spec <spec-id> <type> <description> [tags...]"
    
    # Check if spec already exists
    if jq -e ".specs[\"$spec_id\"]" "$JKSPEC_FILE" >/dev/null 2>&1; then
        error "Spec '$spec_id' already exists. Use 'jkspec update-spec' to modify it."
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
       "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
    
    success "Added spec '$spec_id'"
}

# Update a spec field
cmd_update_spec() {
    check_jkspec
    
    local spec_id="$1"
    local field="$2"
    local value="$3"
    
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jkspec update-spec <spec-id> <field> <value>"
    [[ -z "$field" ]] && error "Field is required. Usage: jkspec update-spec <spec-id> <field> <value>"
    [[ -z "$value" ]] && error "Value is required. Usage: jkspec update-spec <spec-id> <field> <value>"
    
    # Check if spec exists
    jq -e ".specs[\"$spec_id\"]" "$JKSPEC_FILE" >/dev/null 2>&1 || error "Spec '$spec_id' not found"
    
    # Update the field and automatically set status to "draft" if updating any field other than status
    if [[ "$field" == "status" ]]; then
        # Direct status update - don't override
        jq --arg id "$spec_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$id][$field] = $value' \
           "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
    else
        # Any other field update - set status to draft automatically
        jq --arg id "$spec_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$id][$field] = $value | .specs[$id].status = "draft"' \
           "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
        warn "Spec '$spec_id' status automatically set to 'draft' due to modification"
    fi
    
    success "Updated spec '$spec_id': $field = $value"
}

# Remove a spec
cmd_remove_spec() {
    check_jkspec
    
    local spec_id="$1"
    
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jkspec remove-spec <spec-id>"
    
    # Check if spec exists
    jq -e ".specs[\"$spec_id\"]" "$JKSPEC_FILE" >/dev/null 2>&1 || error "Spec '$spec_id' not found"
    
    jq --arg id "$spec_id" 'del(.specs[$id])' "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
    
    success "Removed spec '$spec_id'"
}

# List all specs
cmd_list() {
    check_jkspec
    jq -r '.specs | keys[]' "$JKSPEC_FILE"
}

# Get a specific spec
cmd_get() {
    check_jkspec
    
    local spec_id="$1"
    [[ -z "$spec_id" ]] && error "Spec ID is required. Usage: jkspec get <spec-id>"
    
    jq ".specs[\"$spec_id\"]" "$JKSPEC_FILE"
}

# Add a child spec to a parent spec
cmd_add_child() {
    check_jkspec
    
    local parent_id="$1"
    local child_key="$2"
    local child_id="$3"
    local type="$4"
    local description="$5"
    shift 5
    local tags=("$@")
    
    [[ -z "$parent_id" ]] && error "Parent spec ID is required. Usage: jkspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$child_key" ]] && error "Child key is required (e.g., 'children', 'specs', 'tests'). Usage: jkspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$child_id" ]] && error "Child spec ID is required. Usage: jkspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$type" ]] && error "Type is required. Usage: jkspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    [[ -z "$description" ]] && error "Description is required. Usage: jkspec add-child <parent-id> <child-key> <child-id> <type> <description> [tags...]"
    
    # Check if parent spec exists
    jq -e ".specs[\"$parent_id\"]" "$JKSPEC_FILE" >/dev/null 2>&1 || error "Parent spec '$parent_id' not found"
    
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
       "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
    
    warn "Parent spec '$parent_id' status automatically set to 'draft' due to child addition"
    success "Added child spec '$child_id' to '$parent_id.$child_key'"
}

# Update a field in a nested child spec
cmd_update_child() {
    check_jkspec
    
    local parent_id="$1"
    local child_key="$2"
    local child_id="$3"
    local field="$4"
    local value="$5"
    
    [[ -z "$parent_id" ]] && error "Parent spec ID is required. Usage: jkspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$child_key" ]] && error "Child key is required. Usage: jkspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$child_id" ]] && error "Child spec ID is required. Usage: jkspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$field" ]] && error "Field is required. Usage: jkspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    [[ -z "$value" ]] && error "Value is required. Usage: jkspec update-child <parent-id> <child-key> <child-id> <field> <value>"
    
    # Check if parent and child exist
    jq -e ".specs[\"$parent_id\"]" "$JKSPEC_FILE" >/dev/null 2>&1 || error "Parent spec '$parent_id' not found"
    jq -e ".specs[\"$parent_id\"][\"$child_key\"][\"$child_id\"]" "$JKSPEC_FILE" >/dev/null 2>&1 || error "Child spec '$parent_id.$child_key.$child_id' not found"
    
    # Update the field and set both child and parent to draft (unless directly setting status)
    if [[ "$field" == "status" ]]; then
        # Direct status update on child
        jq --arg parent "$parent_id" \
           --arg key "$child_key" \
           --arg child "$child_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$parent][$key][$child][$field] = $value' \
           "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
    else
        # Any other field - set both child and parent to draft
        jq --arg parent "$parent_id" \
           --arg key "$child_key" \
           --arg child "$child_id" \
           --arg field "$field" \
           --arg value "$value" \
           '.specs[$parent][$key][$child][$field] = $value | .specs[$parent][$key][$child].status = "draft" | .specs[$parent].status = "draft"' \
           "$JKSPEC_FILE" > "$JKSPEC_FILE.tmp" && mv "$JKSPEC_FILE.tmp" "$JKSPEC_FILE"
        warn "Both child '$child_id' and parent '$parent_id' status set to 'draft' due to modification"
    fi
    
    success "Updated child spec '$parent_id.$child_key.$child_id': $field = $value"
}

# Get a nested child spec
cmd_get_child() {
    check_jkspec
    
    local parent_id="$1"
    local child_key="$2"
    local child_id="$3"
    
    [[ -z "$parent_id" ]] && error "Parent spec ID is required. Usage: jkspec get-child <parent-id> <child-key> <child-id>"
    [[ -z "$child_key" ]] && error "Child key is required. Usage: jkspec get-child <parent-id> <child-key> <child-id>"
    [[ -z "$child_id" ]] && error "Child spec ID is required. Usage: jkspec get-child <parent-id> <child-key> <child-id>"
    
    jq ".specs[\"$parent_id\"][\"$child_key\"][\"$child_id\"]" "$JKSPEC_FILE"
}

# Validate spec structure
cmd_validate() {
    check_jkspec
    
    local errors=0
    
    echo "Validating jkspec structure..."
    echo
    
    # Check JSON syntax
    if ! jq empty "$JKSPEC_FILE" 2>/dev/null; then
        error "Invalid JSON syntax in $JKSPEC_FILE"
    fi
    success "✓ JSON syntax valid"
    
    # Check required project fields
    if ! jq -e '.project.name' "$JKSPEC_FILE" >/dev/null 2>&1 || [[ "$(jq -r '.project.name' "$JKSPEC_FILE")" == "" ]]; then
        warn "✗ project.name is missing or empty"
        ((errors++))
    else
        success "✓ project.name present"
    fi
    
    if ! jq -e '.project.version' "$JKSPEC_FILE" >/dev/null 2>&1; then
        warn "✗ project.version is missing"
        ((errors++))
    else
        success "✓ project.version present"
    fi
    
    # Check specs object exists
    if ! jq -e '.specs' "$JKSPEC_FILE" >/dev/null 2>&1; then
        error "specs object is missing"
    fi
    success "✓ specs object present"
    
    # Validate each spec
    local spec_ids=$(jq -r '.specs | keys[]' "$JKSPEC_FILE")
    local spec_count=0
    
    for spec_id in $spec_ids; do
        ((spec_count++))
        
        # Check kebab-case
        if [[ ! "$spec_id" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
            warn "✗ Spec '$spec_id' does not follow kebab-case convention"
            ((errors++))
        fi
        
        # Check required fields
        if ! jq -e ".specs[\"$spec_id\"].type" "$JKSPEC_FILE" >/dev/null 2>&1; then
            warn "✗ Spec '$spec_id' missing 'type' field"
            ((errors++))
        fi
        
        if ! jq -e ".specs[\"$spec_id\"].description" "$JKSPEC_FILE" >/dev/null 2>&1; then
            warn "✗ Spec '$spec_id' missing 'description' field"
            ((errors++))
        fi
        
        if ! jq -e ".specs[\"$spec_id\"].status" "$JKSPEC_FILE" >/dev/null 2>&1; then
            warn "✗ Spec '$spec_id' missing 'status' field"
            ((errors++))
        else
            local status=$(jq -r ".specs[\"$spec_id\"].status" "$JKSPEC_FILE")
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
jkspec - Manage .jkspec/source.json specifications

Usage:
  jkspec init                                         Initialize a new jkspec project
  jkspec add-spec <id> <type> <desc> [tags...]        Add a new spec
  jkspec update-spec <id> <field> <value>             Update a spec field (auto-drafts)
  jkspec remove-spec <id>                             Remove a spec
  jkspec list                                         List all spec IDs
  jkspec get <id>                                     Get a specific spec
  jkspec add-child <parent> <key> <child> <type> <desc> [tags...]
                                                     Add a nested child spec
  jkspec update-child <parent> <key> <child> <field> <value>
                                                     Update a child spec field (auto-drafts parent)
  jkspec get-child <parent> <key> <child>             Get a nested child spec
  jkspec validate                                     Validate jkspec structure
  jkspec help                                         Show this help message

Examples:
  jkspec init
  jkspec add-spec auth-api api "Authentication API endpoints" authentication backend
  jkspec update-spec auth-api status active
  jkspec add-child auth-api endpoints login api "Login endpoint" authentication
  jkspec update-child auth-api endpoints login method POST
  jkspec get-child auth-api endpoints login
  jkspec get auth-api
  jkspec list
  jkspec validate
  jkspec remove-spec auth-api

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
        error "Unknown command: $1. Run 'jkspec help' for usage."
        ;;
esac
