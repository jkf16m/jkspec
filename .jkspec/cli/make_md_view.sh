#!/usr/bin/env bash
set -euo pipefail

# Get repository root (two levels up from this script)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Default values for agent-friendly zero-config invocation
SPEC_ID="${1:-__jkspec.components.cli}"
JSON_FILE="${2:-$REPO_ROOT/.jkspec/source.json}"
OUTPUT_MD="${3:-$REPO_ROOT/.tmp/$(echo "$SPEC_ID" | tr '.' '_').md}"

if [ ! -f "$JSON_FILE" ]; then
  echo "Spec JSON file not found: $JSON_FILE" >&2
  exit 2
fi

mkdir -p "$(dirname "$OUTPUT_MD")"

jq -r --arg spec "$SPEC_ID" '
  def section($title; $content):
    if ($content | tostring | length) > 0 then
      "## " + $title + "\n\n" + $content + "\n"
    else
      ""
    end;

  def hashes($n):
    reduce range(0; $n) as $i (""; . + "#");

  def heading($level; $title):
    hashes($level) + " " + ($title | tostring) + "\n\n";

  def format_scalar($value):
    ($value | type) as $type |
    if $type == "boolean" then (if $value then "true" else "false" end)
    elif $type == "number" then ($value | tostring)
    elif $type == "string" then $value
    else ($value | tostring)
    end;

  def render_nested($value; $level):
    if $value == null then ""
    else ($value | type) as $type |
      if $type == "object" then
        ($value | to_entries | map(
          heading($level; .key) + render_nested(.value; $level + 1)
        ) | join("\n"))
      elif $type == "array" then
        ($value | to_entries | map(
          .value as $v |
          .key as $i |
          ($v | type) as $vtype |
          if $vtype == "object" then
            heading($level; ($v.name // $v.title // ("Item " + (($i + 1) | tostring)))) +
            render_nested($v; $level + 1)
          else
            "- " + format_scalar($v)
          end
        ) | join("\n")) + "\n\n"
      else
        format_scalar($value) + "\n\n"
      end
    end;

  def render_meta($meta):
    if $meta == null then "" else render_nested($meta; 3) end;

  def render_requirements($reqs):
    if $reqs == null then "" else render_nested($reqs; 3) end;

  def render_tasks($tasks):
    if $tasks == null then "" else render_nested($tasks; 3) end;

  def render_notes($notes):
    if $notes == null then "" else render_nested($notes; 3) end;

  def render_any($value):
    if $value == null then "" else render_nested($value; 3) end;


  def render_meta($meta):
    if $meta == null then "" else
      "- Type: " + ($meta.type // "unknown") + "\n" +
      "- Status: " + ($meta.status // "unknown") + "\n" +
      (if $meta.tags then "- Tags: " + ($meta.tags | join(", ")) + "\n" else "" end) +
      (if $meta.description then "- Description: " + $meta.description + "\n" else "" end)
    end;

  def indent($level):
    reduce range(0; $level) as $i (""; . + "  ");

  def render_nested($value; $level):
    if $value == null then ""
    else ($value | type) as $type
      | if $type == "object" then
          ($value | to_entries | map(
            indent($level) + "- **" + .key + "**: " +
            ( .value as $v |
              ($v | type) as $vtype |
              if $v == null then "null"
              elif ($vtype == "object" or $vtype == "array") then "\n" + render_nested($v; $level + 1)
              else ($v | tostring)
              end
            )
          ) | join("\n"))
        elif $type == "array" then
          ($value | map(
            indent($level) + "- " +
            ( . as $v |
              ($v | type) as $vtype |
              if $v == null then "null"
              elif ($vtype == "object" or $vtype == "array") then "\n" + render_nested($v; $level + 1)
              else ($v | tostring)
              end
            )
          ) | join("\n"))
        else
          indent($level) + ($value | tostring)
        end
    end;

  def render_requirements($reqs):
    if $reqs == null then "" else
      ($reqs | map("- **" + (.title // .id // "Requirement") + "** (" + (.priority // "n/a") + ")\n  - " + (.description // "") +
        (if .details then .details | map("    - " + .) | join("\n") | ("\n" + .) else "" end)
      ) | join("\n"))
    end;

  def render_tasks($tasks):
    if $tasks == null then "" else
      ($tasks | map("- [" + (if .done then "x" else " " end) + "] " + (.name // "Task") + ": " + (.description // "")) | join("\n"))
    end;

  def render_notes($notes):
    if $notes == null then "" else
      ($notes | map("- " + .) | join("\n"))
    end;

  def render_any($value):
    if $value == null then "" else
      render_nested($value; 0)
    end;

  def get_spec:
    ("specs." + $spec | split(".")) as $path
    | try getpath($path)
      catch error("Spec path " + $spec + " not found")
    ;

  get_spec as $specObj
  | if $specObj == null then
      error("Spec " + $spec + " not found")
    else
      "# Spec: " + $spec + "\n\n" +
      section("Meta"; render_meta($specObj.__meta)) +
      section("Problem"; render_any($specObj.problem)) +
      section("Deliverables"; render_any($specObj.deliverables)) +
      section("Requirements"; render_requirements($specObj.requirements)) +
      section("Implementation"; render_any($specObj.implementation)) +
      section("Workflow"; render_any($specObj.workflow)) +
      section("Testing"; render_any($specObj.testing)) +
      section("Tasks"; render_tasks($specObj.tasks)) +
      section("Notes"; render_notes($specObj.notes))
    end
' "$JSON_FILE" > "$OUTPUT_MD"
