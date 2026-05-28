"""Flow runner dry-run tests with mocks."""

from drip_mail.engine.runner import FlowRunner
from drip_mail.providers.base import SendResult
from drip_mail.sources.base import Contact, ContactSource


class MockSource(ContactSource):
    def __init__(self, contacts: list[Contact]) -> None:
        self.contacts = contacts
        self.audit_writes: list[dict] = []
        self.columns_ensured: list[str] = []

    def fetch_contacts(self) -> list[Contact]:
        return self.contacts

    def ensure_audit_columns(self, step_ids: list[str]) -> None:
        self.columns_ensured = step_ids

    def write_audit(
        self,
        contact: Contact,
        step_id: str,
        *,
        status: str,
        sent_at: str = "",
        message_id: str = "",
        error: str = "",
    ) -> None:
        self.audit_writes.append(
            {
                "row": contact.row_index,
                "step_id": step_id,
                "status": status,
                "sent_at": sent_at,
                "message_id": message_id,
                "error": error,
            }
        )


class MockProvider:
    def send(self, **kwargs) -> SendResult:  # noqa: ANN003
        return SendResult(success=True, message_id="mock-123")


def test_dry_run_does_not_write_audit():
    contact = Contact(
        row_index=2,
        fields={
            "Timestamp": "2026-05-27 10:00:00",
            "Name": "Alex",
            "Email": "alex@example.com",
        },
    )
    source = MockSource([contact])
    runner = FlowRunner(source=source, dry_run=True)
    runner.provider = MockProvider()

    stats = runner.run_once(flow_filter="welcome_on_signup")
    assert stats["sent"] == 1
    assert stats["failed"] == 0
    assert source.audit_writes == []
    assert source.columns_ensured == []


def test_send_writes_audit_on_success():
    contact = Contact(
        row_index=2,
        fields={
            "Timestamp": "2026-05-27 10:00:00",
            "Name": "Alex",
            "Email": "alex@example.com",
        },
    )
    source = MockSource([contact])
    runner = FlowRunner(source=source, dry_run=False)
    runner.provider = MockProvider()

    stats = runner.run_once(flow_filter="welcome_on_signup")
    assert stats["sent"] == 1
    assert len(source.audit_writes) == 1
    assert source.audit_writes[0]["status"] == "sent"
    assert source.audit_writes[0]["message_id"] == "mock-123"
