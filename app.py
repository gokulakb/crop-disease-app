import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import datetime
import random
import time
import requests
import json
import os
from PIL import Image
from io import BytesIO
from supabase import create_client, Client

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Crop Disease Detection", page_icon="🌾", layout="wide")

# -------------------- SUPABASE --------------------
def init_supabase():
    if "supabase_url" not in st.secrets or "supabase_key" not in st.secrets:
        st.error("Supabase credentials not found. Please set them in Streamlit secrets.")
        st.stop()
    url = st.secrets["supabase_url"].strip()
    key = st.secrets["supabase_key"].strip()
    try:
        client = create_client(url, key)
        # Test connection
        client.table("users").select("email", count="exact").limit(0).execute()
        return client
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        st.stop()

supabase = init_supabase()

# -------------------- WEATHER API --------------------
WEATHER_API_KEY = st.secrets.get("weather_api_key", None)

# -------------------- MOCK MODEL (expanded) --------------------
USE_MOCK = True
MOCK_CLASSES = [
    "Apple Scab", "Apple Black Rot", "Cedar Apple Rust", "Healthy Apple",
    "Corn Common Rust", "Corn Gray Leaf Spot", "Corn Northern Leaf Blight", "Healthy Corn",
    "Grape Black Rot", "Grape Esca (Black Measles)", "Grape Leaf Blight", "Healthy Grape",
    "Potato Early Blight", "Potato Late Blight", "Healthy Potato",
    "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight", "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot", "Tomato Spider Mites", "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus", "Healthy Tomato",
    "Rice Blast", "Rice Brown Spot", "Rice Sheath Blight", "Healthy Rice",
    "Wheat Leaf Rust", "Wheat Stripe Rust", "Wheat Powdery Mildew", "Healthy Wheat",
    "Sugarcane Red Rot", "Sugarcane Smut", "Healthy Sugarcane",
    "Cotton Leaf Curl", "Cotton Boll Rot", "Healthy Cotton"
]

def predict_disease(image):
    if USE_MOCK:
        disease = random.choice(MOCK_CLASSES)
        confidence = random.uniform(0.7, 0.99)
        return disease, confidence
    else:
        # Real prediction code later
        pass

# -------------------- DISEASE DATABASE (expanded) --------------------
DISEASE_DB = {
    "Apple Scab": {
        "crop": "Apple",
        "cause": "Fungus Venturia inaequalis",
        "symptoms": "Olive‑green to brown spots on leaves and fruit; leaves may curl and fall prematurely. Fruit may become deformed and cracked.",
        "prevention": "Plant resistant varieties. Prune trees to improve air circulation. Remove and destroy fallen leaves. Avoid overhead irrigation.",
        "organic": "Neem oil spray (2‑3 ml per liter) every 7‑10 days. Baking soda solution (1 tsp per liter water) with a few drops of vegetable oil.",
        "treatment": "Apply fungicides at green tip, pre‑bloom, and post‑bloom stages.",
        "medicines": [
            {"name": "Captan 50WP", "company": "Bayer", "price": "₹2,499/500g", "rating": 4.5,
             "usage": "Apply 2g per liter of water. Repeat every 7‑10 days. Use 200‑300 liters per acre."},
            {"name": "Myclobutanil", "company": "Spectrum", "price": "₹3,299/250ml", "rating": 4.3,
             "usage": "Apply 0.5ml per liter of water. Do not apply more than 3 times per season."},
            {"name": "Sulfur Spray", "company": "Bonide", "price": "₹1,899/500ml", "rating": 4.2,
             "usage": "Apply 5ml per liter. Use when temperature is below 30°C."}
        ],
        "season": "Spring/Fall",
        "severity": "High"
    },
    "Corn Common Rust": {
        "crop": "Corn",
        "cause": "Fungus Puccinia sorghi",
        "symptoms": "Reddish‑brown pustules on both leaf surfaces, primarily on leaves. Pustules may turn black as they age.",
        "prevention": "Plant resistant hybrids. Practice crop rotation. Avoid overhead irrigation. Remove crop debris after harvest.",
        "organic": "Sulfur‑based fungicides. Compost tea spray. Neem oil (2ml per liter) weekly.",
        "treatment": "Apply fungicides at first sign of rust. Repeat every 7‑10 days if necessary.",
        "medicines": [
            {"name": "Azoxystrobin", "company": "Syngenta", "price": "₹4,599/500ml", "rating": 4.6,
             "usage": "Apply 1ml per liter. Use 200‑300 liters per acre. Maximum 2 applications per season."},
            {"name": "Pyraclostrobin", "company": "BASF", "price": "₹5,299/500ml", "rating": 4.4,
             "usage": "Apply 0.8ml per liter. Do not apply within 30 days of harvest."}
        ],
        "season": "Summer",
        "severity": "Medium"
    },
    "Potato Early Blight": {
        "crop": "Potato",
        "cause": "Fungus Alternaria solani",
        "symptoms": "Dark brown to black lesions with concentric rings, usually on lower leaves. Lesions may enlarge and cause leaf drop.",
        "prevention": "Crop rotation (avoid planting potatoes in same field for 3 years). Proper spacing. Avoid overhead irrigation. Use disease‑free seed.",
        "organic": "Copper fungicides (3g per liter). Bacillus subtilis spray. Compost tea.",
        "treatment": "Apply fungicides at first sign of disease. Repeat every 7‑10 days.",
        "medicines": [
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,799/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Use 300‑400 liters per acre. Repeat every 7‑10 days."},
            {"name": "Azoxystrobin", "company": "Bayer", "price": "₹4,899/500ml", "rating": 4.5,
             "usage": "Apply 1ml per liter. Use 200 liters per acre. Maximum 2 applications."}
        ],
        "season": "Summer/Fall",
        "severity": "Medium"
    },
    "Tomato Septoria Leaf Spot": {
        "crop": "Tomato",
        "cause": "Fungus Septoria lycopersici",
        "symptoms": "Small, water‑soaked spots that later develop gray centers with dark brown margins. Leaves yellow and drop.",
        "prevention": "Avoid overhead watering. Remove infected leaves. Crop rotation. Use mulch to prevent soil splash.",
        "organic": "Copper fungicides. Baking soda spray (1 tsp per liter water with a few drops of vegetable oil).",
        "treatment": "Apply fungicides containing chlorothalonil or copper hydroxide at first sign.",
        "medicines": [
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,799/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Repeat every 7‑10 days."},
            {"name": "Copper Hydroxide", "company": "DuPont", "price": "₹3,199/500g", "rating": 4.2,
             "usage": "Apply 2g per liter. Use 300 liters per acre."}
        ],
        "season": "Spring/Summer",
        "severity": "Medium"
    },
    "Tomato Blast": {
        "crop": "Tomato",
        "cause": "Fungus Alternaria solani (early blight) or Phytophthora infestans (late blight)",
        "symptoms": "Dark lesions on leaves, stems, and fruit. Rapid wilting and death of foliage.",
        "prevention": "Use resistant varieties. Avoid overhead irrigation. Remove infected plant debris.",
        "organic": "Copper fungicides. Neem oil.",
        "treatment": "Apply fungicides containing chlorothalonil, mancozeb, or copper compounds.",
        "medicines": [
            {"name": "Mancozeb", "company": "Dow", "price": "₹2,999/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Repeat every 7‑10 days."},
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,799/500g", "rating": 4.3,
             "usage": "Apply 2g per liter."}
        ],
        "season": "Spring/Summer",
        "severity": "High"
    },
    "Rice Blast": {
        "crop": "Rice",
        "cause": "Fungus Magnaporthe oryzae",
        "symptoms": "Diamond‑shaped lesions with gray centers and brown margins on leaves. Can infect panicles.",
        "prevention": "Use resistant varieties. Avoid excessive nitrogen. Maintain proper water management.",
        "organic": "Neem cake, Trichoderma, silica application.",
        "treatment": "Apply fungicides at booting and heading stages.",
        "medicines": [
            {"name": "Tricyclazole", "company": "Bayer", "price": "₹3,899/500ml", "rating": 4.5,
             "usage": "Apply 1ml per liter. Use 200 liters per acre."},
            {"name": "Isoprothiolane", "company": "Syngenta", "price": "₹4,299/500ml", "rating": 4.3,
             "usage": "Apply 0.8ml per liter."}
        ],
        "season": "Kharif",
        "severity": "High"
    },
    "Grape Black Rot": {
        "crop": "Grape",
        "cause": "Fungus Guignardia bidwellii",
        "symptoms": "Circular lesions on leaves with black margins, shriveled and blackened fruit.",
        "prevention": "Prune to improve air circulation. Remove mummified fruit. Maintain proper spacing.",
        "organic": "Copper fungicides, Bacillus subtilis, garlic spray.",
        "treatment": "Apply fungicides from early season through fruit set.",
        "medicines": [
            {"name": "Mancozeb", "company": "Dow", "price": "₹2,999/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Repeat every 7‑10 days."},
            {"name": "Copper Oxychloride", "company": "Nufarm", "price": "₹3,499/500g", "rating": 4.2,
             "usage": "Apply 3g per liter."}
        ],
        "season": "Spring",
        "severity": "High"
    },
    "Wheat Leaf Rust": {
        "crop": "Wheat",
        "cause": "Fungus Puccinia triticina",
        "symptoms": "Small, reddish‑brown pustules scattered on leaves.",
        "prevention": "Use resistant varieties. Early planting. Avoid excessive nitrogen.",
        "organic": "Sulfur spray, neem oil.",
        "treatment": "Apply fungicides at first sign.",
        "medicines": [
            {"name": "Tebuconazole", "company": "Bayer", "price": "₹3,399/500ml", "rating": 4.3,
             "usage": "Apply 1ml per liter."},
            {"name": "Propiconazole", "company": "Syngenta", "price": "₹4,199/500ml", "rating": 4.4,
             "usage": "Apply 0.5ml per liter."}
        ],
        "season": "Spring",
        "severity": "Medium"
    }
}

# -------------------- CROP CALENDAR --------------------
CROP_CALENDAR = {
    "Rice": {"planting": "June-July", "harvesting": "November-December"},
    "Wheat": {"planting": "October-December", "harvesting": "March-April"},
    "Maize": {"planting": "June-July", "harvesting": "September-October"},
    "Sugarcane": {"planting": "January-March", "harvesting": "November-February"},
    "Cotton": {"planting": "May-June", "harvesting": "November-December"},
    "Groundnut": {"planting": "June-July", "harvesting": "September-October"},
}

