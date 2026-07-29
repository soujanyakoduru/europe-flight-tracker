"""
Once-a-day background snapshot — NOT a live poller. This exists purely so
that a day you forget to open the dashboard doesn't leave a permanent gap
in your 7-day history (AviationStack's free tier has no historical lookup).

Run via GitHub Actions once daily; the dashboard's Refresh button handles
on-demand freshness separately.
"""

import os
from datetime import datetime, timezone

from aviationstack_client import get_flight_status, to_row
from history_store import upsert_row

FLIGHTS = [f.strip() for f in os.environ.get(
    "FLIGHT_NUMBERS", "EY239,EY153,EY156,EY232"
).split(",") if f.strip()]


def main() -> None:
    api_key = os.environ["AVIATIONSTACK_API_KEY"]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for flight in FLIGHTS:
        try:
            data = get_flight_status(flight, api_key)
            if not data:
                print(f"{flight}: no data returned, skipped")
                continue
            row = to_row(flight, data, now)
            upsert_row(row)
            print(f"{flight}: saved ({row['status']})")
        except Exception as e:
            print(f"{flight}: fetch failed — {e}")


if __name__ == "__main__":
    main()
