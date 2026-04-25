from flask import Flask, jsonify, request
from flask_cors import CORS

from findRestaurants import find_restaurants

app = Flask(__name__)
CORS(app)


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"message": "Backend is running!"})


@app.route("/api/recommendations", methods=["POST"])
def recommendations():
    data = request.get_json()

    try:
        result = find_restaurants(
            food_picks=data.get("food_picks", []),
            location=data.get("location", "Portland, OR"),
            radius=data.get("radius", "10 mi"),
            vibes=data.get("vibes", []),
            restrictions=data.get("restrictions", ""),
            price_range=data.get("price_range", ""),
            special_requests=data.get("special_requests", ""),
        )
        return jsonify(result.model_dump())
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