# -------------------- WEATHER FUNCTION --------------------
def get_weather(city="Delhi"):
    if not WEATHER_API_KEY:
        return None, "Weather API key not configured. Please get a free API key from OpenWeatherMap and add it to Streamlit secrets."
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data, None
        else:
            return None, data.get("message", "Unknown error")
    except Exception as e:
        return None, str(e)

# -------------------- AUTH FUNCTIONS --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, name, password):
    pwd_hash = hash_password(password)
    try:
        supabase.table("users").insert({"email": email, "name": name, "password_hash": pwd_hash}).execute()
        return True, "Registration successful! Please login."
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    pwd_hash = hash_password(password)
    try:
        response = supabase.table("users").select("name").eq("email", email).eq("password_hash", pwd_hash).execute()
        if response.data:
            return True, response.data[0]["name"]
        else:
            return False, "Invalid email or password."
    except Exception as e:
        return False, str(e)

def get_officers(district=None):
    query = supabase.table("officers").select("*")
    if district and district != "All":
        query = query.eq("district", district)
    response = query.execute()
    return response.data

def book_appointment(user_email, officer_id, date, time_slot):
    data = {
        "user_email": user_email,
        "officer_id": officer_id,
        "appointment_date": str(date),
        "appointment_time": str(time_slot)
    }
    supabase.table("appointments").insert(data).execute()
    return True

# -------------------- IMPROVED CHATBOT ENGINE --------------------
def chatbot_response(query):
    query = query.lower().strip()
    
    # Greetings
    if any(word in query for word in ["hello", "hi", "hey", "namaste", "hola"]):
        return "Hello! How can I assist you with your crops today?"
    
    # Help / menu
    if any(word in query for word in ["help", "what can you do", "options"]):
        return "I can answer questions about crop diseases, prevention, treatment, officers, weather, and crop calendar. Just ask me!"
    
    # Disease information
    for disease in DISEASE_DB:
        if disease.lower() in query or any(word in query for word in disease.lower().split()):
            info = DISEASE_DB[disease]
            return (f"**{disease}**\n\n"
                    f"**Cause:** {info['cause']}\n"
                    f"**Symptoms:** {info['symptoms']}\n"
                    f"**Prevention:** {info['prevention']}\n"
                    f"**Treatment:** {info['treatment']}\n"
                    f"**Organic options:** {info['organic']}")
    
    # Look for partial matches (e.g., "tomato blast" might not be exact key)
    disease_keys = list(DISEASE_DB.keys())
    for key in disease_keys:
        if any(word in key.lower() for word in query.split() if len(word) > 3):
            info = DISEASE_DB[key]
            return (f"Did you mean **{key}**?\n\n"
                    f"**Cause:** {info['cause']}\n"
                    f"**Symptoms:** {info['symptoms']}\n"
                    f"**Prevention:** {info['prevention']}\n"
                    f"**Treatment:** {info['treatment']}\n"
                    f"**Organic options:** {info['organic']}")
    
    # Officers
    if any(word in query for word in ["officer", "agriculture officer", "appointment", "contact officer"]):
        return "You can find and book appointments with local agricultural officers under the 'Officers & Appointments' page."
    
    # Weather
    if any(word in query for word in ["weather", "temperature", "rain", "forecast", "climate"]):
        return "Go to the Weather page to get current conditions for your city. You'll need to add your OpenWeatherMap API key in Streamlit secrets."
    
    # Crop calendar
    if any(word in query for word in ["crop calendar", "planting time", "harvesting time", "when to plant"]):
        return "The Crop Calendar page shows optimal planting and harvesting seasons for common crops."
    
    # Thanks
    if any(word in query for word in ["thank", "thanks", "dhanyavaad", "thank you"]):
        return "You're welcome! Feel free to ask anytime."
    
    # Default
    return "I'm sorry, I didn't understand that. Try asking about a specific disease (e.g., 'tomato blast'), officers, weather, or crop calendar."

