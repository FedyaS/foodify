# Foodify

Foodify helps users discover restaurants that fit exactly what they are craving.  
The app asks for preferred food types, location, search radius, vibe, dietary restrictions, budget, and any special requests, then returns ranked restaurant recommendations tailored to those inputs.

## What it does

- Collects user preferences through a guided multi-step React UI.
- Sends those preferences to a Flask backend API.
- Uses OpenAI to generate **3–5 personalized restaurant recommendations**.
- Returns structured results with:
  - restaurant name
  - match score (0–100)
  - cuisine tags
  - distance, price range, and hours
  - vibe tags and dietary notes
  - a short “why you’ll love it” explanation
  - optional menu link

## Tech stack

- **Frontend:** React + Vite
- **Backend:** Flask + Flask-CORS
- **AI layer:** OpenAI API with typed response parsing (Pydantic models)

Foodify is designed to feel fast, opinionated, and personal—more like getting suggestions from a friend than scrolling generic restaurant lists.