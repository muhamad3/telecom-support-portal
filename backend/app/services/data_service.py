import os
import pandas as pd
from ..models.schemas import DatasetRecord

_records: list[DatasetRecord] | None = None

_XLSX = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Dataset.xlsx")

_CATEGORIES = [
    ("Billing",   ["bill", "charge", "payment", "invoice", "refund", "fee", "pricing"]),
    ("Network",   ["signal", "coverage", "internet", "speed", "outage", "network", "wifi"]),
    ("Technical", ["device", "hardware", "software", "error", "troubleshoot", "firmware"]),
    ("Account",   ["account", "cancel", "upgrade", "plan", "login", "password", "contract"]),
    ("Service",   ["support", "escalat", "complaint", "warranty", "exchange", "appointment"]),
]


def _classify(text: str) -> str:
    t = text.lower()
    for cat, kws in _CATEGORIES:
        for k in kws:
            if k in t:
                return cat
    return "General"


def _priority(text: str) -> str:
    t = text.lower()

    high_words = ["urgent", "critical", "outage", "emergency", "escalate"]
    for w in high_words:
        if w in t:
            return "High"

    medium_words = ["issue", "problem", "error", "fail", "complaint"]
    for w in medium_words:
        if w in t:
            return "Medium"

    return "Low"


def _load() -> list[DatasetRecord]:
    global _records
    if _records is not None:
        return _records

    df = pd.read_excel(_XLSX)
    texts: list[str] = df["text"].dropna().astype(str).tolist()

    _records = []
    i = 1
    for text in texts:
        record = DatasetRecord(
            id=i,
            issue_type=_classify(text),
            message=text.strip(),
            priority=_priority(text),
        )
        _records.append(record)
        i += 1

    return _records


def get_records(
    page: int = 1,
    page_size: int = 10,
    issue_type: str | None = None,
    search: str | None = None,
) -> tuple[list[DatasetRecord], int]:
    rows = _load()

    if issue_type:
        filtered_by_type = []
        for r in rows:
            if r.issue_type.lower() == issue_type.lower():
                filtered_by_type.append(r)
        rows = filtered_by_type

    if search:
        t = search.lower()
        filtered_by_search = []
        for r in rows:
            if t in r.message.lower():
                filtered_by_search.append(r)
        rows = filtered_by_search

    total = len(rows)
    start = (page - 1) * page_size
    return rows[start : start + page_size], total
