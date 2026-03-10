import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def save_output_to_file(response: Any, file_path: str) -> None:
    """Save structured output to disk."""
    target_path = Path(file_path)
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = response if isinstance(response, str) else json.dumps(response, indent=4)
        target_path.write_text(payload, encoding="utf-8")
        logger.info("Output successfully saved to %s", target_path)
    except OSError:
        logger.exception("Failed to save output to %s", target_path)
