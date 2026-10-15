import requests


def generate_ai_plan(
    destination,
    days,
    budget,
    interests,
    verified_location=None
):
    """
    Generate a personalized travel plan using local
    Ollama + Llama 3.2.

    verified_location contains information obtained
    from the location/geocoding service so that the AI
    does not guess the destination's geography.
    """

    destination = str(destination).strip()

    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 3

    try:
        budget = float(budget)
    except (ValueError, TypeError):
        budget = 0

    # --------------------------------------------------
    # INTERESTS
    # --------------------------------------------------

    if isinstance(interests, list):

        selected_interests = [
            str(item).strip()
            for item in interests
            if str(item).strip()
        ]

        interest_text = (
            ", ".join(selected_interests)
            if selected_interests
            else "General sightseeing"
        )

    else:

        interest_text = str(interests).strip()

        if not interest_text:
            interest_text = "General sightseeing"

    # --------------------------------------------------
    # VERIFIED LOCATION
    # --------------------------------------------------

    if verified_location:
        location_text = str(verified_location).strip()
    else:
        location_text = destination

    # --------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------

    prompt = f"""
You are an expert worldwide travel planner.

Create a practical, realistic and personalized travel
itinerary.

==================================================
VERIFIED TRIP INFORMATION
==================================================

USER ENTERED DESTINATION:
{destination}

VERIFIED LOCATION:
{location_text}

NUMBER OF DAYS:
{days}

TOTAL BUDGET:
₹{budget:,.0f}

TRAVELER INTERESTS:
{interest_text}

==================================================
CRITICAL LOCATION RULE
==================================================

The user entered:

{destination}

The verified location information is:

{location_text}

The VERIFIED LOCATION is the source of truth.

You MUST NOT guess the state, country, city,
district or geographical location.

You MUST use the verified location information.

NEVER change the destination to another place.

NEVER substitute another city or state.

NEVER invent geographical information.

For example:

If the verified location says:

Gokarna, Karnataka, India

then the entire itinerary must be about:

Gokarna, Karnataka, India.

Do NOT say that Gokarna is in Maharashtra.

If the verified location says:

Goa, India

then create the plan for Goa, India.

If the verified location says:

Paris, France

then create the plan for Paris, France.

If the verified location says:

Tokyo, Japan

then create the plan for Tokyo, Japan.

==================================================
DESTINATION TITLE
==================================================

The title MUST use the user's destination:

# ✈️ {destination} Travel Plan

==================================================
INTERESTS
==================================================

The traveler selected:

{interest_text}

You MUST use ALL selected interests.

Spread them naturally throughout the itinerary.

Do not focus on only one interest.

==================================================
TRIP OVERVIEW
==================================================

## 🧳 Trip Overview

Describe the VERIFIED destination.

Use the verified location information:

{location_text}

Do not guess its state or country.

Explain why this destination matches
the traveler's interests.

==================================================
PERSONALIZED INTERESTS
==================================================

## ❤️ Personalized Interests

List and explain how ALL selected interests
are included in the trip.

==================================================
BUDGET
==================================================

## 💰 Budget

The total budget is:

₹{budget:,.0f}

Give a reasonable estimated division between:

- Accommodation
- Food
- Transportation
- Activities
- Other expenses

Do not claim exact live prices.

==================================================
DAY-BY-DAY ITINERARY
==================================================

Create EXACTLY {days} days.

Every day MUST contain:

### 🌅 Morning

### ☀️ Afternoon

### 🌆 Evening

All activities must be relevant to:

{destination}

and:

{location_text}

Do not randomly include attractions
from another city.

==================================================
DAY FORMAT
==================================================

## 📅 Day 1

### 🌅 Morning

Activity in {destination}.

### ☀️ Afternoon

Activity in {destination}.

### 🌆 Evening

Activity in {destination}.

Continue the same format until:

## 📅 Day {days}

==================================================
FOOD
==================================================

## 🍴 Food Recommendations

Recommend local food relevant to:

{location_text}

==================================================
ACCOMMODATION
==================================================

## 🏨 Accommodation Area

Suggest suitable areas or neighborhoods
within or near:

{destination}

Consider:

- Budget
- Location
- Safety
- Attractions
- Transportation

Do not claim live availability.

==================================================
TRANSPORTATION
==================================================

## 🚕 Transportation

Suggest suitable transportation options
for:

{destination}

==================================================
LOCAL GUIDE TIPS
==================================================

## 🧑‍🏫 Local Guide Tips

Give practical tips specifically for:

{destination}

==================================================
SAFETY
==================================================

## ⚠️ Safety & Important Tips

Give general safety advice for:

{destination}

==================================================
FINAL RULES
==================================================

1. The USER ENTERED DESTINATION is:
   {destination}

2. The VERIFIED LOCATION is:
   {location_text}

3. VERIFIED LOCATION is the source of truth.

4. NEVER change the destination.

5. NEVER guess the state or country.

6. NEVER say Gokarna is in Maharashtra
   when the verified location says Karnataka.

7. Create EXACTLY {days} days.

8. Every day must contain Morning,
   Afternoon and Evening.

9. Use ALL selected interests:
   {interest_text}

10. Keep activities relevant to the destination.

11. Do not invent live hotel prices.

12. Do not invent live weather.

13. Do not claim real-time availability.

14. Do not use attractions from another city.

15. Do not randomly change the destination.

Now generate the complete travel plan.
"""

    # --------------------------------------------------
    # OLLAMA
    # --------------------------------------------------

    ollama_url = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:

        response = requests.post(
            ollama_url,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        ai_response = data.get(
            "response",
            ""
        ).strip()

        if not ai_response:
            return (
                "⚠️ Llama 3.2 did not return a "
                "travel plan."
            )

        return ai_response

    except requests.exceptions.ConnectionError:

        return (
            "⚠️ Ollama is not running.\n\n"
            "Please start Ollama and make sure "
            "Llama 3.2 is available."
        )

    except requests.exceptions.Timeout:

        return (
            "⚠️ The local AI took too long to respond.\n\n"
            "Please try again."
        )

    except Exception as error:

        return (
            "⚠️ Local AI could not generate "
            "the travel plan.\n\n"
            f"Error: {error}"
        )