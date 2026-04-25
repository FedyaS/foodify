import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger(__name__)


class ChatGPTRestaurant(BaseModel):
    """Schema sent to OpenAI — only fields the LLM should fill."""
    name: str = Field(description="Restaurant name")
    match_score: int = Field(description="Match score from 0-100 based on how well this restaurant fits the user's preferences")
    cuisine_tags: list[str] = Field(description="Short cuisine/style labels, e.g. 'Thai', 'Fusion', 'Brunch'")
    distance: str = Field(description="Human-readable distance, e.g. '0.8 mi away'")
    price_range: str = Field(description="Price per person bracket, e.g. '$15-25/person'")
    hours: str = Field(description="Current closing time, e.g. 'Closes 10pm'")
    vibe_tags: list[str] = Field(description="Vibe descriptors from: Cozy, Lively, Upscale, Authentic, Hidden Gem")
    dietary_note: str = Field(description="Dietary accommodation note, e.g. 'Vegan options available'")
    why_youll_love_it: str = Field(description="1-2 sentence personalized description of why this matches the user")
    menu_url: str | None = Field(default=None, description="URL to the restaurant's menu, if known")
    address: str | None = Field(default=None, description="Full street address")


class Restaurant(ChatGPTRestaurant):
    """Extended model with fields populated by geocoding and distance APIs."""
    lat: float | None = Field(default=None, description="Latitude from Google Places geocoding")
    lng: float | None = Field(default=None, description="Longitude from Google Places geocoding")
    place_id: str | None = Field(default=None, description="Google Maps place_id for exact linking")
    distance_text: str | None = Field(default=None, description="Distance from user, e.g. '1.2 mi'")
    drive_time: str | None = Field(default=None, description="Driving time, e.g. '8 min'")
    walk_time: str | None = Field(default=None, description="Walking time, e.g. '22 min'")
    maps_url: str | None = Field(default=None, description="Google Maps URL for this restaurant")


class FoodifyResponse(BaseModel):
    restaurants: list[ChatGPTRestaurant] = Field(description="List of 3-5 recommended restaurants, ranked by match_score descending")


SYSTEM_PROMPT = (
    "You are Foodify, a restaurant recommendation engine. "
    "Given a user's food preferences, location, vibe, dietary restrictions, "
    "and budget, you MUST return 3-5 real restaurant recommendations that actually "
    "exist in or near the specified location. "
    "NEVER return an empty list. Always recommend real, well-known restaurants. "
    "Rank by match_score (0-100). Be specific, vivid, and opinionated "
    "in the 'why_youll_love_it' field. "
    "Always include the full street address for each restaurant in the 'address' field. "
    "If the location says 'Current Location', treat it as a general request and "
    "recommend popular restaurants in a major nearby city."
)


def build_user_prompt(
    food_picks: list[str],
    location: str,
    radius: str,
    vibes: list[str],
    restrictions: str,
    price_range: str,
    special_requests: str,
) -> str:
    return (
        f"I'm craving: {', '.join(food_picks)}.\n"
        f"Location: {location} (within {radius}).\n"
        f"Vibe I want: {', '.join(vibes) if vibes else 'No preference'}.\n"
        f"Dietary restrictions: {restrictions or 'None'}.\n"
        f"Budget: {price_range}.\n"
        f"Special requests: {special_requests or 'None'}."
    )


def find_restaurants(
    food_picks: list[str],
    location: str,
    radius: str,
    vibes: list[str],
    restrictions: str,
    price_range: str,
    special_requests: str,
) -> list[Restaurant]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

    client = OpenAI(api_key=key)

    user_prompt = build_user_prompt(
        food_picks=food_picks,
        location=location,
        radius=radius,
        vibes=vibes,
        restrictions=restrictions,
        price_range=price_range,
        special_requests=special_requests,
    )

    logger.info("Sending prompt to OpenAI:\n%s", user_prompt)

    response = client.beta.chat.completions.parse(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format=FoodifyResponse,
    )

    message = response.choices[0].message
    logger.info("OpenAI finish_reason=%s, refusal=%s", response.choices[0].finish_reason, message.refusal)
    logger.info("OpenAI raw content (first 500 chars): %s", (message.content or "")[:500])

    parsed = message.parsed
    if parsed is None:
        logger.error("OpenAI returned None parsed result")
        return []

    logger.info("OpenAI returned %d restaurants", len(parsed.restaurants))
    for r in parsed.restaurants:
        logger.info("  -> %s | %s", r.name, r.address)
    return [Restaurant(**r.model_dump()) for r in parsed.restaurants]
