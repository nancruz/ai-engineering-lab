"""A small, inspectable JSON Schema subset validator for tool arguments.

Supports: type, properties, required, additionalProperties=false, enum,
minLength, maxLength, pattern, minimum, maximum, items, minItems, maxItems.
The browser workbench (docs/agents/assets/agentlab.js) mirrors this file; the
site tests check that both return identical errors.
"""
import re

TYPE_NAMES = ("object", "string", "integer", "number", "boolean", "array")


def _type_ok(kind, value):
    if kind == "object": return isinstance(value, dict)
    if kind == "string": return isinstance(value, str)
    if kind == "integer": return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number": return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "boolean": return isinstance(value, bool)
    if kind == "array": return isinstance(value, list)
    raise ValueError(f"unsupported schema type: {kind}")


def _num(n):
    return str(int(n)) if isinstance(n, float) and n.is_integer() else str(n)


def validate(schema, value, path="$"):
    """Return a list of {"path", "problem"} dicts. Empty means valid."""
    errors = []
    kind = schema.get("type")
    if kind and not _type_ok(kind, value):
        return [{"path": path, "problem": f"must be of type {kind}"}]
    if "enum" in schema and value not in schema["enum"]:
        errors.append({"path": path, "problem": "must be one of: " + ", ".join(str(v) for v in schema["enum"])})
    if kind == "string":
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append({"path": path, "problem": f"must have at least {schema['minLength']} characters"})
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append({"path": path, "problem": f"must have at most {schema['maxLength']} characters"})
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append({"path": path, "problem": f"must match {schema['pattern']}"})
    if kind in ("integer", "number"):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append({"path": path, "problem": f"must be >= {_num(schema['minimum'])}"})
        if "maximum" in schema and value > schema["maximum"]:
            errors.append({"path": path, "problem": f"must be <= {_num(schema['maximum'])}"})
    if kind == "array":
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append({"path": path, "problem": f"must have at least {schema['minItems']} items"})
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append({"path": path, "problem": f"must have at most {schema['maxItems']} items"})
        if "items" in schema:
            for i, item in enumerate(value):
                errors += validate(schema["items"], item, f"{path}[{i}]")
    if kind == "object":
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                errors.append({"path": f"{path}.{name}", "problem": "is required"})
        for name, item in value.items():
            if name in props:
                errors += validate(props[name], item, f"{path}.{name}")
            elif schema.get("additionalProperties") is False:
                errors.append({"path": f"{path}.{name}", "problem": "is not allowed"})
    return errors


def lint_tool(tool):
    """Heuristic review of a tool definition from the model's point of view."""
    notes = []
    desc = tool.get("description", "")
    if len(desc) < 40:
        notes.append("Description is too short to tell the model what the tool does.")
    if not re.search(r"\b(use|when|before|prefer|never)\b", desc, re.I):
        notes.append("Say when to use (or not use) the tool.")
    if tool.get("side_effect") and "approv" not in desc.lower():
        notes.append("Side-effecting tool should state what approval it needs.")
    schema = tool.get("input_schema", {})
    if schema.get("additionalProperties") is not False:
        notes.append("Set additionalProperties to false so invented arguments are rejected.")
    for name, prop in schema.get("properties", {}).items():
        if prop.get("type") == "string" and not any(k in prop for k in ("enum", "pattern", "maxLength")):
            notes.append(f"Parameter {name} accepts any string; add enum, pattern or maxLength.")
    return notes
