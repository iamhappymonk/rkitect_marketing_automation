"""Contact source abstraction."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Contact:
    """One row from the signup sheet."""

    row_index: int  # 1-based sheet row number
    fields: dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: str = "") -> str:
        return (self.fields.get(key) or default).strip()

    def audit_status(self, step_id: str) -> str:
        return self.get(f"{step_id}_status").lower()


class ContactSource(Protocol):
    def fetch_contacts(self) -> list[Contact]: ...

    def ensure_audit_columns(self, step_ids: list[str]) -> None: ...

    def write_audit(
        self,
        contact: Contact,
        step_id: str,
        *,
        status: str,
        sent_at: str = "",
        message_id: str = "",
        error: str = "",
    ) -> None: ...
