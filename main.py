from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

places = [
    {
        "id": 1,
        "name": "Agumbe",
        "district": "Shivamogga",
        "type": "Rainforest",
        "description": "Known as the Cherrapunji of the South, Agumbe is a stunning rainforest village with breathtaking sunsets and rich biodiversity.",
        "budget": "1500-2000/day",
        "stay": "Forest Homestay 800-1200/night",
        "food": "Malnad cuisine, fish curry, akki roti",
        "carry": "Raincoat, trekking shoes, mosquito repellent",
        "best_season": "October - February",
        "rating": 4.7,
        "image": "https://images.unsplash.com/photo-1588416936097-41850ab3d86d?w=400",
        "tags": ["Trekking", "Nature", "Waterfalls"],
        "lat": 13.5024,
        "lng": 75.0952
    },
    {
        "id": 2,
        "name": "Yana Rocks",
        "district": "Uttara Kannada",
        "type": "Rock Formation",
        "description": "Mysterious black crystalline rock formations rising from the forest floor. A geological wonder and trekking paradise.",
        "budget": "1000-1500/day",
        "stay": "Budget hotels 500-800/night",
        "food": "Local Karnataka thali, coconut based dishes",
        "carry": "Trekking shoes, water bottle, sunscreen",
        "best_season": "November - March",
        "rating": 4.6,
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
        "tags": ["Trekking", "Heritage", "Nature"],
        "lat": 14.6269,
        "lng": 74.5647
    },
    {
        "id": 3,
        "name": "Shettihalli Church",
        "district": "Hassan",
        "type": "Heritage",
        "description": "A hauntingly beautiful submerged church that rises from the Hemavathi reservoir during summer. Called the Floating Church of Karnataka.",
        "budget": "800-1200/day",
        "stay": "Homestays 600-900/night",
        "food": "Hassan local food, ragi mudde, sambar",
        "carry": "Camera, comfortable shoes, sunhat",
        "best_season": "June - October (submerged), November - May (visible)",
        "rating": 4.5,
        "image": "https://images.unsplash.com/photo-1548013146-72479768bada?w=400",
        "tags": ["Heritage", "Photography", "Unique"],
        "lat": 13.0550,
        "lng": 76.0364
    },
    {
        "id": 4,
        "name": "St Marys Island",
        "district": "Udupi",
        "type": "Beach",
        "description": "Unique hexagonal basalt rock formations on a pristine island. Accessible only by boat, making it a true hidden gem.",
        "budget": "1200-1800/day",
        "stay": "Udupi hotels 800-1500/night",
        "food": "Fresh seafood, Mangalorean fish curry, neer dosa",
        "carry": "Sunscreen, swimwear, waterproof bag",
        "best_season": "October - May",
        "rating": 4.6,
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400",
        "tags": ["Beach", "Nature", "Island"],
        "lat": 13.3561,
        "lng": 74.6535
    },
    {
        "id": 5,
        "name": "Mullayanagiri",
        "district": "Chikmagalur",
        "type": "Trek",
        "description": "The highest peak in Karnataka at 1930m. A thrilling trek through coffee plantations with panoramic views of the Western Ghats.",
        "budget": "1500-2500/day",
        "stay": "Chikmagalur resorts 1000-2000/night",
        "food": "Coffee, local Karnataka food, bread omelette",
        "carry": "Warm clothes, trekking shoes, torch, first aid",
        "best_season": "September - March",
        "rating": 4.8,
        "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400",
        "tags": ["Trekking", "Hills", "Nature"],
        "lat": 13.3986,
        "lng": 75.7139
    },
    {
        "id": 6,
        "name": "Dandeli",
        "district": "Uttara Kannada",
        "type": "Wildlife",
        "description": "A hidden adventure paradise with white water rafting, jungle safaris and rich wildlife including black panthers.",
        "budget": "2000-3000/day",
        "stay": "Jungle camps 1500-2500/night",
        "food": "Forest camp food, local Karnataka cuisine",
        "carry": "Light clothes, insect repellent, binoculars",
        "best_season": "October - May",
        "rating": 4.7,
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400",
        "tags": ["Wildlife", "Adventure", "Trekking"],
        "lat": 15.2667,
        "lng": 74.6167
    },
    {
        "id": 7,
        "name": "Devarayanadurga",
        "district": "Tumkur",
        "type": "Trek",
        "description": "A rocky hill fortress just 70km from Bengaluru. Perfect weekend getaway with ancient temples and stunning rock formations.",
        "budget": "800-1200/day",
        "stay": "Tumkur hotels 500-1000/night",
        "food": "Darshini food, idli vada, local Karnataka meals",
        "carry": "Trekking shoes, water, snacks, camera",
        "best_season": "October - February",
        "rating": 4.4,
        "image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400",
        "tags": ["Trekking", "Heritage", "Bengaluru Nearby"],
        "lat": 13.3833,
        "lng": 77.0833
    },
    {
        "id": 8,
        "name": "Sakleshpur",
        "district": "Hassan",
        "type": "Hills",
        "description": "A misty hill station surrounded by coffee and tea plantations. Less crowded than Coorg but equally beautiful.",
        "budget": "1500-2500/day",
        "stay": "Plantation stays 1200-2000/night",
        "food": "South Indian breakfast, coffee, local thali",
        "carry": "Light woolens, raincoat, trekking shoes",
        "best_season": "September - March",
        "rating": 4.5,
        "image": "https://images.unsplash.com/photo-1455156218388-5e61b526818b?w=400",
        "tags": ["Hills", "Nature", "Plantation"],
        "lat": 12.9452,
        "lng": 75.7862
    }
]

@app.route("/")
def home():
    return render_template("index.html", places=places)

@app.route("/place/<int:place_id>")
def place_detail(place_id):
    place = next((p for p in places if p["id"] == place_id), None)
    if not place:
        return "Place not found", 404
    return render_template("place.html", place=place)

@app.route("/ai-recommend", methods=["POST"])
def ai_recommend():
    user_input = request.json.get("message", "")
    places_summary = "\n".join([f"- {p['name']} ({p['district']}): {p['type']}, Budget {p['budget']}, Best season {p['best_season']}" for p in places])
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are GemIndia AI, a travel assistant built by Fazil, a developer from Bengaluru.
If anyone asks who built you or who created you, say: I was built by Fazil, a developer from Bengaluru who loves Karnataka travel!
You have knowledge of these places:
{places_summary}

Based on the users preferences, recommend 2-3 places from this list with brief reasons why.
Keep response short, friendly and helpful. Use simple language."""
            },
            {"role": "user", "content": user_input}
        ]
    )
    return jsonify({"reply": response.choices[0].message.content})

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    tag = request.args.get("tag", "")
    results = places
    if query:
        results = [p for p in results if query in p["name"].lower() or query in p["district"].lower() or query in p["type"].lower()]
    if tag:
        results = [p for p in results if tag in p["tags"]]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)