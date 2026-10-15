from urllib.parse import quote


def recommend_transport(
    origin,
    destination,
    travelers=1,
    budget=0,
    travel_date=None
):
    origin = str(origin).strip()
    destination = str(destination).strip()

    if not origin or not destination:
        return []

    # Google Maps route
    maps_base = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote(origin)}"
        f"&destination={quote(destination)}"
    )

    # Direct Rome2Rio route
    rome2rio_url = (
        "https://www.rome2rio.com/map/"
        + quote(origin)
        + "/"
        + quote(destination)
    )

    # Flight search
    flight_url = (
        "https://www.google.com/search?q="
        + quote(f"flights from {origin} to {destination}")
    )

    # Train search
    train_url = (
        "https://www.google.com/search?q="
        + quote(f"trains from {origin} to {destination}")
    )

    # Bus search
    bus_url = (
        "https://www.google.com/search?q="
        + quote(f"buses from {origin} to {destination}")
    )

    return [
        {
            "name": "🌍 All Transport Options",
            "price": "View current route and price information",
            "best_for": "✈️ Flights • 🚆 Trains • 🚌 Buses • ⛴️ Ferries",
            "description": (
                f"Compare real-world transport options from "
                f"{origin} to {destination}."
            ),
            "link": rome2rio_url
        },
        {
            "name": "✈️ Flights",
            "price": "Check current fares",
            "best_for": "Long-distance travel",
            "description": (
                "Search current flight options, airlines "
                "and available fares."
            ),
            "link": flight_url
        },
        {
            "name": "🚆 Trains",
            "price": "Check current fares",
            "best_for": "Rail travel",
            "description": (
                "Search train routes and current travel "
                "information."
            ),
            "link": train_url
        },
        {
            "name": "🚌 Buses",
            "price": "Check current fares",
            "best_for": "Budget travel",
            "description": (
                "Search available bus routes and operators "
                "between your locations."
            ),
            "link": bus_url
        },
        {
            "name": "🚗 Road Travel",
            "price": "Fuel and toll costs vary",
            "best_for": "Car / Road Trip",
            "description": (
                "Open Google Maps for driving directions "
                "between your locations."
            ),
            "link": maps_base + "&travelmode=driving"
        },
        {
            "name": "🚆🚌 Public Transport",
            "price": "Check current route information",
            "best_for": "Local and intercity public transport",
            "description": (
                "Find available public transport routes "
                "using Google Maps."
            ),
            "link": maps_base + "&travelmode=transit"
        }
    ]