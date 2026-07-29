"""Thin wrapper around AviationStack's free real-time flights endpoint."""

import requests

API_URL = "http://api.aviationstack.com/v1/flights"  # free plan is HTTP only, not HTTPS


def get_flight_status(flight_iata: str, api_key: str) -> dict:
    """Fetch the most recent live/scheduled entry for a flight number, e.g. 'EY239'.

    Returns the first matching flight dict, or {} if none found.
    """
    resp = requests.get(API_URL, params={"access_key": api_key, "flight_iata": flight_iata}, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "AviationStack API error"))
    data = payload.get("data") or []
    return data[0] if data else {}


def to_row(flight_iata: str, flight: dict, pulled_at_iso: str) -> dict:
    """Flatten AviationStack's response into the flat row shape used in our CSV."""
    dep = flight.get("departure") or {}
    arr = flight.get("arrival") or {}
    return {
        "pulled_at_utc": pulled_at_iso,
        "flight_date": flight.get("flight_date"),
        "flight_number": (flight.get("flight") or {}).get("iata", flight_iata),
        "status": flight.get("flight_status"),
        "delay_minutes": dep.get("delay") or arr.get("delay") or "",
        "dep_airport": dep.get("iata"),
        "dep_scheduled": dep.get("scheduled"),
        "dep_estimated": dep.get("estimated"),
        "dep_actual": dep.get("actual"),
        "arr_airport": arr.get("iata"),
        "arr_scheduled": arr.get("scheduled"),
        "arr_estimated": arr.get("estimated"),
        "arr_actual": arr.get("actual"),
    }
