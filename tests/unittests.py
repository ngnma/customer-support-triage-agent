# tests/unittests.py
import json

from support_triage.schemas import Ticket
from support_triage.utils import parse_ticket   # change "utils" if your module has another name


def test_parse_ticket_valid(tmp_path):
    """A well-formed ticket file returns a Ticket with the same content."""
    # Arrange: build the input. tmp_path is a fresh temp folder pytest gives you.
    ticket_file = tmp_path / "ticket.json"
    ticket_file.write_text(
        json.dumps({"content": "My order hasn't arrived."}),
        encoding="utf-8",
    )

    # Act: call the ONE function you're testing.
    ticket = parse_ticket(ticket_file)

    # Assert: check the result matches what you expect.
    assert isinstance(ticket, Ticket)
    assert ticket.content == "My order hasn't arrived."