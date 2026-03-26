from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, send_from_directory
from groq import Groq
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, session, redirect
import uuid
import cloudinary
import cloudinary.uploader
from datetime import datetime
from werkzeug.utils import secure_filename
import requests as http_requests
from flask_wtf.csrf import CSRFProtect
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-key-change-this")

# Enable CSRF protection
csrf = CSRFProtect(app)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")
JSONBIN_BIN_ID = os.getenv("JSONBIN_BIN_ID")
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

GEMS_BIN_ID = os.getenv("GEMS_BIN_ID")
GEMS_BIN_URL = f"https://api.jsonbin.io/v3/b/{GEMS_BIN_ID}"

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def load_experiences():
    try:
        res = http_requests.get(JSONBIN_URL + "/latest", headers={"X-Master-Key": JSONBIN_API_KEY})
        data = res.json()
        return data.get("record", {}).get("experiences", [])
    except:
        return []

def save_experiences(experiences):
    try:
        http_requests.put(JSONBIN_URL, json={"experiences": experiences},
            headers={"Content-Type": "application/json", "X-Master-Key": JSONBIN_API_KEY})
    except:
        pass

def load_gems():
    try:
        res = http_requests.get(GEMS_BIN_URL + "/latest", headers={"X-Master-Key": JSONBIN_API_KEY})
        data = res.json()
        return data.get("record", {}).get("gems", [])
    except:
        return []

def save_gems(gems):
    try:
        res = http_requests.put(GEMS_BIN_URL, json={"gems": gems},
            headers={"Content-Type": "application/json", "X-Master-Key": JSONBIN_API_KEY})
        return res.status_code == 200
    except Exception as e:
        print(f"save_gems error: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== ADMIN AUTHENTICATION ====================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me_123")


