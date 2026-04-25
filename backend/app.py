import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from distance import enrich_with_distance
from findRestaurants import find_restaurants
from geocode import build_static_map_url, geocode_restaurants, reverse_geocode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"message": "Backend is running!"})


@app.route("/api/recommendations", methods=["POST"])
def recommendations():
    data = request.get_json()
    user_coords = data.get("user_coords")
    location_str = data.get("location", "Portland, OR")

    if location_str in ("Current Location", ""):
        if user_coords:
            resolved = reverse_geocode(user_coords)
            if resolved:
                logger.info("Resolved 'Current Location' -> '%s'", resolved)
                location_str = resolved
            else:
                logger.warning("Reverse geocode failed, falling back to default")
                location_str = "Portland, OR"
        else:
            logger.warning("'Current Location' sent without coords, falling back to default")
            location_str = "Portland, OR"

    try:
        restaurants = find_restaurants(
            food_picks=data.get("food_picks", []),
            location=location_str,
            radius=data.get("radius", "10 mi"),
            vibes=data.get("vibes", []),
            restrictions=data.get("restrictions", ""),
            price_range=data.get("price_range", ""),
            special_requests=data.get("special_requests", ""),
        )

        restaurants = geocode_restaurants(
            restaurants,
            location_str=location_str,
            user_coords=user_coords,
        )

        restaurants = enrich_with_distance(restaurants, user_coords=user_coords)

        map_image_url = None
        try:
            map_image_url = build_static_map_url(restaurants, user_coords)
        except Exception:
            logger.exception("Failed to build static map URL")

        payload = {
            "restaurants": [r.model_dump() for r in restaurants],
            "map_image_url": map_image_url,
        }
        logger.info("Returning %d restaurants, map_url=%s",
                     len(restaurants), "yes" if map_image_url else "no")
        return jsonify(payload)
    except ValueError as e:
        logger.exception("ValueError in recommendations")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.exception("Unexpected error in recommendations")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
