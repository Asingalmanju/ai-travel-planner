import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def get_tour_guide(place, interests):

    if isinstance(interests, list):
        interest_text = ", ".join(interests)
    else:
        interest_text = str(interests)

    prompt = f"""
You are an expert worldwide travel tour guide.

Place: {place}

Traveler interests:
{interest_text}

Create useful information about this place.

Return information suitable for a travel-planning application.

Include:
1. A short description of the place
2. Best time to visit
3. Recommended duration
4. Five practical travel tips

Consider ALL of the traveler's interests.

Do not invent exact live prices, live weather,
or exact opening hours.
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            raise Exception("Ollama returned an empty response.")

        return {
            "name": place,
            "about": answer,
            "best_time": "Check the current seasonal conditions before travelling.",
            "duration": "Around 2–4 hours depending on the attraction.",
            "tips": [
                "Carry a valid ID and necessary travel documents.",
                "Respect local rules and customs.",
                "Keep your belongings secure.",
                "Check current weather before visiting.",
                "Follow official safety instructions."
            ]
        }

    except Exception as error:

        return {
            "name": place,
            "about": (
                "The local AI tour guide is currently unavailable."
            ),
            "best_time": "Please check current local conditions.",
            "duration": "Depends on the attraction.",
            "tips": [
                "Make sure Ollama is running.",
                "Make sure the llama3.2 model is installed.",
                "Try again after starting Ollama."
            ],
            "error": str(error)
        }