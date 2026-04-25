from __future__ import annotations

import logging
import os

import requests

from findRestaurants import Restaurant

logger = logging.getLogger(__name__)

ROUTES_URL = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
FIELD_MASK = "originIndex,destinationIndex,duration,distanceMeters,condition"
TIMEOUT = 5


def _make_waypoint(*, lat: float | None = None, lng: float | None = None, address: str | None = None) -> dict:
    """Build a Routes API waypoint from coordinates (preferred) or address."""
    if lat is not None and lng is not None:
        return {"waypoint": {"location": {"latLng": {"latitude": lat, "longitude": lng}}}}
    return {"waypoint": {"address": address or ""}}


def _call_route_matrix(
    api_key: str,
    origin_lat: float,
    origin_lng: float,
    restaurant: "Restaurant",
    travel_mode: str,
) -> dict | None:
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    origin = _make_waypoint(lat=origin_lat, lng=origin_lng)
    if restaurant.lat is not None and restaurant.lng is not None:
        dest = _make_waypoint(lat=restaurant.lat, lng=restaurant.lng)
    else:
        dest = _make_waypoint(address=restaurant.address or restaurant.name)
    body = {
        "origins": [origin],
        "destinations": [dest],
        "travelMode": travel_mode,
    }
    try:
        resp = requests.post(ROUTES_URL, json=body, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        results = resp.json()
        if isinstance(results, list) and results:
            return results[0]
        return None
    except Exception:
        logger.exception("Google Routes API call failed for %s (%s)", restaurant.name, travel_mode)
        return None


def _meters_to_miles(meters: int, cap_miles: float = 50.0) -> str | None:
    """Convert meters to a miles string. Returns None if over cap (unreasonable)."""
    miles = meters / 1609.34
    if miles > cap_miles:
        return None
    return f"{miles:.1f} mi"


def _seconds_to_min(duration_str: str, cap_minutes: int = 0) -> str | None:
    """Convert a duration string like '480s' to '8 min'.
    If cap_minutes > 0 and the result exceeds the cap, return None
    (signals the value is unreasonable and should be hidden)."""
    seconds = int(duration_str.rstrip("s"))
    minutes = max(1, round(seconds / 60))
    if cap_minutes > 0 and minutes > cap_minutes:
        return None
    return f"{minutes} min"


def _enrich_single(
    restaurant: Restaurant,
    api_key: str,
    origin_lat: float,
    origin_lng: float,
) -> Restaurant:
    drive_result = _call_route_matrix(api_key, origin_lat, origin_lng, restaurant, "DRIVE")
    walk_result = _call_route_matrix(api_key, origin_lat, origin_lng, restaurant, "WALK")

    if drive_result and drive_result.get("condition") == "ROUTE_EXISTS":
        if "distanceMeters" in drive_result:
            restaurant.distance_text = _meters_to_miles(drive_result["distanceMeters"])
        if "duration" in drive_result:
            restaurant.drive_time = _seconds_to_min(drive_result["duration"], cap_minutes=180)

    if walk_result and walk_result.get("condition") == "ROUTE_EXISTS":
        if "duration" in walk_result:
            restaurant.walk_time = _seconds_to_min(walk_result["duration"], cap_minutes=300)

    return restaurant


def enrich_with_distance(
    restaurants: list[Restaurant],
    user_coords: dict | None,
) -> list[Restaurant]:
    """Add distance_text, drive_time, and walk_time to each restaurant.
    Requires user_coords and a Google Maps API key. Silently skips if
    either is missing — maps_url is handled by geocode.py."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key or not user_coords:
        return restaurants

    lat = user_coords.get("lat")
    lng = user_coords.get("lng")
    if lat is None or lng is None:
        return restaurants

    for r in restaurants:
        try:
            _enrich_single(r, api_key, lat, lng)
            logger.info("Distance for '%s': %s, drive=%s, walk=%s",
                        r.name, r.distance_text, r.drive_time, r.walk_time)
        except Exception:
            logger.exception("Failed to enrich restaurant: %s", r.name)
    return restaurants
