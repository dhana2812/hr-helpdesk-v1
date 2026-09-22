import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings
from app.observability.cost import calculate_request_cost_float


def start_timer() -> float:
    """
    Start a monotonic timer for request latency measurement.
    """

    return time.perf_counter()


def calculate_latency_ms(
    start_time: float,
) -> float:
    """
    Calculate elapsed request latency in milliseconds.
    """

    return round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )


def write_request_log(
    *,
    request_id: str,
    user_id: str,
    input_tokens: int,
    output_tokens: int,
    model: str,
    tool_names: list[str],
    latency_ms: float,
    status: str,
) -> dict[str, Any]:
    """
    Write one structured request record to a JSONL file.
    """

    cost_usd = calculate_request_cost_float(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "request_id": request_id,
        "user_id": user_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model": model,
        "tool_names": tool_names,
        "latency_ms": latency_ms,
        "status": status,
        "cost_usd": round(cost_usd, 10),
    }

    log_path = Path(settings.log_file)

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with log_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return record