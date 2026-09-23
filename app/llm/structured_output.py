import json
from typing import Any

from pydantic import ValidationError

from app.schemas import HRResponse


class StructuredOutputError(Exception):
    """Raised when the LLM response cannot be converted to HRResponse."""
    

def parse_hr_response(content: str) -> HRResponse:
    """
    Parse and validate an LLM response against the HRResponse schema.
    """

    if not content or not content.strip():
        raise StructuredOutputError("LLM returned an empty response.")

    try:
        data: Any = json.loads(content)
        if isinstance(data, dict):
            if "urgency" in data and "priority" not in data:
                data["priority"] = data["urgency"]
            elif "priority" in data and "urgency" not in data:
                data["urgency"] = data["priority"]
    except json.JSONDecodeError as exc:
        raise StructuredOutputError(
            f"LLM response is not valid JSON: {exc}"
        ) from exc

    try:
        return HRResponse.model_validate(data)
    except ValidationError as exc:
        raise StructuredOutputError(
            f"LLM JSON failed schema validation: {exc}"
        ) from exc