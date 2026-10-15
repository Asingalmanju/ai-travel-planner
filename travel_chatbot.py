import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def travel_chatbot(
    question,
    destination="Worldwide",
    interests=None,
    budget=0
):

    if interests is None:
        interests = []

    if isinstance(interests, list):
        interest_text = ", ".join(interests)
    else:
        interest_text = str(interests)

    prompt = f"""
You are an intelligent worldwide AI Travel Assistant.

Destination:
{destination}

Traveler interests:
{interest_text}

Total travel budget:
₹{budget}

Traveler question:
{question}

Answer the question clearly and practically.

Personalize the answer according to:
- Destination
- Budget
- ALL selected interests

You can help with:
- Places to visit
- Food
- Transportation
- Hotels
- Activities
- Safety
- Packing
- Local customs
- Budget tips
- Travel planning

Do not claim live hotel availability,
live prices, or live weather unless supplied
by the application.

Keep the response easy to understand.
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
            return "⚠️ The AI assistant returned an empty response."

        return answer

    except Exception as error:

        return (
            "⚠️ AI Travel Assistant is currently unavailable.\n\n"
            "Please make sure Ollama is running and "
            "the llama3.2 model is installed.\n\n"
            f"Technical details: {error}"
        )