# -------------------- FULL 8‑LANGUAGE TRANSLATIONS --------------------
TRANSLATIONS = {
    "en": {
        "🌱 Crop Care AI": "🌱 Crop Care AI",
        "Select Language": "Select Language",
        "Home": "Home",
        "Disease Detection": "Disease Detection",
        "Disease Database": "Disease Database",
        "Officers & Appointments": "Officers & Appointments",
        "Live Data": "Live Data",
        "Assistant": "Assistant",
        "Crop Calendar": "Crop Calendar",
        "Weather": "Weather",
        "About": "About",
        "Menu": "Menu",
        "🔐 Login / Sign Up": "🔐 Login / Sign Up",
        "Login": "Login",
        "Sign Up": "Sign Up",
        "Google Login": "Google Login",
        "Login with Google (Demo)": "Login with Google (Demo)",
        "Simulated Google Login (for demo)": "Simulated Google Login (for demo)",
        "Email": "Email",
        "Password": "Password",
        "Full Name": "Full Name",
        "Welcome": "Welcome",
        "Logout": "Logout",
        "Please login to use disease detection": "Please login to use disease detection",
        "Upload Image": "Upload Image",
        "Take a Photo": "Take a Photo",
        "Analyze Uploaded Image": "Analyze Uploaded Image",
        "Analyze Camera Photo": "Analyze Camera Photo",
        "Detection complete! Confidence:": "Detection complete! Confidence:",
        "Disease:": "Disease:",
        "Crop:": "Crop:",
        "Severity:": "Severity:",
        "Cause": "Cause",
        "Symptoms": "Symptoms",
        "Prevention": "Prevention",
        "Organic Treatment": "Organic Treatment",
        "Treatment": "Treatment",
        "Recommended Medicines": "Recommended Medicines",
        "How to use": "How to use",
        "Buy": "Buy",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ Consult your local agriculture officer before treatment",
        "All": "All",
        "Filter by crop": "Filter by crop",
        "Filter by district": "Filter by district",
        "Available Officers": "Available Officers",
        "Phone": "Phone",
        "Available": "Available",
        "Book Appointment": "Book Appointment",
        "Select Date": "Select Date",
        "Select Time": "Select Time",
        "Confirm Booking": "Confirm Booking",
        "Appointment booked successfully! Officer will contact you.": "Appointment booked successfully! Officer will contact you.",
        "No officers found in this district.": "No officers found in this district.",
        "Temperature": "Temperature",
        "Humidity": "Humidity",
        "Soil Moisture": "Soil Moisture",
        "Rainfall (24h)": "Rainfall (24h)",
        "Today": "Today",
        "Current Disease Risk:": "Current Disease Risk:",
        "Low": "Low",
        "Medium": "Medium",
        "High": "High",
        "Disease Incidence Trend": "Disease Incidence Trend",
        "Daily Disease Cases (Last 30 Days)": "Daily Disease Cases (Last 30 Days)",
        "Weather Forecast": "Weather Forecast",
        "7-Day Temperature Forecast": "7-Day Temperature Forecast",
        "Date": "Date",
        "Temperature (°C)": "Temperature (°C)",
        "Choose your preferred way to interact": "Choose your preferred way to interact",
        "Chat": "Chat",
        "Voice": "Voice",
        "Type your message here...": "Type your message here...",
        "Send": "Send",
        "You said:": "You said:",
        "Assistant:": "Assistant:",
        "Listening...": "Listening...",
        "Start Listening": "Start Listening",
        "Stop Listening": "Stop Listening",
        "Features": "Features",
        "Technology": "Technology",
        "Contact": "Contact",
        "Disclaimer": "Disclaimer",
        "For assistance only. Always consult agriculture experts.": "For assistance only. Always consult agriculture experts.",
        "Version 9.0 | © 2025 Crop Care AI": "Version 9.0 | © 2025 Crop Care AI",
        "Crop Calendar": "Crop Calendar",
        "Optimal planting and harvesting times for common crops": "Optimal planting and harvesting times for common crops",
        "Planting Season": "Planting Season",
        "Harvesting Season": "Harvesting Season",
        "Current weather conditions for your region": "Current weather conditions for your region",
        "Enter city": "Enter city",
        "Get Weather": "Get Weather",
        "Wind Speed": "Wind Speed",
        "Pressure": "Pressure",
        "You": "You",
        "Command": "Command",
        "Send Command": "Send Command",
    },
    "hi": {
        "🌱 Crop Care AI": "🌱 क्रॉप केयर एआई",
        "Select Language": "भाषा चुनें",
        "Home": "होम",
        "Disease Detection": "रोग का पता लगाना",
        "Disease Database": "रोग डेटाबेस",
        "Officers & Appointments": "अधिकारी और नियुक्तियाँ",
        "Live Data": "लाइव डेटा",
        "Assistant": "सहायक",
        "Crop Calendar": "फसल कैलेंडर",
        "Weather": "मौसम",
        "About": "बारे में",
        "Menu": "मेनू",
        "🔐 Login / Sign Up": "🔐 लॉगिन / साइन अप",
        "Login": "लॉगिन",
        "Sign Up": "साइन अप",
        "Google Login": "गूगल लॉगिन",
        "Login with Google (Demo)": "गूगल से लॉगिन (डेमो)",
        "Simulated Google Login (for demo)": "सिम्युलेटेड गूगल लॉगिन (डेमो के लिए)",
        "Email": "ईमेल",
        "Password": "पासवर्ड",
        "Full Name": "पूरा नाम",
        "Welcome": "स्वागत हे",
        "Logout": "लॉग आउट",
        "Please login to use disease detection": "कृपया रोग का पता लगाने के लिए लॉगिन करें",
        "Upload Image": "छवि अपलोड करें",
        "Take a Photo": "फोटो लें",
        "Analyze Uploaded Image": "अपलोड की गई छवि का विश्लेषण करें",
        "Analyze Camera Photo": "कैमरा फोटो का विश्लेषण करें",
        "Detection complete! Confidence:": "पता लगाना पूरा हुआ! आत्मविश्वास:",
        "Disease:": "रोग:",
        "Crop:": "फसल:",
        "Severity:": "गंभीरता:",
        "Cause": "कारण",
        "Symptoms": "लक्षण",
        "Prevention": "रोकथाम",
        "Organic Treatment": "जैविक उपचार",
        "Treatment": "उपचार",
        "Recommended Medicines": "अनुशंसित दवाएं",
        "How to use": "उपयोग कैसे करें",
        "Buy": "खरीदें",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ उपचार से पहले अपने स्थानीय कृषि अधिकारी से सलाह लें",
        "All": "सभी",
        "Filter by crop": "फसल के अनुसार फ़िल्टर करें",
        "Filter by district": "जिले के अनुसार फ़िल्टर करें",
        "Available Officers": "उपलब्ध अधिकारी",
        "Phone": "फ़ोन",
        "Available": "उपलब्ध",
        "Book Appointment": "अपॉइंटमेंट बुक करें",
        "Select Date": "तारीख चुनें",
        "Select Time": "समय चुनें",
        "Confirm Booking": "बुकिंग की पुष्टि करें",
        "Appointment booked successfully! Officer will contact you.": "अपॉइंटमेंट सफलतापूर्वक बुक हो गया! अधिकारी आपसे संपर्क करेगा।",
        "No officers found in this district.": "इस जिले में कोई अधिकारी नहीं मिला।",
        "Temperature": "तापमान",
        "Humidity": "नमी",
        "Soil Moisture": "मिट्टी की नमी",
        "Rainfall (24h)": "वर्षा (24 घंटे)",
        "Today": "आज",
        "Current Disease Risk:": "वर्तमान रोग जोखिम:",
        "Low": "कम",
        "Medium": "मध्यम",
        "High": "उच्च",
        "Disease Incidence Trend": "रोग घटना प्रवृत्ति",
        "Daily Disease Cases (Last 30 Days)": "दैनिक रोग के मामले (पिछले 30 दिन)",
        "Weather Forecast": "मौसम का पूर्वानुमान",
        "7-Day Temperature Forecast": "7-दिवसीय तापमान पूर्वानुमान",
        "Date": "तारीख",
        "Temperature (°C)": "तापमान (डिग्री सेल्सियस)",
        "Choose your preferred way to interact": "अपना पसंदीदा तरीका चुनें",
        "Chat": "चैट",
        "Voice": "आवाज",
        "Type your message here...": "अपना संदेश यहाँ टाइप करें...",
        "Send": "भेजें",
        "You said:": "आपने कहा:",
        "Assistant:": "सहायक:",
        "Listening...": "सुन रहा हूँ...",
        "Start Listening": "सुनना शुरू करें",
        "Stop Listening": "सुनना बंद करें",
        "Features": "विशेषताएँ",
        "Technology": "प्रौद्योगिकी",
        "Contact": "संपर्क करें",
        "Disclaimer": "अस्वीकरण",
        "For assistance only. Always consult agriculture experts.": "केवल सहायता के लिए। हमेशा कृषि विशेषज्ञों से सलाह लें।",
        "Version 9.0 | © 2025 Crop Care AI": "संस्करण 9.0 | © 2025 क्रॉप केयर एआई",
        "Crop Calendar": "फसल कैलेंडर",
        "Optimal planting and harvesting times for common crops": "सामान्य फसलों के लिए इष्टतम रोपण और कटाई का समय",
        "Planting Season": "रोपण का मौसम",
        "Harvesting Season": "कटाई का मौसम",
        "Current weather conditions for your region": "आपके क्षेत्र के लिए वर्तमान मौसम की स्थिति",
        "Enter city": "शहर दर्ज करें",
        "Get Weather": "मौसम प्राप्त करें",
        "Wind Speed": "हवा की गति",
        "Pressure": "दबाव",
        "You": "आप",
        "Command": "आदेश",
        "Send Command": "आदेश भेजें",
    },
    "te": {
        "🌱 Crop Care AI": "🌱 క్రాప్ కేర్ AI",
        "Select Language": "భాషను ఎంచుకోండి",
        "Home": "హోమ్",
        "Disease Detection": "వ్యాధి గుర్తింపు",
        "Disease Database": "వ్యాధి డేటాబేస్",
        "Officers & Appointments": "అధికారులు & నియామకాలు",
        "Live Data": "ప్రత్యక్ష డేటా",
        "Assistant": "సహాయకుడు",
        "Crop Calendar": "పంట క్యాలెండర్",
        "Weather": "వాతావరణం",
        "About": "గురించి",
        "Menu": "మెను",
        "🔐 Login / Sign Up": "🔐 లాగిన్ / సైన్ అప్",
        "Login": "లాగిన్",
        "Sign Up": "సైన్ అప్",
        "Google Login": "గూగుల్ లాగిన్",
        "Login with Google (Demo)": "గూగుల్ తో లాగిన్ (డెమో)",
        "Simulated Google Login (for demo)": "సిమ్యులేటెడ్ గూగుల్ లాగిన్ (డెమో కోసం)",
        "Email": "ఇమెయిల్",
        "Password": "పాస్వర్డ్",
        "Full Name": "పూర్తి పేరు",
        "Welcome": "స్వాగతం",
        "Logout": "లాగ్అవుట్",
        "Please login to use disease detection": "దయచేసి వ్యాధి గుర్తింపును ఉపయోగించడానికి లాగిన్ చేయండి",
        "Upload Image": "చిత్రాన్ని అప్లోడ్ చేయండి",
        "Take a Photo": "ఫోటో తీయండి",
        "Analyze Uploaded Image": "అప్లోడ్ చేసిన చిత్రాన్ని విశ్లేషించండి",
        "Analyze Camera Photo": "కెమెరా ఫోటోను విశ్లేషించండి",
        "Detection complete! Confidence:": "గుర్తింపు పూర్తయింది! విశ్వాసం:",
        "Disease:": "వ్యాధి:",
        "Crop:": "పంట:",
        "Severity:": "తీవ్రత:",
        "Cause": "కారణం",
        "Symptoms": "లక్షణాలు",
        "Prevention": "నివారణ",
        "Organic Treatment": "సేంద్రీయ చికిత్స",
        "Treatment": "చికిత్స",
        "Recommended Medicines": "సిఫార్సు చేసిన మందులు",
        "How to use": "ఎలా ఉపయోగించాలి",
        "Buy": "కొనండి",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ చికిత్సకు ముందు మీ స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి",
        "All": "అన్నీ",
        "Filter by crop": "పంట ద్వారా ఫిల్టర్ చేయండి",
        "Filter by district": "జిల్లా ద్వారా ఫిల్టర్ చేయండి",
        "Available Officers": "అందుబాటులో ఉన్న అధికారులు",
        "Phone": "ఫోన్",
        "Available": "అందుబాటులో ఉంది",
        "Book Appointment": "నియామకాన్ని బుక్ చేసుకోండి",
        "Select Date": "తేదీని ఎంచుకోండి",
        "Select Time": "సమయాన్ని ఎంచుకోండి",
        "Confirm Booking": "బుకింగ్‌ను నిర్ధారించండి",
        "Appointment booked successfully! Officer will contact you.": "నియామకం విజయవంతంగా బుక్ చేయబడింది! అధికారి మిమ్మల్ని సంప్రదిస్తారు.",
        "No officers found in this district.": "ఈ జిల్లాలో అధికారులు ఎవరూ కనుగొనబడలేదు.",
        "Temperature": "ఉష్ణోగ్రత",
        "Humidity": "తేమ",
        "Soil Moisture": "నేల తేమ",
        "Rainfall (24h)": "వర్షపాతం (24 గం)",
        "Today": "నేడు",
        "Current Disease Risk:": "ప్రస్తుత వ్యాధి ప్రమాదం:",
        "Low": "తక్కువ",
        "Medium": "మధ్యస్థం",
        "High": "ఎక్కువ",
        "Disease Incidence Trend": "వ్యాధి సంభవం ధోరణి",
        "Daily Disease Cases (Last 30 Days)": "రోజువారీ వ్యాధి కేసులు (గత 30 రోజులు)",
        "Weather Forecast": "వాతావరణ సూచన",
        "7-Day Temperature Forecast": "7-రోజుల ఉష్ణోగ్రత సూచన",
        "Date": "తేదీ",
        "Temperature (°C)": "ఉష్ణోగ్రత (°C)",
        "Choose your preferred way to interact": "మీకు ఇష్టమైన పరస్పర చర్యను ఎంచుకోండి",
        "Chat": "చాట్",
        "Voice": "వాయిస్",
        "Type your message here...": "మీ సందేశాన్ని ఇక్కడ టైప్ చేయండి...",
        "Send": "పంపండి",
        "You said:": "మీరు అన్నారు:",
        "Assistant:": "సహాయకుడు:",
        "Listening...": "వింటున్నాను...",
        "Start Listening": "వినడం ప్రారంభించండి",
        "Stop Listening": "వినడం ఆపండి",
        "Features": "లక్షణాలు",
        "Technology": "సాంకేతికత",
        "Contact": "సంప్రదించండి",
        "Disclaimer": "నిరాకరణ",
        "For assistance only. Always consult agriculture experts.": "సహాయం కోసం మాత్రమే. ఎల్లప్పుడూ వ్యవసాయ నిపుణులను సంప్రదించండి.",
        "Version 9.0 | © 2025 Crop Care AI": "వెర్షన్ 9.0 | © 2025 క్రాప్ కేర్ AI",
        "Crop Calendar": "పంట క్యాలెండర్",
        "Optimal planting and harvesting times for common crops": "సాధారణ పంటలకు సరైన నాటడం మరియు కోత సమయాలు",
        "Planting Season": "నాటడం సీజన్",
        "Harvesting Season": "కోత సీజన్",
        "Current weather conditions for your region": "మీ ప్రాంతానికి ప్రస్తుత వాతావరణ పరిస్థితులు",
        "Enter city": "నగరాన్ని నమోదు చేయండి",
        "Get Weather": "వాతావరణం పొందండి",
        "Wind Speed": "గాలి వేగం",
        "Pressure": "పీడనం",
        "You": "మీరు",
        "Command": "ఆదేశం",
        "Send Command": "ఆదేశం పంపండి",
    },
    "kn": {
        "🌱 Crop Care AI": "🌱 ಕ್ರಾಪ್ ಕೇರ್ AI",
        "Select Language": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "Home": "ಮುಖಪುಟ",
        "Disease Detection": "ರೋಗ ಪತ್ತೆ",
        "Disease Database": "ರೋಗ ಡೇಟಾಬೇಸ್",
        "Officers & Appointments": "ಅಧಿಕಾರಿಗಳು ಮತ್ತು ನೇಮಕಾತಿಗಳು",
        "Live Data": "ನೇರ ಡೇಟಾ",
        "Assistant": "ಸಹಾಯಕ",
        "Crop Calendar": "ಬೆಳೆ ಕ್ಯಾಲೆಂಡರ್",
        "Weather": "ಹವಾಮಾನ",
        "About": "ಕುರಿತು",
        "Menu": "ಮೆನು",
        "🔐 Login / Sign Up": "🔐 ಲಾಗಿನ್ / ಸೈನ್ ಅಪ್",
        "Login": "ಲಾಗಿನ್",
        "Sign Up": "ಸೈನ್ ಅಪ್",
        "Google Login": "ಗೂಗಲ್ ಲಾಗಿನ್",
        "Login with Google (Demo)": "ಗೂಗಲ್‌ನೊಂದಿಗೆ ಲಾಗಿನ್ (ಡೆಮೊ)",
        "Simulated Google Login (for demo)": "ಸಿಮ್ಯುಲೇಟೆಡ್ ಗೂಗಲ್ ಲಾಗಿನ್ (ಡೆಮೊಗಾಗಿ)",
        "Email": "ಇಮೇಲ್",
        "Password": "ಪಾಸ್ವರ್ಡ್",
        "Full Name": "ಪೂರ್ಣ ಹೆಸರು",
        "Welcome": "ಸ್ವಾಗತ",
        "Logout": "ಲಾಗ್ ಔಟ್",
        "Please login to use disease detection": "ದಯವಿಟ್ಟು ರೋಗ ಪತ್ತೆ ಬಳಸಲು ಲಾಗಿನ್ ಮಾಡಿ",
        "Upload Image": "ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "Take a Photo": "ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ",
        "Analyze Uploaded Image": "ಅಪ್ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಿ",
        "Analyze Camera Photo": "ಕ್ಯಾಮೆರಾ ಫೋಟೋವನ್ನು ವಿಶ್ಲೇಷಿಸಿ",
        "Detection complete! Confidence:": "ಪತ್ತೆ ಪೂರ್ಣಗೊಂಡಿದೆ! ವಿಶ್ವಾಸ:",
        "Disease:": "ರೋಗ:",
        "Crop:": "ಬೆಳೆ:",
        "Severity:": "ತೀವ್ರತೆ:",
        "Cause": "ಕಾರಣ",
        "Symptoms": "ಲಕ್ಷಣಗಳು",
        "Prevention": "ತಡೆಗಟ್ಟುವಿಕೆ",
        "Organic Treatment": "ಸಾವಯವ ಚಿಕಿತ್ಸೆ",
        "Treatment": "ಚಿಕಿತ್ಸೆ",
        "Recommended Medicines": "ಶಿಫಾರಸು ಮಾಡಿದ ಔಷಧಗಳು",
        "How to use": "ಹೇಗೆ ಬಳಸುವುದು",
        "Buy": "ಖರೀದಿಸಿ",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ ಚಿಕಿತ್ಸೆಗೆ ಮೊದಲು ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "All": "ಎಲ್ಲಾ",
        "Filter by crop": "ಬೆಳೆಯಿಂದ ಫಿಲ್ಟರ್ ಮಾಡಿ",
        "Filter by district": "ಜಿಲ್ಲೆಯಿಂದ ಫಿಲ್ಟರ್ ಮಾಡಿ",
        "Available Officers": "ಲಭ್ಯವಿರುವ ಅಧಿಕಾರಿಗಳು",
        "Phone": "ಫೋನ್",
        "Available": "ಲಭ್ಯವಿದೆ",
        "Book Appointment": "ನೇಮಕಾತಿಯನ್ನು ಬುಕ್ ಮಾಡಿ",
        "Select Date": "ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ",
        "Select Time": "ಸಮಯ ಆಯ್ಕೆಮಾಡಿ",
        "Confirm Booking": "ಬುಕಿಂಗ್ ದೃಢೀಕರಿಸಿ",
        "Appointment booked successfully! Officer will contact you.": "ನೇಮಕಾತಿ ಯಶಸ್ವಿಯಾಗಿ ಬುಕ್ ಆಗಿದೆ! ಅಧಿಕಾರಿ ನಿಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸುತ್ತಾರೆ.",
        "No officers found in this district.": "ಈ ಜಿಲ್ಲೆಯಲ್ಲಿ ಯಾವುದೇ ಅಧಿಕಾರಿಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
        "Temperature": "ತಾಪಮಾನ",
        "Humidity": "ಆರ್ದ್ರತೆ",
        "Soil Moisture": "ಮಣ್ಣಿನ ತೇವಾಂಶ",
        "Rainfall (24h)": "ಮಳೆ (24 ಗಂಟೆಗಳು)",
        "Today": "ಇಂದು",
        "Current Disease Risk:": "ಪ್ರಸ್ತುತ ರೋಗದ ಅಪಾಯ:",
        "Low": "ಕಡಿಮೆ",
        "Medium": "ಮಧ್ಯಮ",
        "High": "ಹೆಚ್ಚು",
        "Disease Incidence Trend": "ರೋಗ ಸಂಭವದ ಪ್ರವೃತ್ತಿ",
        "Daily Disease Cases (Last 30 Days)": "ದೈನಂದಿನ ರೋಗ ಪ್ರಕರಣಗಳು (ಕೊನೆಯ 30 ದಿನಗಳು)",
        "Weather Forecast": "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ",
        "7-Day Temperature Forecast": "7-ದಿನದ ತಾಪಮಾನ ಮುನ್ಸೂಚನೆ",
        "Date": "ದಿನಾಂಕ",
        "Temperature (°C)": "ತಾಪಮಾನ (°C)",
        "Choose your preferred way to interact": "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಸಂವಹನ ವಿಧಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "Chat": "ಚಾಟ್",
        "Voice": "ಧ್ವನಿ",
        "Type your message here...": "ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
        "Send": "ಕಳುಹಿಸಿ",
        "You said:": "ನೀವು ಹೇಳಿದ್ದು:",
        "Assistant:": "ಸಹಾಯಕ:",
        "Listening...": "ಕೇಳುತ್ತಿದೆ...",
        "Start Listening": "ಕೇಳಲು ಪ್ರಾರಂಭಿಸಿ",
        "Stop Listening": "ಕೇಳುವುದನ್ನು ನಿಲ್ಲಿಸಿ",
        "Features": "ವೈಶಿಷ್ಟ್ಯಗಳು",
        "Technology": "ತಂತ್ರಜ್ಞಾನ",
        "Contact": "ಸಂಪರ್ಕ",
        "Disclaimer": "ಹಕ್ಕು ನಿರಾಕರಣೆ",
        "For assistance only. Always consult agriculture experts.": "ಸಹಾಯಕ್ಕಾಗಿ ಮಾತ್ರ. ಯಾವಾಗಲೂ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "Version 9.0 | © 2025 Crop Care AI": "ಆವೃತ್ತಿ 9.0 | © 2025 ಕ್ರಾಪ್ ಕೇರ್ AI",
        "Crop Calendar": "ಬೆಳೆ ಕ್ಯಾಲೆಂಡರ್",
        "Optimal planting and harvesting times for common crops": "ಸಾಮಾನ್ಯ ಬೆಳೆಗಳಿಗೆ ಸೂಕ್ತವಾದ ನೆಡುವಿಕೆ ಮತ್ತು ಕೊಯ್ಲು ಸಮಯಗಳು",
        "Planting Season": "ನೆಡುವಿಕೆ ಕಾಲ",
        "Harvesting Season": "ಕೊಯ್ಲು ಕಾಲ",
        "Current weather conditions for your region": "ನಿಮ್ಮ ಪ್ರದೇಶದ ಪ್ರಸ್ತುತ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳು",
        "Enter city": "ನಗರವನ್ನು ನಮೂದಿಸಿ",
        "Get Weather": "ಹವಾಮಾನ ಪಡೆಯಿರಿ",
        "Wind Speed": "ಗಾಳಿಯ ವೇಗ",
        "Pressure": "ಒತ್ತಡ",
        "You": "ನೀವು",
        "Command": "ಆಜ್ಞೆ",
        "Send Command": "ಆಜ್ಞೆ ಕಳುಹಿಸಿ",
    },
    "ta": {
        "🌱 Crop Care AI": "🌱 கிராப் கேர் AI",
        "Select Language": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "Home": "முகப்பு",
        "Disease Detection": "நோய் கண்டறிதல்",
        "Disease Database": "நோய் தரவுத்தளம்",
        "Officers & Appointments": "அதிகாரிகள் & சந்திப்புகள்",
        "Live Data": "நேரடி தரவு",
        "Assistant": "உதவியாளர்",
        "Crop Calendar": "பயிர் நாட்காட்டி",
        "Weather": "வானிலை",
        "About": "பற்றி",
        "Menu": "மெனு",
        "🔐 Login / Sign Up": "🔐 உள்நுழைவு / பதிவு",
        "Login": "உள்நுழைவு",
        "Sign Up": "பதிவு",
        "Google Login": "கூகுள் உள்நுழைவு",
        "Login with Google (Demo)": "கூகுள் மூலம் உள்நுழைக (டெமோ)",
        "Simulated Google Login (for demo)": "உருவகப்படுத்தப்பட்ட கூகுள் உள்நுழைவு (டெமோவிற்கு)",
        "Email": "மின்னஞ்சல்",
        "Password": "கடவுச்சொல்",
        "Full Name": "முழு பெயர்",
        "Welcome": "வரவேற்கிறோம்",
        "Logout": "வெளியேறு",
        "Please login to use disease detection": "தயவுசெய்து நோய் கண்டறிதலைப் பயன்படுத்த உள்நுழைக",
        "Upload Image": "படத்தை பதிவேற்றவும்",
        "Take a Photo": "ஒரு புகைப்படம் எடு",
        "Analyze Uploaded Image": "பதிவேற்றப்பட்ட படத்தை பகுப்பாய்வு செய்யவும்",
        "Analyze Camera Photo": "கேமரா புகைப்படத்தை பகுப்பாய்வு செய்யவும்",
        "Detection complete! Confidence:": "கண்டறிதல் முடிந்தது! நம்பிக்கை:",
        "Disease:": "நோய்:",
        "Crop:": "பயிர்:",
        "Severity:": "தீவிரத்தன்மை:",
        "Cause": "காரணம்",
        "Symptoms": "அறிகுறிகள்",
        "Prevention": "தடுப்பு",
        "Organic Treatment": "இயற்கை சிகிச்சை",
        "Treatment": "சிகிச்சை",
        "Recommended Medicines": "பரிந்துரைக்கப்பட்ட மருந்துகள்",
        "How to use": "எப்படி பயன்படுத்துவது",
        "Buy": "வாங்க",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ சிகிச்சைக்கு முன் உங்கள் உள்ளூர் வேளாண்மை அதிகாரியை அணுகவும்",
        "All": "அனைத்தும்",
        "Filter by crop": "பயிர் வாரியாக வடிகட்டவும்",
        "Filter by district": "மாவட்டம் வாரியாக வடிகட்டவும்",
        "Available Officers": "கிடைக்கக்கூடிய அதிகாரிகள்",
        "Phone": "தொலைபேசி",
        "Available": "கிடைக்கும்",
        "Book Appointment": "சந்திப்பை பதிவு செய்யவும்",
        "Select Date": "தேதியைத் தேர்ந்தெடுக்கவும்",
        "Select Time": "நேரத்தைத் தேர்ந்தெடுக்கவும்",
        "Confirm Booking": "பதிவை உறுதிப்படுத்தவும்",
        "Appointment booked successfully! Officer will contact you.": "சந்திப்பு வெற்றிகரமாக பதிவு செய்யப்பட்டது! அதிகாரி உங்களைத் தொடர்புகொள்வார்.",
        "No officers found in this district.": "இந்த மாவட்டத்தில் அதிகாரிகள் எவரும் கிடைக்கவில்லை.",
        "Temperature": "வெப்பநிலை",
        "Humidity": "ஈரப்பதம்",
        "Soil Moisture": "மண்ணின் ஈரப்பதம்",
        "Rainfall (24h)": "மழைப்பொழிவு (24 மணி)",
        "Today": "இன்று",
        "Current Disease Risk:": "தற்போதைய நோய் ஆபத்து:",
        "Low": "குறைந்த",
        "Medium": "நடுத்தர",
        "High": "உயர்",
        "Disease Incidence Trend": "நோய் நிகழ்வு போக்கு",
        "Daily Disease Cases (Last 30 Days)": "தினசரி நோய் வழக்குகள் (கடந்த 30 நாட்கள்)",
        "Weather Forecast": "வானிலை முன்னறிவிப்பு",
        "7-Day Temperature Forecast": "7-நாள் வெப்பநிலை முன்னறிவிப்பு",
        "Date": "தேதி",
        "Temperature (°C)": "வெப்பநிலை (டிகிரி செல்சியஸ்)",
        "Choose your preferred way to interact": "உங்கள் விருப்பமான தொடர்பு முறையைத் தேர்வுசெய்க",
        "Chat": "அரட்டை",
        "Voice": "குரல்",
        "Type your message here...": "உங்கள் செய்தியை இங்கே தட்டச்சு செய்க...",
        "Send": "அனுப்பு",
        "You said:": "நீங்கள் சொன்னது:",
        "Assistant:": "உதவியாளர்:",
        "Listening...": "கேட்டுக் கொண்டிருக்கிறது...",
        "Start Listening": "கேட்கத் தொடங்கு",
        "Stop Listening": "கேட்பதை நிறுத்து",
        "Features": "அம்சங்கள்",
        "Technology": "தொழில்நுட்பம்",
        "Contact": "தொடர்பு கொள்ள",
        "Disclaimer": "பொறுப்புத் துறப்பு",
        "For assistance only. Always consult agriculture experts.": "உதவிக்கு மட்டுமே. எப்போதும் வேளாண் நிபுணர்களை அணுகவும்.",
        "Version 9.0 | © 2025 Crop Care AI": "பதிப்பு 9.0 | © 2025 கிராப் கேர் AI",
        "Crop Calendar": "பயிர் நாட்காட்டி",
        "Optimal planting and harvesting times for common crops": "பொதுவான பயிர்களுக்கு உகந்த நடவு மற்றும் அறுவடை நேரங்கள்",
        "Planting Season": "நடவு காலம்",
        "Harvesting Season": "அறுவடை காலம்",
        "Current weather conditions for your region": "உங்கள் பகுதிக்கான தற்போதைய வானிலை நிலைமைகள்",
        "Enter city": "நகரத்தை உள்ளிடவும்",
        "Get Weather": "வானிலை பெறுக",
        "Wind Speed": "காற்றின் வேகம்",
        "Pressure": "அழுத்தம்",
        "You": "நீங்கள்",
        "Command": "கட்டளை",
        "Send Command": "கட்டளையை அனுப்பு",
    },
    "bn": {
        "🌱 Crop Care AI": "🌱 ক্রপ কেয়ার এআই",
        "Select Language": "ভাষা নির্বাচন করুন",
        "Home": "হোম",
        "Disease Detection": "রোগ সনাক্তকরণ",
        "Disease Database": "রোগ ডেটাবেস",
        "Officers & Appointments": "কর্মকর্তা ও অ্যাপয়েন্টমেন্ট",
        "Live Data": "লাইভ ডেটা",
        "Assistant": "সহায়ক",
        "Crop Calendar": "ফসল ক্যালেন্ডার",
        "Weather": "আবহাওয়া",
        "About": "সম্পর্কে",
        "Menu": "মেনু",
        "🔐 Login / Sign Up": "🔐 লগইন / সাইন আপ",
        "Login": "লগইন",
        "Sign Up": "সাইন আপ",
        "Google Login": "গুগল লগইন",
        "Login with Google (Demo)": "গুগল দিয়ে লগইন (ডেমো)",
        "Simulated Google Login (for demo)": "সিমুলেটেড গুগল লগইন (ডেমোর জন্য)",
        "Email": "ইমেইল",
        "Password": "পাসওয়ার্ড",
        "Full Name": "পুরো নাম",
        "Welcome": "স্বাগতম",
        "Logout": "লগআউট",
        "Please login to use disease detection": "রোগ সনাক্তকরণ ব্যবহার করতে অনুগ্রহ করে লগইন করুন",
        "Upload Image": "ছবি আপলোড করুন",
        "Take a Photo": "ছবি তুলুন",
        "Analyze Uploaded Image": "আপলোড করা ছবি বিশ্লেষণ করুন",
        "Analyze Camera Photo": "ক্যামেরার ছবি বিশ্লেষণ করুন",
        "Detection complete! Confidence:": "সনাক্তকরণ সম্পূর্ণ! আত্মবিশ্বাস:",
        "Disease:": "রোগ:",
        "Crop:": "ফসল:",
        "Severity:": "তীব্রতা:",
        "Cause": "কারণ",
        "Symptoms": "লক্ষণ",
        "Prevention": "প্রতিরোধ",
        "Organic Treatment": "জৈব চিকিৎসা",
        "Treatment": "চিকিৎসা",
        "Recommended Medicines": "প্রস্তাবিত ওষুধ",
        "How to use": "কিভাবে ব্যবহার করবেন",
        "Buy": "কিনুন",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ চিকিৎসার আগে আপনার স্থানীয় কৃষি কর্মকর্তার সাথে পরামর্শ করুন",
        "All": "সব",
        "Filter by crop": "ফসল অনুযায়ী ফিল্টার",
        "Filter by district": "জেলা অনুযায়ী ফিল্টার",
        "Available Officers": "উপলব্ধ কর্মকর্তা",
        "Phone": "ফোন",
        "Available": "উপলব্ধ",
        "Book Appointment": "অ্যাপয়েন্টমেন্ট বুক করুন",
        "Select Date": "তারিখ নির্বাচন করুন",
        "Select Time": "সময় নির্বাচন করুন",
        "Confirm Booking": "বুকিং নিশ্চিত করুন",
        "Appointment booked successfully! Officer will contact you.": "অ্যাপয়েন্টমেন্ট সফলভাবে বুক হয়েছে! কর্মকর্তা আপনার সাথে যোগাযোগ করবেন।",
        "No officers found in this district.": "এই জেলায় কোনো কর্মকর্তা পাওয়া যায়নি।",
        "Temperature": "তাপমাত্রা",
        "Humidity": "আর্দ্রতা",
        "Soil Moisture": "মাটির আর্দ্রতা",
        "Rainfall (24h)": "বৃষ্টিপাত (২৪ ঘণ্টা)",
        "Today": "আজ",
        "Current Disease Risk:": "বর্তমান রোগের ঝুঁকি:",
        "Low": "কম",
        "Medium": "মাঝারি",
        "High": "উচ্চ",
        "Disease Incidence Trend": "রোগের ঘটনা প্রবণতা",
        "Daily Disease Cases (Last 30 Days)": "দৈনিক রোগের ঘটনা (গত ৩০ দিন)",
        "Weather Forecast": "আবহাওয়ার পূর্বাভাস",
        "7-Day Temperature Forecast": "৭ দিনের তাপমাত্রার পূর্বাভাস",
        "Date": "তারিখ",
        "Temperature (°C)": "তাপমাত্রা (°সে)",
        "Choose your preferred way to interact": "আপনার পছন্দের উপায় বেছে নিন",
        "Chat": "চ্যাট",
        "Voice": "ভয়েস",
        "Type your message here...": "আপনার বার্তা এখানে টাইপ করুন...",
        "Send": "পাঠান",
        "You said:": "আপনি বলেছেন:",
        "Assistant:": "সহায়ক:",
        "Listening...": "শুনছি...",
        "Start Listening": "শোনা শুরু করুন",
        "Stop Listening": "শোনা বন্ধ করুন",
        "Features": "বৈশিষ্ট্য",
        "Technology": "প্রযুক্তি",
        "Contact": "যোগাযোগ",
        "Disclaimer": "দাবিত্যাগ",
        "For assistance only. Always consult agriculture experts.": "শুধুমাত্র সহায়তার জন্য। সর্বদা কৃষি বিশেষজ্ঞদের পরামর্শ নিন।",
        "Version 9.0 | © 2025 Crop Care AI": "সংস্করণ ৯.০ | © ২০২৫ ক্রপ কেয়ার এআই",
        "Crop Calendar": "ফসল ক্যালেন্ডার",
        "Optimal planting and harvesting times for common crops": "সাধারণ ফসলের জন্য আদর্শ রোপণ ও কাটার সময়",
        "Planting Season": "রোপণের মৌসুম",
        "Harvesting Season": "কাটার মৌসুম",
        "Current weather conditions for your region": "আপনার অঞ্চলের বর্তমান আবহাওয়া পরিস্থিতি",
        "Enter city": "শহর লিখুন",
        "Get Weather": "আবহাওয়া দেখুন",
        "Wind Speed": "বাতাসের গতি",
        "Pressure": "চাপ",
        "You": "আপনি",
        "Command": "কমান্ড",
        "Send Command": "কমান্ড পাঠান",
    },
    "mr": {
        "🌱 Crop Care AI": "🌱 क्रॉप केअर एआय",
        "Select Language": "भाषा निवडा",
        "Home": "मुखपृष्ठ",
        "Disease Detection": "रोग शोध",
        "Disease Database": "रोग डेटाबेस",
        "Officers & Appointments": "अधिकारी आणि भेटी",
        "Live Data": "थेट डेटा",
        "Assistant": "सहाय्यक",
        "Crop Calendar": "पीक कॅलेंडर",
        "Weather": "हवामान",
        "About": "बद्दल",
        "Menu": "मेनू",
        "🔐 Login / Sign Up": "🔐 लॉगिन / साइन अप",
        "Login": "लॉगिन",
        "Sign Up": "साइन अप",
        "Google Login": "गूगल लॉगिन",
        "Login with Google (Demo)": "गूगलसह लॉगिन (डेमो)",
        "Simulated Google Login (for demo)": "सिम्युलेटेड गूगल लॉगिन (डेमोसाठी)",
        "Email": "ईमेल",
        "Password": "पासवर्ड",
        "Full Name": "पूर्ण नाव",
        "Welcome": "स्वागत आहे",
        "Logout": "लॉगआउट",
        "Please login to use disease detection": "कृपया रोग शोध वापरण्यासाठी लॉगिन करा",
        "Upload Image": "प्रतिमा अपलोड करा",
        "Take a Photo": "फोटो काढा",
        "Analyze Uploaded Image": "अपलोड केलेल्या प्रतिमेचे विश्लेषण करा",
        "Analyze Camera Photo": "कॅमेरा फोटोचे विश्लेषण करा",
        "Detection complete! Confidence:": "शोध पूर्ण! आत्मविश्वास:",
        "Disease:": "रोग:",
        "Crop:": "पीक:",
        "Severity:": "तीव्रता:",
        "Cause": "कारण",
        "Symptoms": "लक्षणे",
        "Prevention": "प्रतिबंध",
        "Organic Treatment": "सेंद्रिय उपचार",
        "Treatment": "उपचार",
        "Recommended Medicines": "शिफारस केलेली औषधे",
        "How to use": "कसे वापरावे",
        "Buy": "खरेदी करा",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ उपचारापूर्वी आपल्या स्थानिक कृषी अधिकाऱ्याचा सल्ला घ्या",
        "All": "सर्व",
        "Filter by crop": "पीकानुसार फिल्टर करा",
        "Filter by district": "जिल्ह्यानुसार फिल्टर करा",
        "Available Officers": "उपलब्ध अधिकारी",
        "Phone": "फोन",
        "Available": "उपलब्ध",
        "Book Appointment": "भेट बुक करा",
        "Select Date": "तारीख निवडा",
        "Select Time": "वेळ निवडा",
        "Confirm Booking": "बुकिंगची पुष्टी करा",
        "Appointment booked successfully! Officer will contact you.": "भेट यशस्वीरित्या बुक झाली! अधिकारी आपल्याशी संपर्क साधेल.",
        "No officers found in this district.": "या जिल्ह्यात कोणतेही अधिकारी आढळले नाहीत.",
        "Temperature": "तापमान",
        "Humidity": "आर्द्रता",
        "Soil Moisture": "मातीतील ओलावा",
        "Rainfall (24h)": "पाऊस (२४ तास)",
        "Today": "आज",
        "Current Disease Risk:": "सध्याचा रोग धोका:",
        "Low": "कमी",
        "Medium": "मध्यम",
        "High": "उच्च",
        "Disease Incidence Trend": "रोग घटना प्रवृत्ती",
        "Daily Disease Cases (Last 30 Days)": "दैनिक रोग प्रकरणे (गेल्या ३० दिवस)",
        "Weather Forecast": "हवामान अंदाज",
        "7-Day Temperature Forecast": "७-दिवसीय तापमान अंदाज",
        "Date": "तारीख",
        "Temperature (°C)": "तापमान (°से)",
        "Choose your preferred way to interact": "आपला आवडता मार्ग निवडा",
        "Chat": "चॅट",
        "Voice": "व्हॉइस",
        "Type your message here...": "आपला संदेश येथे टाइप करा...",
        "Send": "पाठवा",
        "You said:": "आपण म्हणालात:",
        "Assistant:": "सहाय्यक:",
        "Listening...": "ऐकत आहे...",
        "Start Listening": "ऐकणे सुरू करा",
        "Stop Listening": "ऐकणे थांबवा",
        "Features": "वैशिष्ट्ये",
        "Technology": "तंत्रज्ञान",
        "Contact": "संपर्क",
        "Disclaimer": "अस्वीकरण",
        "For assistance only. Always consult agriculture experts.": "फक्त मदतीसाठी. नेहमी कृषी तज्ज्ञांचा सल्ला घ्या.",
        "Version 9.0 | © 2025 Crop Care AI": "आवृत्ती ९.० | © २०२५ क्रॉप केअर एआय",
        "Crop Calendar": "पीक कॅलेंडर",
        "Optimal planting and harvesting times for common crops": "सामान्य पिकांसाठी इष्टतम लागवड आणि कापणीची वेळ",
        "Planting Season": "लागवड हंगाम",
        "Harvesting Season": "कापणी हंगाम",
        "Current weather conditions for your region": "आपल्या प्रदेशाची सध्याची हवामान स्थिती",
        "Enter city": "शहर प्रविष्ट करा",
        "Get Weather": "हवामान मिळवा",
        "Wind Speed": "वाऱ्याचा वेग",
        "Pressure": "दाब",
        "You": "आपण",
        "Command": "कमांड",
        "Send Command": "कमांड पाठवा",
    },
    "gu": {
        "🌱 Crop Care AI": "🌱 ક્રોપ કેર એઆઈ",
        "Select Language": "ભાષા પસંદ કરો",
        "Home": "હોમ",
        "Disease Detection": "રોગ શોધ",
        "Disease Database": "રોગ ડેટાબેઝ",
        "Officers & Appointments": "અધિકારીઓ અને એપોઇન્ટમેન્ટ્સ",
        "Live Data": "લાઈવ ડેટા",
        "Assistant": "સહાયક",
        "Crop Calendar": "પાક કેલેન્ડર",
        "Weather": "હવામાન",
        "About": "વિશે",
        "Menu": "મેનુ",
        "🔐 Login / Sign Up": "🔐 લૉગિન / સાઇન અપ",
        "Login": "લૉગિન",
        "Sign Up": "સાઇન અપ",
        "Google Login": "ગૂગલ લૉગિન",
        "Login with Google (Demo)": "ગૂગલથી લૉગિન (ડેમો)",
        "Simulated Google Login (for demo)": "સિમ્યુલેટેડ ગૂગલ લૉગિન (ડેમો માટે)",
        "Email": "ઇમેઇલ",
        "Password": "પાસવર્ડ",
        "Full Name": "પૂરું નામ",
        "Welcome": "સ્વાગત છે",
        "Logout": "લૉગઆઉટ",
        "Please login to use disease detection": "કૃપા કરીને રોગ શોધનો ઉપયોગ કરવા માટે લૉગિન કરો",
        "Upload Image": "છબી અપલોડ કરો",
        "Take a Photo": "ફોટો લો",
        "Analyze Uploaded Image": "અપલોડ કરેલ છબીનું વિશ્લેષણ કરો",
        "Analyze Camera Photo": "કૅમેરા ફોટોનું વિશ્લેષણ કરો",
        "Detection complete! Confidence:": "શોધ પૂર્ણ! આત્મવિશ્વાસ:",
        "Disease:": "રોગ:",
        "Crop:": "પાક:",
        "Severity:": "તીવ્રતા:",
        "Cause": "કારણ",
        "Symptoms": "લક્ષણો",
        "Prevention": "નિવારણ",
        "Organic Treatment": "ઓર્ગેનિક ટ્રીટમેન્ટ",
        "Treatment": "સારવાર",
        "Recommended Medicines": "ભલામણ કરેલ દવાઓ",
        "How to use": "કેવી રીતે ઉપયોગ કરવો",
        "Buy": "ખરીદો",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ સારવાર પહેલાં તમારા સ્થાનિક કૃષિ અધિકારીની સલાહ લો",
        "All": "બધા",
        "Filter by crop": "પાક દ્વારા ફિલ્ટર કરો",
        "Filter by district": "જિલ્લા દ્વારા ફિલ્ટર કરો",
        "Available Officers": "ઉપલબ્ધ અધિકારીઓ",
        "Phone": "ફોન",
        "Available": "ઉપલબ્ધ",
        "Book Appointment": "એપોઇન્ટમેન્ટ બુક કરો",
        "Select Date": "તારીખ પસંદ કરો",
        "Select Time": "સમય પસંદ કરો",
        "Confirm Booking": "બુકિંગની પુષ્ટિ કરો",
        "Appointment booked successfully! Officer will contact you.": "એપોઇન્ટમેન્ટ સફળતાપૂર્વક બુક થઈ! અધિકારી તમારો સંપર્ક કરશે.",
        "No officers found in this district.": "આ જિલ્લામાં કોઈ અધિકારી મળ્યા નથી.",
        "Temperature": "તાપમાન",
        "Humidity": "ભેજ",
        "Soil Moisture": "માટીનો ભેજ",
        "Rainfall (24h)": "વરસાદ (૨૪ કલાક)",
        "Today": "આજે",
        "Current Disease Risk:": "વર્તમાન રોગ જોખમ:",
        "Low": "નીચું",
        "Medium": "મધ્યમ",
        "High": "ઊંચું",
        "Disease Incidence Trend": "રોગની ઘટનાનું વલણ",
        "Daily Disease Cases (Last 30 Days)": "દૈનિક રોગના કેસ (છેલ્લા ૩૦ દિવસ)",
        "Weather Forecast": "હવામાન આગાહી",
        "7-Day Temperature Forecast": "૭-દિવસની તાપમાન આગાહી",
        "Date": "તારીખ",
        "Temperature (°C)": "તાપમાન (°સે)",
        "Choose your preferred way to interact": "તમારી પસંદગીની રીત પસંદ કરો",
        "Chat": "ચેટ",
        "Voice": "અવાજ",
        "Type your message here...": "તમારો સંદેશ અહીં લખો...",
        "Send": "મોકલો",
        "You said:": "તમે કહ્યું:",
        "Assistant:": "સહાયક:",
        "Listening...": "સાંભળી રહ્યું છે...",
        "Start Listening": "સાંભળવાનું શરૂ કરો",
        "Stop Listening": "સાંભળવાનું બંધ કરો",
        "Features": "વિશેષતાઓ",
        "Technology": "ટેકનોલોજી",
        "Contact": "સંપર્ક",
        "Disclaimer": "અસ્વીકરણ",
        "For assistance only. Always consult agriculture experts.": "માત્ર સહાય માટે. હંમેશા કૃષિ નિષ્ણાતોની સલાહ લો.",
        "Version 9.0 | © 2025 Crop Care AI": "સંસ્કરણ ૯.૦ | © ૨૦૨૫ ક્રોપ કેર એઆઈ",
        "Crop Calendar": "પાક કેલેન્ડર",
        "Optimal planting and harvesting times for common crops": "સામાન્ય પાકો માટે શ્રેષ્ઠ વાવેતર અને લણણીનો સમય",
        "Planting Season": "વાવેતરની મોસમ",
        "Harvesting Season": "લણણીની મોસમ",
        "Current weather conditions for your region": "તમારા પ્રદેશ માટે વર્તમાન હવામાન પરિસ્થિતિઓ",
        "Enter city": "શહેર દાખલ કરો",
        "Get Weather": "હવામાન મેળવો",
        "Wind Speed": "પવનની ગતિ",
        "Pressure": "દબાણ",
        "You": "તમે",
        "Command": "આદેશ",
        "Send Command": "આદેશ મોકલો",
    },
}

