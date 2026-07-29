"""Thin wrapper around SkyLink API's flight_status endpoint (via RapidAPI)."""

import requests

BASE_URL = "https://skylink-api.p.rapidapi.com/v3"
HOST = "skylink-api.p.rapidapi.com"


def get_flight_status(flight_iata: str, api_key: str) -> dict:
    """Fetch live status for a flight number, e.g. 'EY239'.

    Returns the parsed JSON dict, or raises requests.HTTPError on failure.
    """
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": HOST}
    resp = requests.get(f"{BASE_URL}/flight_status/{flight_iata}", headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()


def to_row(flight_iata: str, data: dict, pulled_at_iso: str) -> dict:
    """Flatten SkyLink's response into the flat row shape used in our CSV."""
    dep = data.get("departure") or {}
    arr = data.get("arrival") or {}
    sched_dep = dep.get("scheduled_time") or ""
    return {
        "pulled_at_utc": pulled_at_iso,
        "flight_date": sched_dep[:10] if sched_dep else "",
        "flight_number": data.get("flight_number", flight_iata),
        "status": data.get("status"),
        "delay_minutes": data.get("delay_minutes"),
        "dep_airport": dep.get("airport"),
        "dep_scheduled": dep.get("scheduled_time"),
        "dep_estimated": dep.get("estimated_time"),
        "dep_actual": dep.get("actual_time"),
        "arr_airport": arr.get("airport"),
        "arr_scheduled": arr.get("scheduled_time"),
        "arr_estimated": arr.get("estimated_time"),
        "arr_actual": arr.get("actual_time"),
    }
