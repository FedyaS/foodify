# Foodify Location Feature — Backend Changes

## Overview
Accept user coordinates, fetch real distance/time data from Google Routes API, enrich restaurant results before returning to frontend.

## New Environment Variable
- `GOOGLE_MAPS_API_KEY` in `.env`
- Optional — if missing, skip all distance/time enrichment and return nulls

## API Contract Changes

### Request — POST `/api/recommendations`
Add optional field:
```json
{
  "user_coords": { "lat": 45.5152, "lng": -122.6784 }
}
```
Nullable. If absent, distance enrichment is skipped.

### Response — each restaurant object gains:
```json
{
  "distance_text": "1.2 mi",
  "drive_time": "8 min",
  "walk_time": "22 min",
  "address": "123 SE Division St, Portland, OR",
  "maps_url": "https://www.google.com/maps/search/?api=1&query=..."
}
```
All nullable. Frontend handles nulls by hiding the element.

## Pydantic Model Changes

Add to `Restaurant`:
```python
address: str | None = Field(default=None, description="Full street address")
distance_text: str | None = Field(default=None, description="Distance from user, e.g. '1.2 mi'")
drive_time: str | None = Field(default=None, description="Driving time, e.g. '8 min'")
walk_time: str | None = Field(default=None, description="Walking time, e.g. '22 min'")
maps_url: str | None = Field(default=None, description="Google Maps search URL")
```

Update the GPT system prompt to ask for `address` in responses. GPT already guesses addresses — now we formalize it.

## New Module: `distance.py`

### `enrich_with_distance(restaurants, user_coords, location_str) -> list[Restaurant]`

Flow:
1. If no `GOOGLE_MAPS_API_KEY` or no `user_coords` → just build `maps_url` from name+location, return
2. For each restaurant, call Google Routes API (Compute Route Matrix) with:
   - Origin: `user_coords`
   - Destination: restaurant address (from GPT) or name + location as fallback
   - Travel modes: DRIVE and WALK
3. Parse response → fill `distance_text`, `drive_time`, `walk_time`
4. Build `maps_url` for each

### Error Handling
- Wrap entire enrichment in try/except
- On any failure: log it, return restaurants with null distance fields
- Per-restaurant failure: skip that restaurant's enrichment, don't fail the batch
- Timeout: 5 second timeout on Google API calls

## Integration in `app.py`

```python
result = find_restaurants(...)
enriched = enrich_with_distance(
    result.restaurants,
    user_coords=data.get("user_coords"),
    location_str=data.get("location", "Portland, OR"),
)
return jsonify({"restaurants": [r.model_dump() for r in enriched]})
```

## Google Routes API Call Shape

```python
import requests

url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
headers = {
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,condition",
}
body = {
    "origins": [{"waypoint": {"location": {"latLng": {"latitude": lat, "longitude": lng}}}}],
    "destinations": [{"waypoint": {"address": address}}],
    "travelMode": "DRIVE",  # or "WALK"
}
response = requests.post(url, json=body, headers=headers, timeout=5)
```

## Graceful Degradation Rules
1. No Google API key → skip enrichment entirely, return GPT data as-is with null distance fields
2. Google API error → log, return nulls
3. Single restaurant geocode fails → skip it, enrich the rest
4. **Never raise to the client. Always return a valid response.**
