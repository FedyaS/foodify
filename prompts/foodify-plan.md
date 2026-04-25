# Foodify — Implementation Plan

## Concept
Spotify-like recommendation algorithm for restaurants/food. User inputs preferences → AI generates personalized restaurant recommendations.

## Tech Stack
- **Frontend**: React + Vite
- **Backend**: Python Flask
- **AI**: OpenAI API (GPT-4) for recommendation engine
- **Restaurant Data**: Google Places API

## Screens
1. **Food Picker** — 3x3 grid, tap to select, image swaps out, 4 picks total
2. **Preferences** — Location, radius, vibe, restrictions, price, special requests
3. **Loading** — Animated transition
4. **Results** — Restaurant cards with match score, details, summary

---

## Google Stitch Prompt

Design a modern, visually stunning mobile-first web app called "Foodify" — a Spotify-style recommendation engine for restaurants. Dark theme with vibrant food-colored accents (warm oranges, reds, greens). Smooth, polished UI. 4 screens total:

**Screen 1 — "Pick Your Cravings"**
Header: "Foodify" logo (stylized fork-and-waveform icon). Subtext: "Tap foods that look good to you"
Body: A 3x3 grid of high-quality square food photos with subtle rounded corners and a soft shadow. When a photo is tapped, it gets a glowing colored border/checkmark overlay and then smoothly swaps to a new food image. A small progress indicator shows "2 of 4 picked". Bottom: a "Next" button that activates after 4 picks. Clean, minimal, photo-forward layout — the food images are the star.

**Screen 2 — "Set Your Vibe"**
A scrollable form with these sections, each with a subtle section header:
- **Location**: Text input defaulting to "Portland, OR" with a small map pin icon
- **Radius**: Horizontal slider or segmented control (1 mi / 5 mi / 10 mi / 25 mi), default 10 mi
- **Vibe**: Horizontally scrollable pill/chip selectors — Cozy, Lively, Upscale, Authentic, Hidden Gem. Multi-select allowed. Each chip has a small emoji/icon.
- **Food Restrictions**: Small text input with placeholder "e.g. gluten-free, vegan..."
- **Price Range**: Row of 4 tappable buttons — "$10-15" / "$15-25" / "$25-40" / "$40+" — styled as cards or pills
- **Special Requests**: Multiline text area with placeholder "Anything else? e.g. outdoor seating, good for dates..."
Bottom: "Find My Food" button, bold and prominent.

**Screen 3 — "Finding Your Perfect Bite..."**
A beautiful full-screen loading/transition screen. Centered animated illustration or Lottie-style animation — a fork spinning, or food icons orbiting around a plate. Pulsing text below: "Analyzing your taste..." then "Scanning nearby restaurants..." then "Ranking your matches..." — cycling through these messages. Background has a subtle gradient shift animation. This screen should feel premium and exciting.

**Screen 4 — "Your Matches"**
A vertical scrollable list of restaurant result cards. Each card is a rounded rectangle with:
- Left/top: A restaurant photo (landscape, cropped nicely)
- **Restaurant Name** — bold, large
- **Match Score** — a circular badge showing "97/100" in accent color
- **Cuisine tags** as small pills (e.g. "Thai", "Fusion")
- Row of compact info items with icons: 📍 "0.8 mi away" | 💰 "$15-25/person" | 🕐 "Closes 10pm"
- **Vibe**: pill chips matching the ones from Screen 2 (e.g. "Cozy", "Hidden Gem")
- **Dietary note**: "✅ Vegan options available" in green text
- **Why you'll love it**: 1-2 sentence italic description — "A tucked-away Thai spot with bold curries and a candlelit patio that feels like Bangkok at sunset."
- A subtle "View Menu →" link at the bottom of each card

Cards should have generous spacing, soft shadows, and feel like premium content cards. Include 3-4 example restaurant cards with realistic fake data.

Overall style: Dark background (#0a0a0a or similar), cards slightly lighter (#1a1a1a), accent colors warm orange (#FF6B35) and soft green (#4CAF50). Typography is clean sans-serif (Inter or similar). Everything feels like a premium consumer app — think Spotify meets Yelp meets a high-end food magazine.
