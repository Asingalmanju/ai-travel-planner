from urllib.parse import quote


def recommend_hotels(destination, budget=0, days=1, travelers=1):
    """
    Real-world hotel search recommendations.

    The function creates live search links for the destination.
    It does not invent hotel names, ratings, or prices.
    """

    destination = str(destination).strip()

    if not destination:
        return []

    # Google Maps hotel search
    maps_url = (
        "https://www.google.com/maps/search/"
        + quote(f"hotels in {destination}")
    )

    # Google hotel search
    google_url = (
        "https://www.google.com/search?q="
        + quote(f"hotels in {destination}")
    )

    # Booking.com destination search
    booking_url = (
        "https://www.booking.com/searchresults.html?ss="
        + quote(destination)
    )

    # Expedia search
    expedia_url = (
        "https://www.expedia.com/Hotel-Search?"
        + "destination="
        + quote(destination)
    )

    hotels = [
        {
            "name": f"🏨 Hotels in {destination}",
            "price": "Live prices on booking site",
            "rating": "Live ratings on booking site",
            "description": (
                f"Find real hotels and accommodation options "
                f"in {destination}. Compare current prices, "
                f"ratings, locations and facilities."
            ),
            "link": maps_url,
        },
        {
            "name": f"⭐ Top Hotels in {destination}",
            "price": "Check current price",
            "rating": "Check current rating",
            "description": (
                "Search highly rated hotels and compare "
                "different accommodation options."
            ),
            "link": google_url,
        },
        {
            "name": f"🌍 Booking Options in {destination}",
            "price": "Live availability",
            "rating": "Live guest ratings",
            "description": (
                "Browse available properties, rooms, "
                "prices and guest reviews."
            ),
            "link": booking_url,
        },
        {
            "name": f"✈️ Expedia Hotels in {destination}",
            "price": "Live prices",
            "rating": "Live ratings",
            "description": (
                "Search real accommodation options and "
                "compare available stays."
            ),
            "link": expedia_url,
        },
    ]

    return hotels