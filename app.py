print("================================")
print("       AI TRAVEL PLANNER")
print("================================")

destination = input("Where do you want to travel? ").lower()
days = int(input("How many days do you want to stay? "))
budget = input("What is your budget? ₹")
interest = input(
    "What do you like? (beach/adventure/food/history/nature): "
).lower()

print()
print("================================")
print("        YOUR TRAVEL PLAN")
print("================================")

print("Destination:", destination.title())
print("Budget: ₹", budget)
print("Interest:", interest)
print()

# Goa recommendations
goa = {

    "beach": [
        ["Baga Beach", "Calangute Beach", "Anjuna Beach"],
        ["Vagator Beach", "Candolim Beach", "Palolem Beach"],
        ["Colva Beach", "Miramar Beach", "Benaulim Beach"]
    ],

    "history": [
        ["Fort Aguada", "Basilica of Bom Jesus", "Old Goa"],
        ["Se Cathedral", "Chapora Fort", "Reis Magos Fort"],
        ["Church of St. Cajetan", "Archaeological Museum", "Panjim"]
    ],

    "nature": [
        ["Dudhsagar Falls", "Spice Plantation", "Mollem National Park"],
        ["Butterfly Beach", "Cotigao Wildlife Sanctuary", "Palolem"],
        ["Salim Ali Bird Sanctuary", "Netravali Wildlife Sanctuary", "Cabo de Rama"]
    ],

    "adventure": [
        ["Dudhsagar Trek", "River Rafting", "Scuba Diving"],
        ["Parasailing", "Kayaking", "Jet Skiing"],
        ["Snorkeling", "Trekking", "Water Sports"]
    ],

    "food": [
        ["Goan Fish Thali", "Panjim Food Tour", "Local Restaurant"],
        ["Seafood Restaurant", "Goan Bakery", "Night Market"],
        ["Local Food Street", "Traditional Goan Restaurant", "Beach Shack"]
    ]
}


# Check destination
if destination == "goa":

    # Check interest
    if interest in goa:

        recommendations = goa[interest]

        for day in range(1, days + 1):

            print("DAY", day)
            print("-" * 30)

            if day <= len(recommendations):

                today = recommendations[day - 1]

                print("Morning  :", today[0])
                print("Afternoon:", today[1])
                print("Evening  :", today[2])

            else:

                print("More recommendations will be added soon!")

            print()

    else:

        print("Sorry! That interest is not available.")
        print("Try: beach, adventure, food, history or nature")

else:

    print("Currently, personalized recommendations are available for Goa.")

print("================================")
print("Have a wonderful trip! ✈️")
print("================================")