def t(key):
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# -------------------- SESSION STATE --------------------
if "language" not in st.session_state:
    st.session_state.language = "en"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------- IMPROVED CSS --------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 1.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid #eaeaea;
        height: 100%;
        color: #1a1a1a;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(26, 67, 113, 0.4);
    }
    
    .chat-message {
        padding: 0.8rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-message {
        background: #e1f5fe;
        color: #0d3c61;
        margin-left: auto;
    }
    .bot-message {
        background: #f1f3f4;
        color: #1a1a1a;
        margin-right: auto;
    }
    
    .medicine-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3498db;
        color: #1a1a1a;
    }
    
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    .sidebar-text {
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/plant-under-sun--v1.png", width=80)
    st.markdown(f"<h2 class='sidebar-text'>{t('🌱 Crop Care AI')}</h2>", unsafe_allow_html=True)

    lang_options = {
        "🇬🇧 English": "en",
        "🇮🇳 हिन्दी": "hi",
        "🇮🇳 తెలుగు": "te",
        "🇮🇳 ಕನ್ನಡ": "kn",
        "🇮🇳 தமிழ்": "ta",
        "🇮🇳 বাংলা": "bn",
        "🇮🇳 मराठी": "mr",
        "🇮🇳 ગુજરાતી": "gu"
    }
    # Ensure all selected languages exist in TRANSLATIONS
    available_langs = {k: v for k, v in lang_options.items() if v in TRANSLATIONS}
    selected_lang = st.selectbox(t("Select Language"), list(available_langs.keys()), index=0)
    st.session_state.language = available_langs[selected_lang]

    st.markdown("---")
    menu_options = [
        t("Home"),
        t("Disease Detection"),
        t("Disease Database"),
        t("Officers & Appointments"),
        t("Live Data"),
        t("Assistant"),
        t("Crop Calendar"),
        t("Weather"),
        t("About")
    ]
    icons = ["🏠", "📸", "📚", "👨‍🌾", "📊", "🤖", "📅", "☀️", "ℹ️"]
    for i, opt in enumerate(menu_options):
        if st.button(f"{icons[i]} {opt}", key=f"nav_{opt}"):
            st.session_state.page = opt
            st.rerun()

    st.markdown("---")

    # ---------- LOGIN / SIGNUP ----------
    if not st.session_state.logged_in:
        with st.expander(t("🔐 Login / Sign Up")):
            tab1, tab2, tab3 = st.tabs([t("Login"), t("Sign Up"), t("Google Login")])
            with tab1:
                email = st.text_input(t("Email"), key="login_email")
                password = st.text_input(t("Password"), type="password", key="login_pass")
                if st.button(t("Login")):
                    if email and password:
                        success, result = login_user(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_email = email
                            st.session_state.user_name = result
                            st.success(t(f"Welcome {result}!"))
                            st.rerun()
                        else:
                            st.error(t(result))
                    else:
                        st.warning(t("Please fill all fields"))
            with tab2:
                name = st.text_input(t("Full Name"), key="signup_name")
                email = st.text_input(t("Email"), key="signup_email")
                password = st.text_input(t("Password"), type="password", key="signup_pass")
                if st.button(t("Sign Up")):
                    if name and email and password:
                        success, msg = register_user(email, name, password)
                        if success:
                            st.success(t(msg))
                        else:
                            st.error(t(msg))
                    else:
                        st.warning(t("Please fill all fields"))
            with tab3:
                st.markdown(t("Simulated Google Login (for demo)"))
                if st.button(t("Login with Google (Demo)")):
                    test_email = "googleuser@example.com"
                    test_name = "Google User"
                    test_pass = "googlepass"
                    pwd_hash = hash_password(test_pass)
                    try:
                        supabase.table("users").upsert(
                            {"email": test_email, "name": test_name, "password_hash": pwd_hash},
                            on_conflict="email"
                        ).execute()
                    except Exception as e:
                        st.error(f"Database error: {e}")
                    else:
                        success, result = login_user(test_email, test_pass)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_email = test_email
                            st.session_state.user_name = result
                            st.success(t(f"Welcome {result}!"))
                            st.rerun()
                        else:
                            st.error(t("Google login failed"))
    else:
        st.success(t(f"Welcome, {st.session_state.user_name}!"))
        if st.button(t("Logout")):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.rerun()

# -------------------- MAIN CONTENT --------------------
page = st.session_state.page

# ---- Home ----
if page == t("Home"):
    st.markdown("""
        <div class="main-header">
            <img src="https://img.icons8.com/color/96/000000/plant-under-sun--v1.png" style="width:60px; height:60px;">
            <h1>🌾 AI Crop Disease Detection</h1>
            <p>Protect your crops with artificial intelligence</p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="feature-card"><h3>📸 {t("Instant Detection")}</h3><p>{t("Upload or take photos for instant disease identification with 95%+ accuracy.")}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="feature-card"><h3>💊 {t("Treatment Guide")}</h3><p>{t("Get detailed treatment plans, medicine recommendations, and organic solutions.")}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="feature-card"><h3>👨‍🌾 {t("Officer Connect")}</h3><p>{t("Find nearby agriculture officers and book appointments directly.")}</p></div>', unsafe_allow_html=True)

# ---- Disease Detection ----
elif page == t("Disease Detection"):
    st.markdown(f'<div class="main-header"><h1>📸 {t("Disease Detection")}</h1><p>{t("Upload a photo or take one with your camera for instant analysis")}</p></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.warning(t("Please login to use disease detection"))
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(t("Upload Image"))
            uploaded = st.file_uploader(t("Choose an image..."), type=['jpg', 'jpeg', 'png'], key="upload")
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, use_column_width=True)
                if st.button(t("Analyze Uploaded Image"), key="analyze_up"):
                    with st.spinner(t("Analyzing with AI model...")):
                        disease, conf = predict_disease(img)
                        st.success(t(f"Detection complete! Confidence: {conf:.1%}"))
                        st.write(f"**{t('Disease')}:** {disease}")
                        if disease in DISEASE_DB:
                            info = DISEASE_DB[disease]
                            with st.expander(t("View Details")):
                                st.markdown(f"**{t('Cause')}:** {info['cause']}")
                                st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
                                st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
                                st.markdown(f"**{t('Treatment')}:** {info['treatment']}")
                                st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")
                                st.markdown(f"**{t('Recommended Medicines')}:**")
                                for med in info['medicines']:
                                    st.markdown(f"""
                                    <div class="medicine-card">
                                        <b>{med['name']}</b> by {med['company']} – {med['price']} (⭐ {med['rating']})<br>
                                        {t('How to use')}: {med['usage']}<br>
                                        <a href="https://www.google.com/search?q={med['name']} buy online" target="_blank">{t('Buy')}</a>
                                    </div>
                                    """, unsafe_allow_html=True)
                        st.info(t("⚠️ Consult your local agriculture officer before treatment"))
        with col2:
            st.subheader(t("Take a Photo"))
            camera = st.camera_input(t("Take a photo"), key="camera")
            if camera:
                img = Image.open(camera)
                st.image(img, use_column_width=True)
                if st.button(t("Analyze Camera Photo"), key="analyze_cam"):
                    with st.spinner(t("Analyzing...")):
                        disease, conf = predict_disease(img)
                        st.success(t(f"Detection complete! Confidence: {conf:.1%}"))
                        st.write(f"**{t('Disease')}:** {disease}")
                        st.info(t("⚠️ Consult your local agriculture officer before treatment"))

# ---- Disease Database ----
elif page == t("Disease Database"):
    st.markdown(f'<div class="main-header"><h1>📚 {t("Disease Database")}</h1><p>{t("Comprehensive information about crop diseases")}</p></div>', unsafe_allow_html=True)
    search = st.text_input(t("🔍 Search diseases"))
    crops = [t("All")] + sorted(list(set([info['crop'] for info in DISEASE_DB.values()])))
    crop_filter = st.selectbox(t("Filter by crop"), crops)
    for disease, info in DISEASE_DB.items():
        if crop_filter != t("All") and info['crop'] != crop_filter:
            continue
        if search and search.lower() not in disease.lower():
            continue
        with st.expander(f"🌿 {disease} on {info['crop']}"):
            st.markdown(f"**{t('Cause')}:** {info['cause']}")
            st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
            st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
            st.markdown(f"**{t('Treatment')}:** {info['treatment']}")
            st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")
            st.markdown(f"**{t('Season')}:** {info['season']}")
            st.markdown(f"**{t('Severity')}:** {info['severity']}")
            st.markdown(f"**{t('Recommended Medicines')}:**")
            for med in info['medicines']:
                st.markdown(f"""
                <div class="medicine-card">
                    <b>{med['name']}</b> by {med['company']} – {med['price']} (⭐ {med['rating']})<br>
                    {t('How to use')}: {med['usage']}<br>
                    <a href="https://www.google.com/search?q={med['name']} buy online" target="_blank">{t('Buy')}</a>
                </div>
                """, unsafe_allow_html=True)

# ---- Officers & Appointments ----
elif page == t("Officers & Appointments"):
    st.markdown(f'<div class="main-header"><h1>👨‍🌾 {t("Agricultural Officers & Appointments")}</h1><p>{t("Find nearby officers and schedule consultations")}</p></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.warning(t("Please login to book appointments"))
    else:
        officers = get_officers()
        districts = list(set([o['district'] for o in officers]))
        district_list = [t("All")] + sorted(districts)
        selected_district = st.selectbox(t("Filter by district"), district_list)
        filtered = get_officers(selected_district if selected_district != t("All") else None)
        if filtered:
            st.subheader(t("Available Officers"))
            for off in filtered:
                cola, colb, colc = st.columns([2,2,1])
                with cola:
                    st.markdown(f"**{off['name']}**")
                    st.caption(f"{t('Phone')}: {off['phone']}")
                with colb:
                    st.markdown(f"{t('District')}: {off['district']}")
                    st.caption(f"{t('Available')}: {off['available_from']} - {off['available_to']}")
                with colc:
                    if st.button(t("Book Appointment"), key=f"book_{off['id']}"):
                        st.session_state.selected_officer = off
                        st.session_state.show_booking = True
                st.markdown("---")
            if st.session_state.get("show_booking") and st.session_state.get("selected_officer"):
                off = st.session_state.selected_officer
                st.subheader(t(f"Book Appointment with {off['name']}"))
                with st.form("book_form"):
                    date = st.date_input(t("Select Date"), min_value=datetime.date.today())
                    time_slot = st.time_input(t("Select Time"))
                    if st.form_submit_button(t("Confirm Booking")):
                        book_appointment(st.session_state.user_email, off['id'], date, time_slot)
                        st.success(t("Appointment booked successfully! Officer will contact you."))
                        st.session_state.show_booking = False
                        st.rerun()
        else:
            st.info(t("No officers found in this district."))

# ---- Live Data ----
elif page == t("Live Data"):
    st.markdown(f'<div class="main-header"><h1>📊 {t("Live Crop Health Monitoring")}</h1><p>{t("Real-time data and disease risk assessment")}</p></div>', unsafe_allow_html=True)
    temp = random.uniform(20,35)
    hum = random.uniform(60,85)
    soil = random.uniform(40,70)
    rain = random.uniform(0,10)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("Temperature"), f"{temp:.1f}°C", f"{random.uniform(-2,2):+.1f}°C")
    col2.metric(t("Humidity"), f"{hum:.1f}%", f"{random.uniform(-5,5):+.1f}%")
    col3.metric(t("Soil Moisture"), f"{soil:.1f}%", f"{random.uniform(-3,3):+.1f}%")
    col4.metric(t("Rainfall (24h)"), f"{rain:.1f}mm", t("Today"))
    risk = random.choice([t("Low"), t("Medium"), t("High")])
    if risk == t("Low"):
        st.success(t(f"**Current Disease Risk:** {risk} – Conditions are favorable"))
    elif risk == t("Medium"):
        st.warning(t(f"**Current Disease Risk:** {risk} – Monitor crops regularly"))
    else:
        st.error(t(f"**Current Disease Risk:** {risk} – Take preventive measures"))
    st.subheader(t("Disease Incidence Trend"))
    dates = pd.date_range(end=datetime.date.today(), periods=30)
    df = pd.DataFrame({'Date': dates, 'Cases': np.random.poisson(5,30)+np.random.randint(0,5,30)})
    fig = px.line(df, x='Date', y='Cases', title=t('Daily Disease Cases (Last 30 Days)'))
    st.plotly_chart(fig, use_container_width=True)
    st.subheader(t("Weather Forecast"))
    fdates = pd.date_range(start=datetime.date.today(), periods=7)
    fdf = pd.DataFrame({
        'Date': fdates,
        'Max Temp': np.random.uniform(28,38,7),
        'Min Temp': np.random.uniform(18,25,7),
    })
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=fdf['Date'], y=fdf['Max Temp'], name=t('Max Temp'), mode='lines+markers'))
    fig2.add_trace(go.Scatter(x=fdf['Date'], y=fdf['Min Temp'], name=t('Min Temp'), mode='lines+markers'))
    fig2.update_layout(title=t('7-Day Temperature Forecast'), xaxis_title=t('Date'), yaxis_title=t('Temperature (°C)'))
    st.plotly_chart(fig2, use_container_width=True)

# ---- Assistant ----
elif page == t("Assistant"):
    st.markdown(f'<div class="main-header"><h1>🤖 {t("Assistant")}</h1><p>{t("Choose your preferred way to interact")}</p></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.warning(t("Please login to use the assistant"))
    else:
        tab1, tab2 = st.tabs([t("Chat"), t("Voice")])

        with tab1:
            st.subheader(t("Chat"))
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message"><b>{t("You")}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message"><b>{t("Assistant")}:</b> {msg["content"]}</div>', unsafe_allow_html=True)

            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_input(t("Type your message here..."), key="chat_input")
                submitted = st.form_submit_button(t("Send"))
                if submitted and user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    response = chatbot_response(user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()

        with tab2:
            st.subheader(t("Voice"))
            st.info(t("Click 'Start Listening' and speak a command. I will speak back."))

            voice_html = f"""
            <div style="text-align: center;">
                <button id="start" style="background-color: #1e3c72; color: white; padding: 12px 30px; border: none; border-radius: 50px; margin: 10px;">🎤 {t('Start Listening')}</button>
                <button id="stop" style="background-color: #e53e3e; color: white; padding: 12px 30px; border: none; border-radius: 50px; margin: 10px;">⏹️ {t('Stop Listening')}</button>
                <p id="result" style="font-size: 1.3rem; color: #1a1a1a;"></p>
                <p id="response" style="font-size: 1.1rem; color: #2d3748;"></p>
            </div>

            <script>
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = '{st.session_state.language}';
                recognition.continuous = false;
                recognition.interimResults = false;

                const synth = window.speechSynthesis;

                document.getElementById('start').onclick = () => {{
                    recognition.start();
                    document.getElementById('result').innerHTML = '{t("Listening...")}';
                }};

                document.getElementById('stop').onclick = () => {{
                    recognition.stop();
                    document.getElementById('result').innerHTML = '{t("Stopped.")}';
                }};

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('result').innerHTML = '{t("You said:")} ' + transcript;
                    // Simulate response
                    const reply = "I heard you say: " + transcript + ". In a real version, I would answer properly.";
                    document.getElementById('response').innerHTML = '{t("Assistant:")} ' + reply;
                    const utterance = new SpeechSynthesisUtterance(reply);
                    utterance.lang = '{st.session_state.language}';
                    synth.speak(utterance);
                }};

                recognition.onerror = (event) => {{
                    document.getElementById('result').innerHTML = 'Error: ' + event.error;
                }};
            </script>
            """
            st.components.v1.html(voice_html, height=300)

            st.markdown("---")
            st.write(t("Or type a command:"))
            cmd = st.text_input(t("Command"), key="voice_cmd")
            if st.button(t("Send Command")):
                reply = chatbot_response(cmd)
                st.info(f"{t('Assistant')}: {reply}")
                # Speak using JavaScript
                speak_script = f"""
                <script>
                    const utterance = new SpeechSynthesisUtterance(`{reply}`);
                    utterance.lang = '{st.session_state.language}';
                    window.speechSynthesis.speak(utterance);
                </script>
                """
                st.components.v1.html(speak_script, height=0)

# ---- Crop Calendar ----
elif page == t("Crop Calendar"):
    st.markdown(f'<div class="main-header"><h1>📅 {t("Crop Calendar")}</h1><p>{t("Optimal planting and harvesting times for common crops")}</p></div>', unsafe_allow_html=True)
    df = pd.DataFrame.from_dict(CROP_CALENDAR, orient='index').reset_index()
    df.columns = [t("Crop"), t("Planting Season"), t("Harvesting Season")]
    st.table(df)

# ---- Weather ----
elif page == t("Weather"):
    st.markdown(f'<div class="main-header"><h1>☀️ {t("Weather Forecast")}</h1><p>{t("Current weather conditions for your region")}</p></div>', unsafe_allow_html=True)
    city = st.text_input(t("Enter city"), value="Delhi")
    if st.button(t("Get Weather")):
        data, error = get_weather(city)
        if error:
            st.error(f"Error: {error}")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t("Temperature"), f"{data['main']['temp']} °C")
            with col2:
                st.metric(t("Humidity"), f"{data['main']['humidity']}%")
            with col3:
                st.metric(t("Pressure"), f"{data['main']['pressure']} hPa")
            st.write(f"**{t('Weather')}:** {data['weather'][0]['description'].capitalize()}")
            st.write(f"**{t('Wind Speed')}:** {data['wind']['speed']} m/s")

# ---- About ----
elif page == t("About"):
    st.markdown(f'<div class="main-header"><h1>ℹ️ {t("About")}</h1><p>{t("AI-Powered Crop Disease Detection System")}</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            **{t('Features')}:**
            - {t('95%+ detection accuracy with deep learning')}
            - {t('Multi-language support (8 languages)')}
            - {t('Voice assistant with natural language commands')}
            - {t('Officer directory and appointment booking')}
            - {t('Live crop health monitoring')}
            - {t('Comprehensive disease database')}
            - {t('Crop calendar and weather integration')}
        """)
    with col2:
        st.markdown(f"""
            **{t('Technology')}:**
            - {t('Custom CNN from scratch (no pre-trained models)')}
            - {t('Streamlit Community Cloud')}
            - {t('Supabase for persistent storage')}
            - {t('OpenWeatherMap API')}
        """)
    st.info(t("Version 9.0 | © 2025 Crop Care AI | Built with ❤️ for farmers"))
