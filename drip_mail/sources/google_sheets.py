"""Google Sheets contact source with audit column management."""

from __future__ import annotations

from pathlib import Path

import json

import gspread
from google.oauth2.service_account import Credentials

from drip_mail.config import (
    GOOGLE_CREDENTIALS_JSON,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_TAB,
)
from drip_mail.sources.base import Contact

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

AUDIT_SUFFIXES = ("status", "sent_at", "message_id", "error")


def audit_column_names(step_id: str) -> dict[str, str]:
    return {suffix: f"{step_id}_{suffix}" for suffix in AUDIT_SUFFIXES}


class GoogleSheetsSource:
    def __init__(
        self,
        sheet_id: str | None = None,
        tab_name: str | None = None,
        credentials_path: str | None = None,
    ) -> None:
        self._sheet_id = sheet_id or GOOGLE_SHEET_ID
        self._tab_name = tab_name or GOOGLE_SHEET_TAB
        self._credentials_path = credentials_path or GOOGLE_SERVICE_ACCOUNT_JSON
        self._worksheet: gspread.Worksheet | None = None
        self._headers: list[str] = []

    def _connect(self) -> gspread.Worksheet:
        if self._worksheet is not None:
            return self._worksheet
        if not self._sheet_id:
            raise ValueError("GOOGLE_SHEET_ID is not set")
        if GOOGLE_CREDENTIALS_JSON:
            info = json.loads(GOOGLE_CREDENTIALS_JSON)
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        else:
            cred_path = Path(self._credentials_path)
            if not cred_path.is_file():
                raise FileNotFoundError(
                    f"Service account JSON not found: {cred_path}"
                )
            creds = Credentials.from_service_account_file(
                str(cred_path), scopes=SCOPES
            )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(self._sheet_id)
        self._worksheet = spreadsheet.worksheet(self._tab_name)
        return self._worksheet

    def _load_headers(self) -> list[str]:
        ws = self._connect()
        row = ws.row_values(1)
        self._headers = [h.strip() for h in row]
        return self._headers

    def _header_index(self, column: str) -> int:
        if column not in self._headers:
            raise KeyError(f"Column {column!r} not found in sheet headers")
        return self._headers.index(column) + 1  # 1-based for gspread

    def ensure_audit_columns(self, step_ids: list[str]) -> None:
        ws = self._connect()
        headers = self._load_headers()
        missing: list[str] = []
        for step_id in step_ids:
            for col in audit_column_names(step_id).values():
                if col not in headers:
                    missing.append(col)
        if not missing:
            return
        start_col = len(headers) + 1
        for i, col_name in enumerate(missing):
            ws.update_cell(1, start_col + i, col_name)
        self._headers = headers + missing

    def fetch_contacts(self) -> list[Contact]:
        ws = self._connect()
        headers = self._load_headers()
        if not headers:
            return []
        records = ws.get_all_records(default_blank="")
        contacts: list[Contact] = []
        for i, record in enumerate(records, start=2):
            fields = {
                str(k).strip(): str(v).strip() if v is not None else ""
                for k, v in record.items()
            }
            contacts.append(Contact(row_index=i, fields=fields))
        return contacts

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
        ws = self._connect()
        if not self._headers:
            self._load_headers()
        cols = audit_column_names(step_id)
        values = {
            cols["status"]: status,
            cols["sent_at"]: sent_at,
            cols["message_id"]: message_id,
            cols["error"]: error,
        }
        cells: list[gspread.Cell] = []
        for col_name, value in values.items():
            col_idx = self._header_index(col_name)
            cells.append(
                gspread.Cell(row=contact.row_index, col=col_idx, value=value)
            )
        ws.update_cells(cells, value_input_option="USER_ENTERED")
