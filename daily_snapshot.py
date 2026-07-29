"""
Once-a-day background snapshot — NOT a live poller. This exists purely so
that a day you forget to open the dashboard doesn't leave a permanent gap
in your 7-day history (SkyLink's free tier only reaches ~5 days back).

Run via GitHub Actions once daily; the dashboard's Refresh button handles
on-demand freshness separately.
"""

import os
from datetime import datetime, timezone

from skylink_client import get_flight_status, to_row
from history_store import upsert_row

FLIGHTS = [f.strip() for f in os.environ.get(
    "FLIGHT_NUMBERS", "EY239,EY153,EY156,EY232"
).split(",") if f.strip()]


def main() -> None:
    api_key = os.environ["RAPIDAPI_KEY"]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for flight in FLIGHTS:
        try:
            data = get_flight_status(flight, api_key)
            row = to_row(flight, data, now)
            if row["flight_date"]:
                upsert_row(row)
                print(f"{flight}: saved ({row['status']})")
            else:
                print(f"{flight}: no usable date in response, skipped")
        except Exception as e:
            print(f"{flight}: fetch failed — {e}")


if __name__ == "__main__":
    main()
