"""Shared helpers for reading/writing data/flight_history.csv."""

import csv
import os
from datetime import datetime, timedelta, date

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "flight_history.csv")
FIELDS = [
    "pulled_at_utc", "flight_date", "flight_number", "status", "delay_minutes",
    "dep_airport", "dep_scheduled", "dep_estimated", "dep_actual",
    "arr_airport", "arr_scheduled", "arr_estimated", "arr_actual",
]


def load_all() -> list[dict]:
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))


def upsert_row(row: dict) -> None:
    """Insert row, or overwrite the existing (flight_date, flight_number) row
    with fresher data — so re-fetching the same day just updates it in place."""
    rows = load_all()
    key = (row["flight_date"], row["flight_number"])
    rows = [r for r in rows if (r["flight_date"], r["flight_number"]) != key]
    rows.append(row)
    rows.sort(key=lambda r: (r["flight_number"], r["flight_date"]))

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def last_n_days(flight_number: str, n: int = 7) -> list[dict]:
    cutoff = date.today() - timedelta(days=n - 1)
    out = []
    for r in load_all():
        if r["flight_number"] != flight_number:
            continue
        try:
            d = datetime.strptime(r["flight_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if d >= cutoff:
            out.append(r)
    out.sort(key=lambda r: r["flight_date"])
    return out
