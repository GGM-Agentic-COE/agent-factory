"""gr-L1-input-validator: Deterministic input structure validation."""
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-input-validator")

MAX_STRING_LENGTH = 10000

REQUIRED_FIELDS = ["agent_id", "execution_id", "input_summary"]

TYPE_MAP = {
    "agent_id": str,
    "execution_id": str,
    "agent_version": str,
    "input_summary": dict,
}


def _check_required(data: dict) -> list:
    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] is None]
    return missing


def _check_types(data: dict) -> list:
    errors = []
    for field, expected_type in TYPE_MAP.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                errors.append(f"{field}: expected {expected_type.__name__}, got {type(data[field]).__name__}")
    return errors


def _check_lengths(data: dict, max_len: int = MAX_STRING_LENGTH) -> list:
    violations = []
    for key, value in data.items():
        if isinstance(value, str) and len(value) > max_len:
            violations.append(f"{key}: length {len(value)} exceeds max {max_len}")
    return violations


@action()
async def validate_input_structure(input: str) -> bool:
    """Validate input structure deterministically."""
    try:
        data = json.loads(input) if isinstance(input, str) else input
        if not isinstance(data, dict):
            logger.warning("INPUT_VALIDATOR: input is not a JSON object")
            return False

        missing = _check_required(data)
        if missing:
            logger.warning(f"INPUT_VALIDATOR: missing fields: {missing}")
            return False

        type_errors = _check_types(data)
        if type_errors:
            logger.warning(f"INPUT_VALIDATOR: type errors: {type_errors}")
            return False

        length_errors = _check_lengths(data)
        if length_errors:
            logger.warning(f"INPUT_VALIDATOR: length violations: {length_errors}")
            return False

        return True
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"INPUT_VALIDATOR: parse error: {e}")
        return False
