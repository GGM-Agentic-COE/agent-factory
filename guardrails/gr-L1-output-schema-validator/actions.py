"""gr-L1-output-schema-validator: Deterministic schema validation."""
import json
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-output-schema-validator")

REQUIRED_TOP = ["agent_id", "agent_version", "execution_id", "input_summary", "output"]
VALID_OUTPUT_TYPES = ["story", "epic", "test_case", "code", "design", "document", "decision", "api_spec", "config", "report", "fact"]


def _validate_structure(data: dict) -> list:
    errors = []
    for field in REQUIRED_TOP:
        if field not in data or data[field] is None:
            errors.append(f"missing required field: {field}")

    if "agent_id" in data and data["agent_id"]:
        if not re.match(r'^L[0-4]-.*-agent$', str(data["agent_id"])):
            errors.append("agent_id format invalid (expected L[0-4]-*-agent)")

    if "execution_id" in data and data["execution_id"]:
        if not str(data["execution_id"]).startswith("exec-"):
            errors.append("execution_id format invalid (expected exec-*)")

    if "agent_version" in data and data["agent_version"]:
        if not re.match(r'^\d+\.\d+\.\d+$', str(data["agent_version"])):
            errors.append("agent_version format invalid (expected x.y.z)")

    inp = data.get("input_summary", {})
    if isinstance(inp, dict):
        if "source" not in inp:
            errors.append("input_summary.source missing")
        if "parameters" not in inp or not inp.get("parameters"):
            errors.append("input_summary.parameters missing or empty")

    out = data.get("output", {})
    if isinstance(out, dict):
        if "type" not in out:
            errors.append("output.type missing")
        elif out["type"] not in VALID_OUTPUT_TYPES:
            errors.append(f"output.type invalid: {out['type']}")
        if "schema_version" not in out:
            errors.append("output.schema_version missing")
        items = out.get("items", [])
        if not items and out.get("status") != "failure":
            errors.append("output.items is empty")
        for i, item in enumerate(items):
            meta = item.get("metadata", {})
            if not meta.get("reasoning"):
                errors.append(f"item[{i}].metadata.reasoning missing")
            if not meta.get("citation"):
                errors.append(f"item[{i}].metadata.citation missing")

    return errors


@action()
async def validate_output_schema(output: str) -> bool:
    """Validate output against AgentOutput schema."""
    try:
        data = json.loads(output) if isinstance(output, str) else output
        if not isinstance(data, dict):
            return False
        errors = _validate_structure(data)
        if errors:
            logger.warning(f"SCHEMA_VALIDATOR: {errors}")
            return False
        return True
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"SCHEMA_VALIDATOR: parse error: {e}")
        return False
