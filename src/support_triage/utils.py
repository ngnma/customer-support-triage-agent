import json
import zlib
from pathlib import Path

from pydantic import ValidationError

from support_triage.schemas import Ticket


class TicketParseError(Exception):
    """Raised when a ticket file cannot be turned into a valid Ticket."""


def parse_ticket(path: str | Path) -> Ticket:
    """Read a ticket JSON file and return a validated Ticket.

    Args:
        path: Path to the ticket JSON file.

    Raises:
        TicketParseError: If the file is missing, is not valid JSON,
            or does not match the Ticket schema.
    """
    path = Path(path)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise TicketParseError(f"Ticket file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise TicketParseError(f"Invalid JSON in {path} (line {e.lineno}): {e.msg}") from e

    if not isinstance(raw, dict):
        raise TicketParseError(f"Ticket file must contain a JSON object: {path}")

    try:
        return Ticket(
            ticket_id=zlib.crc32(str(path).encode("utf-8")),
            content=raw.get("content"),
        )
    except ValidationError as e:
        reasons = [
            f"  - {'.'.join(map(str, err['loc']))}: {err['msg']}"
            for err in e.errors(include_input=False)
        ]
        clean_summary = "\n".join(reasons)
        raise TicketParseError(f"Ticket in {path} does not match the schema:\n{clean_summary}") from e