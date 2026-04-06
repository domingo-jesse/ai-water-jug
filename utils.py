import csv
import io
import json
import math
from datetime import datetime
from typing import Dict, List


def estimate_tokens_from_text(text: str) -> int:
    """Rough token approximation for quick local estimates."""
    characters = len(text or "")
    return max(1, math.ceil(characters / 4))


def ml_to_liters(ml: float) -> float:
    return ml / 1000.0


def ml_to_ounces(ml: float) -> float:
    return ml / 29.5735


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def make_session_summary(
    messages: List[Dict],
    events: List[Dict],
    totals: Dict,
    assumptions: Dict,
) -> Dict:
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "totals": totals,
        "assumptions": assumptions,
        "events": events,
        "messages": messages,
    }


def summary_to_json_bytes(summary: Dict) -> bytes:
    return json.dumps(summary, indent=2).encode("utf-8")


def summary_events_to_csv_bytes(events: List[Dict]) -> bytes:
    output = io.StringIO()
    if not events:
        output.write("index,timestamp,user_tokens,assistant_tokens,total_tokens,water_ml\n")
        return output.getvalue().encode("utf-8")

    fieldnames = list(events[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in events:
        writer.writerow(row)
    return output.getvalue().encode("utf-8")