def check_admin_password(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = request.args.get('password')
        if password != ADMIN_PASSWORD:
            return render_template("admin_login.html")
        return f(*args, **kwargs)

    return decorated_function


# ================================================================
places = [
    {"id": 1, "name": "Agumbe", "district": "Shivamogga", "type": "Rainforest", "description": "Known as the Cherrapunji of the South, Agumbe is a stunning rainforest village with breathtaking sunsets and rich biodiversity.", "budget": "1500-2000/day", "stay": "Forest Homestay 800-1200/night", "food": "Malnad cuisine, fish curry, akki roti", "carry": "Raincoat, trekking shoes, mosquito repellent", "best_season": "October - February", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_1.jpg", "tags": ["Trekking", "Nature", "Waterfalls"], "lat": 13.5024, "lng": 75.0952},
    {"id": 2, "name": "Yana Rocks", "district": "Uttara Kannada", "type": "Rock Formation", "description": "Mysterious black crystalline rock formations rising from the forest floor. A geological wonder and trekking paradise.", "budget": "1000-1500/day", "stay": "Budget hotels 500-800/night", "food": "Local Karnataka thali, coconut based dishes", "carry": "Trekking shoes, water bottle, sunscreen", "best_season": "November - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_2.jpg", "tags": ["Trekking", "Heritage", "Nature"], "lat": 14.6269, "lng": 74.5647},
    {"id": 3, "name": "Shettihalli Church", "district": "Hassan", "type": "Heritage", "description": "A hauntingly beautiful submerged church that rises from the Hemavathi reservoir during summer. Called the Floating Church of Karnataka.", "budget": "800-1200/day", "stay": "Homestays 600-900/night", "food": "Hassan local food, ragi mudde, sambar", "carry": "Camera, comfortable shoes, sunhat", "best_season": "June - October (submerged), November - May (visible)", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_3.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 13.0550, "lng": 76.0364},
    {"id": 4, "name": "St Marys Island", "district": "Udupi", "type": "Beach", "description": "Unique hexagonal basalt rock formations on a pristine island. Accessible only by boat, making it a true hidden gem.", "budget": "1200-1800/day", "stay": "Udupi hotels 800-1500/night", "food": "Fresh seafood, Mangalorean fish curry, neer dosa", "carry": "Sunscreen, swimwear, waterproof bag", "best_season": "October - May", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_4.jpg", "tags": ["Beach", "Nature", "Island"], "lat": 13.3561, "lng": 74.6535},
    {"id": 5, "name": "Mullayanagiri", "district": "Chikmagalur", "type": "Trek", "description": "The highest peak in Karnataka at 1930m. A thrilling trek through coffee plantations with panoramic views of the Western Ghats.", "budget": "1500-2500/day", "stay": "Chikmagalur resorts 1000-2000/night", "food": "Coffee, local Karnataka food, bread omelette", "carry": "Warm clothes, trekking shoes, torch, first aid", "best_season": "September - March", "rating": 4.8, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_5.jpg", "tags": ["Trekking", "Hills", "Nature"], "lat": 13.3986, "lng": 75.7139},
    {"id": 6, "name": "Dandeli", "district": "Uttara Kannada", "type": "Wildlife", "description": "A hidden adventure paradise with white water rafting, jungle safaris and rich wildlife including black panthers.", "budget": "2000-3000/day", "stay": "Jungle camps 1500-2500/night", "food": "Forest camp food, local Karnataka cuisine", "carry": "Light clothes, insect repellent, binoculars", "best_season": "October - May", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_6.jpg", "tags": ["Wildlife", "Adventure", "Trekking"], "lat": 15.2667, "lng": 74.6167},
    {"id": 7, "name": "Devarayanadurga", "district": "Tumkur", "type": "Trek", "description": "A rocky hill fortress just 70km from Bengaluru. Perfect weekend getaway with ancient temples and stunning rock formations.", "budget": "800-1200/day", "stay": "Tumkur hotels 500-1000/night", "food": "Darshini food, idli vada, local Karnataka meals", "carry": "Trekking shoes, water, snacks, camera", "best_season": "October - February", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_7.jpg", "tags": ["Trekking", "Heritage", "Bengaluru Nearby"], "lat": 13.3833, "lng": 77.0833},
    {"id": 8, "name": "Sakleshpur", "district": "Hassan", "type": "Hills", "description": "A misty hill station surrounded by coffee and tea plantations. Less crowded than Coorg but equally beautiful.", "budget": "1500-2500/day", "stay": "Plantation stays 1200-2000/night", "food": "South Indian breakfast, coffee, local thali", "carry": "Light woolens, raincoat, trekking shoes", "best_season": "September - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_8.jpg", "tags": ["Hills", "Nature", "Plantation"], "lat": 12.9452, "lng": 75.7862},
    {"id": 9, "name": "Coorg (Kodagu)", "district": "Kodagu", "type": "Hills", "description": "The Scotland of India — misty coffee hills, cascading waterfalls and warm Kodava hospitality make Coorg a timeless gem.", "budget": "2000-3500/day", "stay": "Coffee estate stays 1500-3000/night", "food": "Pandi curry, kadambuttu, bamboo shoot curry", "carry": "Light woolens, raincoat, camera", "best_season": "October - March", "rating": 4.8, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_9.jpg", "tags": ["Hills", "Nature", "Plantation"], "lat": 12.3375, "lng": 75.8069},
    {"id": 10, "name": "Kabini", "district": "Mysuru", "type": "Wildlife", "description": "Where the forest meets the backwaters — Kabini is Karnataka's finest wildlife destination with elephant herds and leopard sightings.", "budget": "3000-6000/day", "stay": "Jungle lodges 2500-5000/night", "food": "Resort meals, tribal cuisine", "carry": "Binoculars, camera, insect repellent, light clothes", "best_season": "October - May", "rating": 4.9, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_10.jpg", "tags": ["Wildlife", "Nature", "Photography"], "lat": 11.9249, "lng": 76.3449},
    {"id": 11, "name": "Badami", "district": "Bagalkot", "type": "Heritage", "description": "Ancient cave temples carved into red sandstone cliffs overlooking a sacred lake. A UNESCO World Heritage candidate.", "budget": "1000-1800/day", "stay": "Heritage hotels 800-1500/night", "food": "North Karnataka food, jolada rotti, enne badnekai", "carry": "Comfortable shoes, sunscreen, water, camera", "best_season": "October - February", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_11.jpg", "tags": ["Heritage", "Photography", "Trekking"], "lat": 15.9150, "lng": 75.6760},
    {"id": 12, "name": "Hampi", "district": "Vijayanagara", "type": "Heritage", "description": "The ruins of the Vijayanagara Empire spread over boulder-strewn landscapes. One of India's most surreal and magical destinations.", "budget": "1200-2000/day", "stay": "Guesthouses 600-1200/night", "food": "South Indian thali, banana leaf meals", "carry": "Comfortable shoes, hat, sunscreen, water", "best_season": "October - February", "rating": 4.9, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_12.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 15.3350, "lng": 76.4600},
    {"id": 13, "name": "Jog Falls", "district": "Shivamogga", "type": "Waterfalls", "description": "The second highest waterfall in India at 253m. Four distinct falls — Raja, Rani, Rover and Rocket — create a thunderous spectacle.", "budget": "1000-1500/day", "stay": "Budget hotels 600-1000/night", "food": "Local Karnataka food, akki roti, fish curry", "carry": "Raincoat, trekking shoes, camera", "best_season": "July - October", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_13.jpg", "tags": ["Waterfalls", "Nature", "Photography"], "lat": 14.2270, "lng": 74.7982},
    {"id": 14, "name": "Gokarna", "district": "Uttara Kannada", "type": "Beach", "description": "A sacred temple town with pristine beaches. Om Beach, Half Moon Beach and Paradise Beach are far less crowded than Goa.", "budget": "1500-2500/day", "stay": "Beach shacks 800-1500/night", "food": "Seafood, coconut curry, local thali", "carry": "Sunscreen, swimwear, light clothes", "best_season": "October - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_14.jpg", "tags": ["Beach", "Heritage", "Nature"], "lat": 14.5479, "lng": 74.3188},
    {"id": 15, "name": "Nandi Hills", "district": "Chikkaballapur", "type": "Hills", "description": "A classic sunrise destination just 60km from Bengaluru. The fort, temple and misty valleys make it a perfect quick escape.", "budget": "800-1200/day", "stay": "Bengaluru stay recommended", "food": "Local Karnataka food, corn on the cob", "carry": "Light woolens for early morning, camera", "best_season": "October - February", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_15.jpg", "tags": ["Hills", "Bengaluru Nearby", "Photography"], "lat": 13.3702, "lng": 77.6835},
    {"id": 16, "name": "Chikmagalur", "district": "Chikmagalur", "type": "Hills", "description": "The birthplace of coffee in India. Rolling hills covered in coffee, cardamom and pepper plantations with misty Western Ghats views.", "budget": "1500-2500/day", "stay": "Coffee estate bungalows 1200-2500/night", "food": "Fresh filter coffee, local Karnataka thali", "carry": "Light woolens, trekking shoes, raincoat", "best_season": "September - March", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_16.jpg", "tags": ["Hills", "Nature", "Plantation"], "lat": 13.3153, "lng": 75.7754},
    {"id": 17, "name": "Belur & Halebidu", "district": "Hassan", "type": "Heritage", "description": "Twin temples of the Hoysala Empire with the most intricate stone carvings in the world. Every inch is a masterpiece.", "budget": "1000-1500/day", "stay": "Hassan hotels 700-1200/night", "food": "Hassan local food, ragi mudde, bisi bele bath", "carry": "Comfortable shoes, camera, sunhat", "best_season": "October - March", "rating": 4.8, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_17.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 13.1650, "lng": 75.8943},
    {"id": 18, "name": "Kudremukh", "district": "Chikmagalur", "type": "Trek", "description": "The horse-face peak of the Western Ghats. A challenging trek through shola forests, grasslands and misty valleys.", "budget": "1500-2000/day", "stay": "Forest guesthouses 800-1200/night", "food": "Packed meals, local food in Kudremukh town", "carry": "Trekking shoes, raincoat, warm clothes, permit", "best_season": "September - February", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_18.jpg", "tags": ["Trekking", "Nature", "Wildlife"], "lat": 13.1833, "lng": 75.2500},
    {"id": 19, "name": "Mysuru", "district": "Mysuru", "type": "Heritage", "description": "The City of Palaces. Mysore Palace, Chamundi Hills and the famous Dasara celebrations make this a cultural treasure.", "budget": "1500-2500/day", "stay": "Heritage hotels 1000-3000/night", "food": "Mysore pak, masala dosa, palace thali", "carry": "Comfortable shoes, camera, light clothes", "best_season": "October - February", "rating": 4.8, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_19.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 12.2958, "lng": 76.6394},
    {"id": 20, "name": "Bidar", "district": "Bidar", "type": "Heritage", "description": "A forgotten kingdom in North Karnataka with Persian-influenced architecture, Bidar Fort and the famous Bidriware craft.", "budget": "800-1200/day", "stay": "Budget hotels 500-900/night", "food": "Biryani, North Karnataka food, kebabs", "carry": "Comfortable shoes, camera, sunhat", "best_season": "October - February", "rating": 4.3, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_20.jpg", "tags": ["Heritage", "Unique", "Photography"], "lat": 17.9104, "lng": 77.5199},
    {"id": 21, "name": "Aihole", "district": "Bagalkot", "type": "Heritage", "description": "The cradle of Indian temple architecture with over 125 ancient temples. An archaeologist's paradise rarely visited by tourists.", "budget": "800-1200/day", "stay": "Badami hotels 700-1200/night", "food": "North Karnataka thali, jolada rotti", "carry": "Camera, comfortable shoes, water, sunscreen", "best_season": "October - February", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_21.jpg", "tags": ["Heritage", "Unique", "Photography"], "lat": 15.9589, "lng": 75.8786},
    {"id": 22, "name": "Pattadakal", "district": "Bagalkot", "type": "Heritage", "description": "UNESCO World Heritage Site with stunning Chalukya temples. Often skipped by tourists but rivals Hampi in grandeur.", "budget": "800-1200/day", "stay": "Badami hotels 700-1200/night", "food": "North Karnataka food, local thali", "carry": "Camera, comfortable shoes, sunscreen", "best_season": "October - February", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_22.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 15.9483, "lng": 75.8189},
    {"id": 23, "name": "Murudeshwar", "district": "Uttara Kannada", "type": "Beach", "description": "A massive Shiva statue overlooking the Arabian Sea with a stunning temple on a rocky promontory. Dramatic and divine.", "budget": "1200-2000/day", "stay": "Beach resorts 1000-2000/night", "food": "Seafood, coconut-based curries, neer dosa", "carry": "Sunscreen, camera, light clothes", "best_season": "October - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_23.jpg", "tags": ["Beach", "Heritage", "Photography"], "lat": 14.0943, "lng": 74.1051},
    {"id": 24, "name": "Bheemeshwari", "district": "Mandya", "type": "Adventure", "description": "A premier adventure camp on the Cauvery river. Fishing, kayaking and nature walks in pristine forest surroundings.", "budget": "2500-4000/day", "stay": "Jungle lodges 2000-3500/night", "food": "Camp food, Cauvery fish, local cuisine", "carry": "Light clothes, insect repellent, camera", "best_season": "October - May", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_24.jpg", "tags": ["Adventure", "Wildlife", "Nature"], "lat": 12.3667, "lng": 77.1833},
    {"id": 25, "name": "Skandagiri", "district": "Chikkaballapur", "type": "Trek", "description": "The famous night trek destination near Bengaluru. Trekking through clouds at night to catch the sunrise above the mist.", "budget": "600-1000/day", "stay": "Bengaluru stay recommended", "food": "Carry packed food, tea at base", "carry": "Torch, warm clothes, trekking shoes, water", "best_season": "October - February", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_25.jpg", "tags": ["Trekking", "Bengaluru Nearby", "Adventure"], "lat": 13.4167, "lng": 77.7000},
    {"id": 26, "name": "Ramanagara", "district": "Ramanagara", "type": "Adventure", "description": "The Sholay hills! Famous rock climbing destination and silk city. Bouldering, rappelling and the iconic Ramadevarabetta vulture sanctuary.", "budget": "800-1200/day", "stay": "Bengaluru stay or local hotels 600-1000/night", "food": "Local Karnataka food, darshini meals", "carry": "Sports shoes, water, camera", "best_season": "October - February", "rating": 4.3, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_26.jpg", "tags": ["Adventure", "Trekking", "Bengaluru Nearby"], "lat": 12.7167, "lng": 77.2833},
    {"id": 27, "name": "Shivanasamudra", "district": "Mandya", "type": "Waterfalls", "description": "Twin waterfalls — Gaganachukki and Bharachukki — on the Cauvery river. One of the widest waterfalls in India.", "budget": "800-1200/day", "stay": "Mysuru or Mandya stay", "food": "Local Karnataka food", "carry": "Camera, comfortable shoes, raincoat in season", "best_season": "July - November", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_27.jpg", "tags": ["Waterfalls", "Nature", "Photography"], "lat": 12.2667, "lng": 77.1667},
    {"id": 28, "name": "Nagarhole National Park", "district": "Kodagu", "type": "Wildlife", "description": "One of India's finest tiger reserves. Dense teak forests, elephants, tigers, leopards and the magical Kabini river.", "budget": "3000-5000/day", "stay": "Jungle lodges 2500-5000/night", "food": "Resort meals, packed jungle food", "carry": "Binoculars, camera, insect repellent", "best_season": "October - May", "rating": 4.8, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_28.jpg", "tags": ["Wildlife", "Nature", "Photography"], "lat": 11.9833, "lng": 76.1167},
    {"id": 29, "name": "Kollur Mookambika", "district": "Udupi", "type": "Heritage", "description": "A sacred temple town at the foothills of the Western Ghats. The Mookambika temple and the trek to Kodachadri peak are unmissable.", "budget": "1000-1500/day", "stay": "Temple guesthouses 500-1000/night", "food": "Temple prasad, South Indian meals", "carry": "Comfortable clothes, camera, trekking shoes", "best_season": "October - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_29.jpg", "tags": ["Heritage", "Trekking", "Nature"], "lat": 13.8608, "lng": 74.8139},
    {"id": 30, "name": "Kodachadri", "district": "Shivamogga", "type": "Trek", "description": "A sacred peak in the Western Ghats with a small Mookambika temple on top. Stunning 360-degree views and shola forests.", "budget": "1200-1800/day", "stay": "Forest guesthouses 600-1000/night", "food": "Packed meals, basic food at base", "carry": "Trekking shoes, raincoat, warm clothes, torch", "best_season": "October - February", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_30.jpg", "tags": ["Trekking", "Nature", "Heritage"], "lat": 13.8911, "lng": 74.8703},
    {"id": 31, "name": "Uttara Kannada Coast", "district": "Uttara Kannada", "type": "Beach", "description": "Karnataka's secret coastline with pristine beaches like Apsarakonda, Nirvana Beach and Vibhuti Falls near the sea.", "budget": "1000-1800/day", "stay": "Beach resorts 800-1500/night", "food": "Fresh seafood, coconut fish curry", "carry": "Sunscreen, swimwear, camera", "best_season": "October - March", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_31.jpg", "tags": ["Beach", "Nature", "Unique"], "lat": 14.8167, "lng": 74.1333},
    {"id": 32, "name": "Bisle Ghat", "district": "Hassan", "type": "Trek", "description": "One of the most scenic viewpoints in Karnataka. On a clear day you can see three districts and the entire Western Ghats panorama.", "budget": "1000-1500/day", "stay": "Sakleshpur homestays 800-1200/night", "food": "Homestay meals, packed food", "carry": "Trekking shoes, warm clothes, raincoat, camera", "best_season": "September - February", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_32.jpg", "tags": ["Trekking", "Nature", "Photography"], "lat": 12.7833, "lng": 75.7500},
    {"id": 33, "name": "Ranganathittu Bird Sanctuary", "district": "Mysuru", "type": "Wildlife", "description": "A bird watcher's paradise on the Cauvery river. Thousands of migratory birds, crocodiles and otters in a stunning riverine setting.", "budget": "800-1200/day", "stay": "Mysuru hotels 800-1500/night", "food": "Mysuru local food, palace thali", "carry": "Binoculars, camera, sunscreen", "best_season": "June - November", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_33.jpg", "tags": ["Wildlife", "Nature", "Photography"], "lat": 12.4167, "lng": 76.6833},
    {"id": 34, "name": "Bandipur National Park", "district": "Chamarajanagar", "type": "Wildlife", "description": "Part of the Nilgiri Biosphere Reserve. Safari drives through dry deciduous forests with elephants, tigers and gaur.", "budget": "2500-4000/day", "stay": "Forest lodges 2000-4000/night", "food": "Resort meals", "carry": "Binoculars, camera, light cotton clothes", "best_season": "October - May", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_34.jpg", "tags": ["Wildlife", "Nature", "Photography"], "lat": 11.6706, "lng": 76.6342},
    {"id": 35, "name": "Chitradurga Fort", "district": "Chitradurga", "type": "Heritage", "description": "The stone fort of seven circles — a massive labyrinthine fortress on rocky hills. One of Karnataka's most impressive but undervisited forts.", "budget": "800-1200/day", "stay": "Budget hotels 500-900/night", "food": "North Karnataka food, local thali", "carry": "Comfortable shoes, water, camera, sunhat", "best_season": "October - February", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_35.jpg", "tags": ["Heritage", "Trekking", "Photography"], "lat": 14.2333, "lng": 76.4000},
    {"id": 36, "name": "Tungabhadra Dam", "district": "Vijayanagara", "type": "Heritage", "description": "A massive dam near Hampi with beautiful gardens, a ropeway and stunning reservoir views. Perfect complement to the Hampi ruins.", "budget": "800-1200/day", "stay": "Hampi guesthouses 600-1200/night", "food": "South Indian thali, local food", "carry": "Camera, comfortable shoes, sunhat", "best_season": "October - February", "rating": 4.2, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_36.jpg", "tags": ["Heritage", "Nature", "Photography"], "lat": 15.2667, "lng": 76.3333},
    {"id": 37, "name": "Hogenakkal Falls", "district": "Chamarajanagar", "type": "Waterfalls", "description": "The Niagara of India — smoking rocks with coracle rides through narrow gorges. The Cauvery at its most dramatic.", "budget": "1000-1500/day", "stay": "Basic guesthouses 500-800/night", "food": "Fresh fish fry, local Tamil-Karnataka food", "carry": "Extra clothes for coracle ride, camera, sunscreen", "best_season": "July - November", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_37.jpg", "tags": ["Waterfalls", "Adventure", "Nature"], "lat": 12.1167, "lng": 77.7833},
    {"id": 38, "name": "Anthargange", "district": "Kolar", "type": "Adventure", "description": "Cave trekking in volcanic rock formations near Bengaluru. Night treks through caves with a sacred spring inside.", "budget": "600-1000/day", "stay": "Kolar hotels 400-700/night", "food": "Local Karnataka food", "carry": "Torch, trekking shoes, water, warm clothes at night", "best_season": "October - February", "rating": 4.3, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_38.jpg", "tags": ["Adventure", "Trekking", "Bengaluru Nearby"], "lat": 13.2167, "lng": 78.2333},
    {"id": 39, "name": "Madhugiri Fort", "district": "Tumkur", "type": "Trek", "description": "The second largest monolith in Asia. A dramatic fort climb on a massive single rock with sweeping Deccan plateau views.", "budget": "600-1000/day", "stay": "Tumkur hotels 500-800/night", "food": "Local darshini food", "carry": "Trekking shoes, water, camera, rope for steep sections", "best_season": "October - February", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_39.jpg", "tags": ["Trekking", "Heritage", "Bengaluru Nearby"], "lat": 13.6667, "lng": 77.2000},
    {"id": 40, "name": "Savandurga", "district": "Ramanagara", "type": "Trek", "description": "One of the largest monolith hills in Asia. A challenging trek up the smooth rock face with Arkavathi river views below.", "budget": "600-1000/day", "stay": "Bengaluru day trip recommended", "food": "Carry packed food", "carry": "Trekking shoes, water, rope optional, camera", "best_season": "October - February", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_40.jpg", "tags": ["Trekking", "Adventure", "Bengaluru Nearby"], "lat": 12.9167, "lng": 77.3000},
    {"id": 41, "name": "Bylakuppe", "district": "Kodagu", "type": "Unique", "description": "The largest Tibetan settlement outside Tibet. Namdroling Monastery's Golden Temple is breathtakingly beautiful.", "budget": "800-1200/day", "stay": "Monastery guesthouses 500-800/night", "food": "Tibetan momos, thukpa, butter tea", "carry": "Respectful clothing, camera", "best_season": "October - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_41.jpg", "tags": ["Unique", "Heritage", "Photography"], "lat": 12.2500, "lng": 76.1333},
    {"id": 42, "name": "Sringeri", "district": "Chikmagalur", "type": "Heritage", "description": "The first of the four sacred mathas established by Adi Shankaracharya. A serene forest temple town on the Tunga river.", "budget": "800-1200/day", "stay": "Matha guesthouses 400-800/night", "food": "Sattvic meals, South Indian food", "carry": "Respectful clothing, camera", "best_season": "October - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_42.jpg", "tags": ["Heritage", "Nature", "Unique"], "lat": 13.4167, "lng": 75.2500},
    {"id": 43, "name": "Kemmanagundi", "district": "Chikmagalur", "type": "Hills", "description": "A hidden hill station in the Western Ghats with rose gardens, waterfalls and stunning trek trails. Less known than Chikmagalur.", "budget": "1200-2000/day", "stay": "KSTDC hotel 800-1500/night", "food": "Basic meals, carry snacks", "carry": "Warm clothes, trekking shoes, camera", "best_season": "September - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_43.jpg", "tags": ["Hills", "Nature", "Trekking"], "lat": 13.5333, "lng": 75.7500},
    {"id": 44, "name": "BR Hills", "district": "Chamarajanagar", "type": "Wildlife", "description": "Where the Eastern and Western Ghats meet. Home to elephants, leopards and the indigenous Soliga tribe.", "budget": "2000-3500/day", "stay": "Forest lodges 1500-3000/night", "food": "Camp food, tribal cuisine", "carry": "Binoculars, insect repellent, camera", "best_season": "October - May", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_44.jpg", "tags": ["Wildlife", "Nature", "Unique"], "lat": 11.9667, "lng": 77.1667},
    {"id": 45, "name": "Netrani Island", "district": "Uttara Kannada", "type": "Adventure", "description": "Karnataka's only coral island — a diver's paradise with crystal clear waters and abundant marine life.", "budget": "3000-5000/day", "stay": "Murudeshwar resorts 1500-3000/night", "food": "Seafood, coastal Karnataka food", "carry": "Diving/snorkeling gear, waterproof bag, sunscreen", "best_season": "October - May", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_45.jpg", "tags": ["Adventure", "Beach", "Unique"], "lat": 14.0167, "lng": 74.3333},
    {"id": 46, "name": "Bijapur (Vijayapura)", "district": "Vijayapura", "type": "Heritage", "description": "The city of Adil Shahi kings with Gol Gumbaz — the world's second largest dome. A treasure of Indo-Islamic architecture.", "budget": "1000-1500/day", "stay": "Hotels 700-1200/night", "food": "Biryani, kebabs, North Karnataka food", "carry": "Comfortable shoes, camera, sunhat", "best_season": "October - February", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_46.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 16.8302, "lng": 75.7100},
    {"id": 47, "name": "Shravanabelagola", "district": "Hassan", "type": "Heritage", "description": "Home to the massive 18-meter Gommateshwara statue — the world's largest monolithic statue carved in 981 AD.", "budget": "800-1200/day", "stay": "Hassan hotels 600-1000/night", "food": "South Indian meals, Jain food", "carry": "Comfortable clothes (no footwear on hill), camera", "best_season": "October - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_47.jpg", "tags": ["Heritage", "Photography", "Unique"], "lat": 12.8583, "lng": 76.4836},
    {"id": 48, "name": "Marvanthe Beach", "district": "Udupi", "type": "Beach", "description": "One of India's most dramatic beaches — the sea on one side and the Souparnika river on the other with NH66 cutting through.", "budget": "1000-1500/day", "stay": "Beach resorts 800-1500/night", "food": "Seafood, Mangalorean cuisine", "carry": "Camera, sunscreen, swimwear", "best_season": "October - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_48.jpg", "tags": ["Beach", "Photography", "Unique"], "lat": 13.7167, "lng": 74.6167},
    {"id": 49, "name": "Udupi", "district": "Udupi", "type": "Heritage", "description": "Famous for the Krishna Matha temple and the birthplace of Udupi cuisine. A clean, spiritual coastal town.", "budget": "1000-1500/day", "stay": "Hotels 700-1200/night", "food": "Udupi thali, idli sambar, masala dosa", "carry": "Comfortable clothes, camera", "best_season": "October - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_49.jpg", "tags": ["Heritage", "Beach", "Unique"], "lat": 13.3409, "lng": 74.7421},
    {"id": 50, "name": "Mangaluru", "district": "Dakshina Kannada", "type": "Beach", "description": "A vibrant coastal city with beautiful beaches, historic churches, Tulu culture and the best seafood in Karnataka.", "budget": "1500-2500/day", "stay": "Hotels 1000-2000/night", "food": "Neer dosa, kori rotti, fish gassi, mangalore buns", "carry": "Light clothes, sunscreen, camera", "best_season": "October - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_50.jpg", "tags": ["Beach", "Heritage", "Unique"], "lat": 12.9141, "lng": 74.8560},
    {"id": 51, "name": "Kukke Subramanya", "district": "Dakshina Kannada", "type": "Heritage", "description": "A sacred serpent temple in the Western Ghats forest. The trek to Kumara Parvatha from here is Karnataka's toughest.", "budget": "1000-1500/day", "stay": "Temple guesthouses 500-900/night", "food": "Temple meals, South Indian food", "carry": "Trekking shoes, permit for trek, warm clothes", "best_season": "October - March", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_51.jpg", "tags": ["Heritage", "Trekking", "Nature"], "lat": 12.8333, "lng": 75.7333},
    {"id": 52, "name": "Kumara Parvatha", "district": "Dakshina Kannada", "type": "Trek", "description": "Karnataka's most challenging trek at 1712m. A two-day trek through dense forests, open grasslands and rocky ridges.", "budget": "1500-2000/day", "stay": "Forest guesthouses 600-1000/night", "food": "Packed food, basic meals at Bhattara Mane", "carry": "Permit, trekking shoes, sleeping bag, warm clothes", "best_season": "October - February", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_52.jpg", "tags": ["Trekking", "Nature", "Adventure"], "lat": 12.8667, "lng": 75.7667},
    {"id": 53, "name": "Honnemaradu", "district": "Shivamogga", "type": "Adventure", "description": "A tiny island village on the Bhadra reservoir — perfect for water sports, camping and serene backwater experiences.", "budget": "1500-2500/day", "stay": "Floating camps 1200-2000/night", "food": "Camp meals, local Malnad food", "carry": "Light clothes, swimwear, camera", "best_season": "October - March", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_53.jpg", "tags": ["Adventure", "Nature", "Unique"], "lat": 13.8500, "lng": 75.3833},
    {"id": 54, "name": "Talakaveri", "district": "Kodagu", "type": "Heritage", "description": "The sacred origin of the Cauvery river on Brahmagiri hill. A serene pilgrimage site with stunning Ghats views.", "budget": "1000-1500/day", "stay": "Madikeri homestays 800-1500/night", "food": "Coorg food, pandi curry, akki roti", "carry": "Warm clothes, comfortable shoes, camera", "best_season": "October - March", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_54.jpg", "tags": ["Heritage", "Nature", "Trekking"], "lat": 12.3833, "lng": 75.4667},
    {"id": 55, "name": "Sirsi Unchalli Falls", "district": "Uttara Kannada", "type": "Waterfalls", "description": "The hidden Lushington Falls — a 116m waterfall deep in the Sahyadri forest. One of Karnataka's most spectacular and least visited falls.", "budget": "1000-1500/day", "stay": "Sirsi hotels 600-1000/night", "food": "Malnad cuisine, fish curry, bamboo shoot dishes", "carry": "Raincoat, trekking shoes, mosquito repellent, camera", "best_season": "October - January", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_55.jpg", "tags": ["Waterfalls", "Nature", "Trekking"], "lat": 14.5167, "lng": 74.9167},
    {"id": 56, "name": "Dubare Elephant Camp", "district": "Kodagu", "type": "Wildlife", "description": "Interact with trained Karnataka forest elephants at dawn. Bath them, feed them and watch them in their natural river habitat.", "budget": "1500-2500/day", "stay": "Jungle camps 1200-2000/night", "food": "Camp food, Coorg cuisine", "carry": "Old clothes for elephant bathing, camera", "best_season": "October - May", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_56.jpg", "tags": ["Wildlife", "Unique", "Adventure"], "lat": 12.3500, "lng": 75.9667},
    {"id": 57, "name": "Talakad", "district": "Mysuru", "type": "Heritage", "description": "An ancient city buried under sand dunes on the Cauvery. Temples emerging from sand and the mysterious Panchalinga temples.", "budget": "800-1200/day", "stay": "Mysuru hotels or basic local stay", "food": "South Indian food, local meals", "carry": "Camera, comfortable clothes, water", "best_season": "October - February", "rating": 4.3, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_57.jpg", "tags": ["Heritage", "Unique", "Photography"], "lat": 12.2000, "lng": 77.0333},
    {"id": 58, "name": "Melukote", "district": "Mandya", "type": "Heritage", "description": "A sacred hilltop temple town with natural rock pools, peacocks and rare Iyengar Brahmin culture. Visited by Ramanujacharya.", "budget": "600-1000/day", "stay": "Mandya hotels 500-800/night", "food": "Iyengar meals, puliyogare, South Indian food", "carry": "Comfortable clothes, camera, water", "best_season": "October - March", "rating": 4.3, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_58.jpg", "tags": ["Heritage", "Unique", "Nature"], "lat": 12.6611, "lng": 76.6569},
    {"id": 59, "name": "Bhadra Wildlife Sanctuary", "district": "Chikmagalur", "type": "Wildlife", "description": "A pristine tiger reserve with boat safaris on the Bhadra reservoir and jeep safaris through dense deciduous forests.", "budget": "2500-4000/day", "stay": "Jungle lodges 2000-3500/night", "food": "Resort meals, camp food", "carry": "Binoculars, camera, insect repellent", "best_season": "October - May", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_59.jpg", "tags": ["Wildlife", "Nature", "Adventure"], "lat": 13.5667, "lng": 75.6333},
    {"id": 60, "name": "Skandagiri Night Trek", "district": "Chikkaballapur", "type": "Adventure", "description": "Trek through sea of clouds at midnight — one of India's most magical trek experiences. Sunrise from above the clouds.", "budget": "800-1200/day", "stay": "Bengaluru stay", "food": "Packed food, hot tea at base camp", "carry": "Torch, warm clothes, trekking shoes, water", "best_season": "October - February", "rating": 4.7, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_60.jpg", "tags": ["Adventure", "Trekking", "Bengaluru Nearby"], "lat": 13.4167, "lng": 77.7000},
    {"id": 61, "name": "Kabini Backwaters", "district": "Mysuru", "type": "Nature", "description": "Sunset boat rides on the Kabini reservoir with elephants bathing on the banks. One of India's most magical wildlife experiences.", "budget": "3000-6000/day", "stay": "Luxury tents 3000-6000/night", "food": "Gourmet jungle meals", "carry": "Camera, binoculars, light clothes", "best_season": "October - May", "rating": 4.9, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_61.jpg", "tags": ["Nature", "Wildlife", "Photography"], "lat": 11.9249, "lng": 76.3449},
    {"id": 62, "name": "Biligiri Rangana Temple", "district": "Chamarajanagar", "type": "Heritage", "description": "A hilltop temple for Lord Ranganatha at 1800m with stunning views. The hill itself is a wildlife sanctuary.", "budget": "1500-2500/day", "stay": "Forest guesthouses 1000-2000/night", "food": "Temple meals, local food", "carry": "Warm clothes, camera, comfortable shoes", "best_season": "October - March", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_62.jpg", "tags": ["Heritage", "Wildlife", "Trekking"], "lat": 11.9667, "lng": 77.1667},
    {"id": 63, "name": "Gulbarga Fort", "district": "Kalaburagi", "type": "Heritage", "description": "A historic Deccan Sultanate fort with the largest single-domed mosque in India. A hidden gem of North Karnataka.", "budget": "800-1200/day", "stay": "City hotels 600-1000/night", "food": "Hyderabadi biryani, North Karnataka food", "carry": "Camera, comfortable shoes, sunhat", "best_season": "October - February", "rating": 4.2, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_63.jpg", "tags": ["Heritage", "Unique", "Photography"], "lat": 17.3297, "lng": 76.8343},
    {"id": 64, "name": "Kodi Beach Kundapur", "district": "Udupi", "type": "Beach", "description": "Where the Sauparnika river meets the sea at a dramatic estuary. One of Karnataka's most photogenic but least visited beaches.", "budget": "800-1200/day", "stay": "Kundapur hotels 600-1000/night", "food": "Fresh seafood, Mangalorean fish curry", "carry": "Camera, sunscreen, swimwear", "best_season": "October - March", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_64.jpg", "tags": ["Beach", "Photography", "Unique"], "lat": 13.6333, "lng": 74.6833},
    {"id": 65, "name": "Channapatna", "district": "Ramanagara", "type": "Unique", "description": "The toy city of India — famous for lacquerware wooden toys with GI tag. A living craft tradition over 400 years old.", "budget": "500-800/day", "stay": "Bengaluru day trip", "food": "Local darshini food, snacks", "carry": "Camera, shopping bag for toys!", "best_season": "Year round", "rating": 4.2, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_65.jpg", "tags": ["Unique", "Bengaluru Nearby", "Heritage"], "lat": 12.6500, "lng": 77.2000},
    {"id": 66, "name": "Shivasamudra Falls", "district": "Mandya", "type": "Waterfalls", "description": "Historic site of Asia's first hydroelectric power station with spectacular twin falls on the Cauvery river.", "budget": "800-1200/day", "stay": "Mysuru day trip or local stay", "food": "Local Karnataka food", "carry": "Camera, comfortable shoes", "best_season": "August - November", "rating": 4.3, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_66.jpg", "tags": ["Waterfalls", "Heritage", "Photography"], "lat": 12.2653, "lng": 77.1575},
    {"id": 67, "name": "Avalabetta", "district": "Chikkaballapur", "type": "Trek", "description": "A flat-topped hill with a glider station and panoramic views near Bengaluru. Perfect for sunrise and a short easy trek.", "budget": "500-800/day", "stay": "Bengaluru day trip", "food": "Carry packed food", "carry": "Camera, water, light shoes", "best_season": "October - February", "rating": 4.2, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_67.jpg", "tags": ["Trekking", "Bengaluru Nearby", "Nature"], "lat": 13.6000, "lng": 77.8167},
    {"id": 68, "name": "Cauvery Fishing Camp", "district": "Mandya", "type": "Adventure", "description": "World-class mahseer fishing on the Cauvery river. A unique adventure in forest surroundings with camping under stars.", "budget": "3000-5000/day", "stay": "Fishing camps 2500-4000/night", "food": "Camp meals, fresh Cauvery fish", "carry": "Fishing gear (available), light clothes, insect repellent", "best_season": "October - March", "rating": 4.5, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_68.jpg", "tags": ["Adventure", "Nature", "Unique"], "lat": 12.2500, "lng": 77.1000},
    {"id": 69, "name": "Chikkamagaluru Coffee Trail", "district": "Chikmagalur", "type": "Unique", "description": "A guided trail through working coffee estates — learn how coffee is grown, processed and roasted in the birthplace of Indian coffee.", "budget": "2000-3000/day", "stay": "Coffee estate bungalows 1500-2500/night", "food": "Fresh coffee, estate meals, local thali", "carry": "Comfortable shoes, light clothes, camera", "best_season": "October - February", "rating": 4.6, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_69.jpg", "tags": ["Unique", "Nature", "Plantation"], "lat": 13.3153, "lng": 75.7754},
    {"id": 70, "name": "Cotigao Wildlife Sanctuary", "district": "Uttara Kannada", "type": "Wildlife", "description": "Karnataka's quiet wilderness bordering Goa with watchtowers, rare birds and peaceful forest walks away from tourist crowds.", "budget": "1500-2500/day", "stay": "Forest guesthouses 800-1500/night", "food": "Malnad cuisine, local food", "carry": "Binoculars, insect repellent, camera, trekking shoes", "best_season": "October - April", "rating": 4.4, "image": "https://res.cloudinary.com/dmk1cx5y9/image/upload/gemindia/place_70.jpg", "tags": ["Wildlife", "Nature", "Trekking"], "lat": 15.0833, "lng": 74.0833},
]


# PING ROUTE - Keeps Render server alive
@app.route("/ping")
def ping():
    return "GemIndia is alive! 🌿", 200


@app.route("/")
def home():
    community_gems = load_gems()
    extra_places = []
    for gem in community_gems:
        extra_places.append({
            "id": gem.get("id"),
            "name": gem.get("place_name", "Hidden Gem"),
            "district": gem.get("district", "Karnataka"),
            "type": gem.get("type", "Community"),
            "description": gem.get("description", ""),
            "budget": gem.get("budget", "N/A"),
            "best_season": gem.get("best_season", "N/A"),
            "rating": None,
            "image": gem.get("image") or "",
            "tags": gem.get("tags", []),
            "lat": gem.get("lat", 0),
"lng": gem.get("lng", 0),
            "stay": "",
            "food": "",
            "carry": "",
            "is_community": True,
            "submitted_by": gem.get("name", "Anonymous"),
            "tip": gem.get("tip", ""),
            "date": gem.get("date", ""),
        })
    all_places = places + extra_places
    total_gems = len(all_places)
    return render_template(
        "index.html",
        places=all_places,
        community_gems=community_gems,
        total_gems=total_gems
    )


@app.route("/place/<int:place_id>")
def place_detail(place_id):
    place = next((p for p in places if p["id"] == place_id), None)
    if not place:
        return "Place not found", 404
    experiences = [e for e in load_experiences() if e["place_id"] == place_id]
    return render_template("place.html", place=place, experiences=experiences)


@app.route("/upload", methods=["POST"])
def upload():
    name = request.form.get("name", "Anonymous")
    place_id = int(request.form.get("place_id", 0))
    story = request.form.get("story", "")
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = 'uploads/' + filename
    experience = {
        "id": str(uuid.uuid4()), "place_id": place_id, "name": name,
        "story": story, "image": image_path, "date": datetime.now().strftime("%d %b %Y")
    }
    experiences = load_experiences()
    experiences.append(experience)
    save_experiences(experiences)
    return redirect(url_for('place_detail', place_id=place_id))


@app.route("/ai-recommend", methods=["POST"])
@csrf.exempt
def ai_recommend():
    user_input = request.json.get("message", "")
    places_summary = "\n".join([f"- {p['name']} ({p['district']}): {p['type']}, Budget {p['budget']}, Best season {p['best_season']}" for p in places])
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are GemIndia AI, a travel assistant built by Fazil, a developer from Bengaluru.
If anyone asks who built you, say: I was built by Fazil, a developer from Bengaluru who loves Karnataka travel!
You know these 70 hidden gems in Karnataka:
{places_summary}
Recommend 2-3 places matching user preferences. Include place name, district, best season and budget.
Be friendly, helpful, use emojis. Keep it short."""},
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


@app.route("/community")
def community():
    gems = load_gems()
    return render_template("community.html", gems=gems)


@app.route("/submit-gem", methods=["GET"])
def submit_gem():
    return render_template("submit_gem.html")


@app.route("/submit-gem", methods=["POST"])
@csrf.exempt
def submit_gem_post():
    submitted_by = request.form.get("submitted_by", "Anonymous")
    place_name = request.form.get("name", "")
    district = request.form.get("district", "")
    place_type = request.form.get("type", "Other")
    description = request.form.get("description", "")
    budget = request.form.get("budget", "")
    best_season = request.form.get("best_season", "")
    tags_raw = request.form.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    tip = request.form.get("tip", "")
    lat = request.form.get("lat", "0")
    lng = request.form.get("lng", "0")

    image_data = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="gemindia/community",
                    transformation=[{"width": 800, "crop": "limit"}]
                )
                image_data = upload_result["secure_url"]
            except Exception as e:
                print(f"Cloudinary upload error: {e}")
                image_data = None

    gem = {
        "id": str(uuid.uuid4()),
        "name": submitted_by,
        "place_name": place_name,
        "district": district,
        "type": place_type,
        "description": description,
        "budget": budget,
        "best_season": best_season,
        "tags": tags,
        "tip": tip,
        "image": image_data,
        "lat": float(lat) if lat else 0,
        "lng": float(lng) if lng else 0,
        "date": datetime.now().strftime("%d %b %Y")
    }
    gems = load_gems()
    gems.append(gem)
    save_gems(gems)
    return redirect(url_for('submit_success'))
    name = request.form.get("name", "Anonymous")
    place_name = request.form.get("place_name", "")
    district = request.form.get("district", "")
    place_type = request.form.get("type", "Other")
    description = request.form.get("description", "")
    budget = request.form.get("budget", "")
    best_season = request.form.get("best_season", "")
    tags = request.form.getlist("tags")
    tip = request.form.get("tip", "")

    image_data = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="gemindia/community",
                    transformation=[{"width": 800, "crop": "limit"}]
                )
                image_data = upload_result["secure_url"]
            except Exception as e:
                print(f"Cloudinary upload error: {e}")
                image_data = None

    gem = {
        "id": str(uuid.uuid4()),
        "name": name,
        "place_name": place_name,
        "district": district,
        "type": place_type,
        "description": description,
        "budget": budget,
        "best_season": best_season,
        "tags": tags,
        "tip": tip,
        "image": image_data,
        "date": datetime.now().strftime("%d %b %Y")
    }
    gems = load_gems()
    gems.append(gem)
    save_gems(gems)
    return redirect(url_for('submit_success'))


@app.route("/submit-success")
def submit_success():
    return render_template("submit_success.html")


@app.route("/admin", methods=["GET", "POST"])
@csrf.exempt
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.getenv("ADMIN_PASSWORD"):
            session['admin_logged_in'] = True
            return render_template("admin.html", places=places)
        else:
            return render_template("admin_login.html", error="Invalid Password")

    if session.get('admin_logged_in'):
        return render_template("admin.html", places=places)

    return render_template("admin_login.html")

    return render_template("admin_login.html")
@check_admin_password
def admin():
    return render_template("admin.html", places=places)


@app.route("/admin/upload-image", methods=["POST"])
@check_admin_password
def admin_upload_image():
    place_id = int(request.form.get("place_id", 0))
    if 'image' not in request.files:
        return jsonify({"error": "No image"}), 400
    file = request.files['image']
    if file and file.filename and allowed_file(file.filename):
        filename = f"place_{place_id}_" + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_url = '/static/uploads/' + filename
        for p in places:
            if p["id"] == place_id:
                p["image"] = image_url
                break
        return jsonify({"success": True, "image_url": image_url, "place_id": place_id})
    return jsonify({"error": "Invalid file"}), 400


@app.route("/sitemap.xml")
def sitemap():
    urls = ['https://gemindia.onrender.com/']
    for p in places:
        urls.append(f'https://gemindia.onrender.com/place/{p["id"]}')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f'  <url><loc>{url}</loc></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')


@app.route("/debug-gems")
def debug_gems():
    try:
        res = http_requests.get(GEMS_BIN_URL + "/latest", headers={"X-Master-Key": JSONBIN_API_KEY})
        return jsonify({"status": res.status_code, "data": res.json()})
    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/googlef6ed7012786480c1.html')
def google_verify():
    return send_from_directory('.', 'googlef6ed7012786480c1.html')
@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)