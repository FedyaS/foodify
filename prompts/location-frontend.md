# Foodify Location Feature — Frontend Changes

## Overview
Add real location awareness to the input flow and distance/maps data to the results.

## Input: Location Acquisition

### "Use My Location" Button
- Add a button next to the location text input on Screen 2 (preferences)
- Calls `navigator.geolocation.getCurrentPosition()`
- On success: store lat/lng in state, update the text input to "Current Location" (or reverse-geocoded city name if we want to get fancy later)
- On fail/deny: do nothing, keep the text input as-is (defaults to "Portland, OR")
- Show a brief spinner on the button while the geolocation request is pending
- Never block the flow — user can always just type a location manually

### State Changes
- Add `userCoords` state: `{ lat: number, lng: number } | null`
- Send `user_coords` alongside `location` in the POST to `/api/recommendations`
- Backend uses coords if available, falls back to location string

### Error Handling
- Geolocation denied → no visible error, button just resets
- Geolocation timeout → same, silent fail
- No HTTPS (localhost is fine) → button hidden or disabled

## Output: Distance & Maps on Result Cards

### Google Maps Link
- Construct per restaurant: `https://www.google.com/maps/search/?api=1&query={encodeURIComponent(restaurant.name + ' ' + location)}`
- Display as a map pin icon/link on each card in the info row
- No API key needed for this link

### Distance, Drive Time, Walk Time
- Backend returns these fields per restaurant (see backend doc)
- Display in the card info row:
  - `📍 1.2 mi` (distance)
  - `🚗 8 min` (drive time)
  - `🚶 22 min` (walk time)
- If any field is `null` (API failed), just don't render that item — never show "unknown" or crash

### Google Maps Directions Link
- "Get Directions" link per card
- URL: `https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={encodeURIComponent(restaurant.name + ' ' + location)}`
- If no user coords, just use: `https://www.google.com/maps/dir/?api=1&destination={encodeURIComponent(restaurant.name + ' ' + location)}` (Google will prompt for origin)

## Graceful Degradation Rules
1. No coords + no Google API key → show Google Maps search link only, no distance/time data
2. Coords available but Google API fails → show Google Maps link, hide distance/time
3. Everything works → show full distance, drive time, walk time, directions link
4. **Never crash. Never show broken UI. Just hide what's unavailable.**
