"""
Simple flight-tracking dashboard.

- Pick a flight from the dropdown.
- Click "Refresh now" to pull its live status from SkyLink and see the
  last 7 days (built up from your own history file — see README for why).

Run locally:      streamlit run app.py
Deploy free:       push to GitHub, then deploy on share.streamlit.io,
                    adding RAPIDAPI_KEY under the app's Secrets.
"""

import os
from datetime import datetime, timezone

import streamlit as st

from aviationstack_client import get_flight_status, to_row
from history_store import upsert_row, last_n_days

FLIGHTS = ["EY239", "EY153", "EY156", "EY232"]

st.set_page_config(page_title="Flight Tracker", layout="centered")
st.title("✈️ Flight Tracker")

api_key = st.secrets.get("AVIATIONSTACK_API_KEY", os.environ.get("AVIATIONSTACK_API_KEY", ""))
if not api_key:
    st.error("No AVIATIONSTACK_API_KEY found. Add it to .streamlit/secrets.toml (local) "
              "or the app's Secrets (Streamlit Cloud).")
    st.stop()

flight = st.selectbox("Flight", FLIGHTS)
refresh = st.button("🔄 Refresh now", type="primary")

if refresh:
    try:
        data = get_flight_status(flight, api_key)
        if not data:
            st.warning(f"No current data returned for {flight} (it may not be scheduled today).")
        else:
            row = to_row(flight, data, datetime.now(timezone.utc).isoformat(timespec="seconds"))
            upsert_row(row)
            st.success(f"Updated {flight} — {row['status']}"
                       + (f" ({row['delay_minutes']} min delay)" if row.get("delay_minutes") else ""))
    except Exception as e:
        st.error(f"Couldn't fetch live status: {e}")

st.subheader(f"{flight} — last 7 days")
rows = last_n_days(flight, n=7)

if not rows:
    st.info("No data yet for this flight. Hit Refresh to fetch today's status, "
            "and the background job will fill in the rest as days pass.")
else:
    display_rows = []
    for r in rows:
        def hhmm(v):
            return v[11:16] if v and len(v) >= 16 else "--"
        display_rows.append({
            "Date": r["flight_date"],
            "Sched Dep": hhmm(r["dep_scheduled"]),
            "Actual Dep": hhmm(r["dep_actual"]) or hhmm(r["dep_estimated"]),
            "Sched Arr": hhmm(r["arr_scheduled"]),
            "Actual Arr": hhmm(r["arr_actual"]) or hhmm(r["arr_estimated"]),
            "Status": r["status"],
            "Delay (min)": r["delay_minutes"] or "",
        })
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

st.caption("Data is self-collected daily + on-demand refresh — see README for why.")
