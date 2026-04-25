import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


class Restaurant(BaseModel):
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


class FoodifyResponse(BaseModel):
    restaurants: list[Restaurant] = Field(description="List of 3-5 recommended restaurants, ranked by match_score descending")


SYSTEM_PROMPT = (
    "You are Foodify, a restaurant recommendation engine. "
    "Given a user's food preferences, location, vibe, dietary restrictions, "
    "and budget, return 3-5 personalized restaurant recommendations. "
    "Rank by match_score (0-100). Be specific, vivid, and opinionated "
    "in the 'why_youll_love_it' field."
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
) -> FoodifyResponse:
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

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format=FoodifyResponse,
    )

    return response.choices[0].message.parsed
