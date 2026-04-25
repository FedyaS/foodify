import logging
import os
from urllib.parse import quote_plus

import requests

from findRestaurants import Restaurant

logger = logging.getLogger(__name__)

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
PLACES_FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.location"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
TIMEOUT = 5


def reverse_geocode(user_coords: dict | None) -> str | None:
    """Turn lat/lng into a human-readable location string like 'Downtown Portland, OR'.
    Returns None if reverse geocoding fails or no coords provided."""
    if not user_coords:
        return None
    lat = user_coords.get("lat")
    lng = user_coords.get("lng")
    if lat is None or lng is None:
        return None

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return None

    try:
        resp = requests.get(
            GEOCODE_URL,
            params={"latlng": f"{lat},{lng}", "key": api_key},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None

        # Try to find neighborhood + city from address components
        neighborhood = None
        city = None
        state = None
        for component in results[0].get("address_components", []):
            types = component.get("types", [])
            if "neighborhood" in types or "sublocality" in types:
                neighborhood = component["short_name"]
            elif "locality" in types:
                city = component["short_name"]
            elif "administrative_area_level_1" in types:
                state = component["short_name"]

        parts = [p for p in [neighborhood, city, state] if p]
        location = ", ".join(parts) if parts else results[0].get("formatted_address", "")
        logger.info("Reverse geocoded (%s, %s) -> '%s'", lat, lng, location)
        return location or None
    except Exception:
        logger.exception("Reverse geocode failed for (%s, %s)", lat, lng)
        return None


def _search_place(
    api_key: str,
    name: str,
    location_str: str,
    user_coords: dict | None,
) -> dict | None:
    """Use Google Places Text Search to find a restaurant by name near a location."""
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": PLACES_FIELD_MASK,
        "Content-Type": "application/json",
    }
    body: dict = {
        "textQuery": f'"{name}" restaurant near {location_str}',
        "maxResultCount": 1,
    }
    if user_coords:
        lat = user_coords.get("lat")
        lng = user_coords.get("lng")
        if lat is not None and lng is not None:
            body["locationBias"] = {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 40000.0,
                }
            }
    try:
        resp = requests.post(PLACES_URL, json=body, headers=headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            logger.error("Places API %d for '%s': %s", resp.status_code, name, resp.text[:500])
            return None
        data = resp.json()
        places = data.get("places", [])
        if places:
            return places[0]
        return None
    except Exception:
        logger.exception("Places Text Search failed for %s", name)
        return None


def _build_place_url(name: str, place_id: str) -> str:
    return (
        f"https://www.google.com/maps/search/?api=1"
        f"&query={quote_plus(name)}&query_place_id={place_id}"
    )


def _build_fallback_url(name: str, address: str | None, location_str: str) -> str:
    query = f"{name}, {address}" if address else f"{name}, {location_str}"
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


def geocode_restaurants(
    restaurants: list[Restaurant],
    location_str: str,
    user_coords: dict | None,
) -> list[Restaurant]:
    """Resolve each restaurant to a real Google place.
    Sets lat, lng, place_id, address, and maps_url on each restaurant.
    If the API is unavailable or a restaurant can't be found, the original
    data is kept and a fallback maps_url is set."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("No GOOGLE_MAPS_API_KEY — skipping geocoding")
        for r in restaurants:
            r.maps_url = _build_fallback_url(r.name, r.address, location_str)
        return restaurants

    for r in restaurants:
        try:
            place = _search_place(api_key, r.name, location_str, user_coords)
            if place:
                loc = place.get("location", {})
                r.lat = loc.get("latitude")
                r.lng = loc.get("longitude")
                r.place_id = place.get("id")
                resolved_address = place.get("formattedAddress")
                if resolved_address:
                    r.address = resolved_address
                logger.info("Geocoded '%s' -> place_id=%s, lat=%s, lng=%s, addr=%s",
                            r.name, r.place_id, r.lat, r.lng, r.address)
                if r.place_id:
                    r.maps_url = _build_place_url(r.name, r.place_id)
                else:
                    r.maps_url = _build_fallback_url(r.name, r.address, location_str)
            else:
                logger.warning("No Places result for: %s", r.name)
                r.maps_url = _build_fallback_url(r.name, r.address, location_str)
        except Exception:
            logger.exception("Geocode failed for restaurant: %s", r.name)
            r.maps_url = _build_fallback_url(r.name, r.address, location_str)

    return restaurants


def build_static_map_url(
    restaurants: list[Restaurant],
    user_coords: dict | None,
) -> str | None:
    """Build a Google Maps Static API URL showing numbered markers for all
    geocoded restaurants. Returns None if no restaurants have coordinates."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return None

    markers = []
    for i, r in enumerate(restaurants):
        if r.lat is not None and r.lng is not None:
            label = str(i + 1) if i < 9 else str(i + 1)
            markers.append(f"markers=color:red%7Clabel:{label}%7C{r.lat},{r.lng}")

    if not markers:
        return None

    if user_coords:
        lat = user_coords.get("lat")
        lng = user_coords.get("lng")
        if lat is not None and lng is not None:
            markers.append(f"markers=color:blue%7Clabel:U%7C{lat},{lng}")

    base = "https://maps.googleapis.com/maps/api/staticmap"
    params = f"size=600x400&scale=2&maptype=roadmap&{'&'.join(markers)}&key={api_key}"
    return f"{base}?{params}"
