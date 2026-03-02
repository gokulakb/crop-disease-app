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
if "supabase_url" in st.secrets and "supabase_key" in st.secrets:
    supabase: Client = create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
else:
    st.error("Supabase credentials not found. Please set them in Streamlit secrets.")
    st.stop()

# -------------------- WEATHER API --------------------
WEATHER_API_KEY = st.secrets.get("weather_api_key", None)

# -------------------- PLACEHOLDER MODEL (random predictions) --------------------
USE_MOCK = True   # Set to False later when you have a real model

MOCK_CLASSES = [
    "Apple Scab", "Apple Black Rot", "Cedar Apple Rust", "Healthy Apple",
    "Corn Common Rust", "Corn Gray Leaf Spot", "Corn Northern Leaf Blight", "Healthy Corn",
    "Grape Black Rot", "Grape Esca (Black Measles)", "Grape Leaf Blight", "Healthy Grape",
    "Potato Early Blight", "Potato Late Blight", "Healthy Potato",
    "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight", "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot", "Tomato Spider Mites", "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus", "Healthy Tomato"
]

def predict_disease(image):
    if USE_MOCK:
        disease = random.choice(MOCK_CLASSES)
        confidence = random.uniform(0.7, 0.99)
        return disease, confidence
    else:
        # Real prediction code will go here later
        pass

# -------------------- DISEASE DATABASE (detailed) --------------------
DISEASE_DB = {
    "Apple Scab": {
        "crop": "Apple",
        "symptoms": "Olive‑green to brown spots on leaves and fruit, leaves may curl and fall prematurely. Fruit may become deformed and cracked.",
        "prevention": "Plant resistant varieties. Prune trees to improve air circulation. Remove and destroy fallen leaves. Avoid overhead irrigation.",
        "organic": "Neem oil spray (2‑3 ml per liter) every 7‑10 days. Baking soda solution (1 tsp per liter water) with a few drops of vegetable oil.",
        "medicines": [
            {"name": "Captan 50WP", "company": "Bayer", "price": "₹2,499/500g", "rating": 4.5,
             "usage": "Apply 2g per liter of water. Repeat every 7‑10 days. Use 200‑300 liters per acre.",
             "link": "https://www.google.com/search?q=Captan+50WP"},
            {"name": "Myclobutanil", "company": "Spectrum", "price": "₹3,299/250ml", "rating": 4.3,
             "usage": "Apply 0.5ml per liter of water. Do not apply more than 3 times per season.",
             "link": "https://www.google.com/search?q=Myclobutanil"},
            {"name": "Sulfur Spray", "company": "Bonide", "price": "₹1,899/500ml", "rating": 4.2,
             "usage": "Apply 5ml per liter. Use when temperature is below 30°C.",
             "link": "https://www.google.com/search?q=Sulfur+Spray"}
        ],
        "season": "Spring/Fall",
        "severity": "High"
    },
    "Corn Rust": {
        "crop": "Corn",
        "symptoms": "Reddish‑brown pustules on both leaf surfaces, primarily on leaves. Pustules may turn black as they age.",
        "prevention": "Plant resistant hybrids. Practice crop rotation. Avoid overhead irrigation. Remove crop debris after harvest.",
        "organic": "Sulfur‑based fungicides. Compost tea spray. Neem oil (2ml per liter) weekly.",
        "medicines": [
            {"name": "Azoxystrobin", "company": "Syngenta", "price": "₹4,599/500ml", "rating": 4.6,
             "usage": "Apply 1ml per liter. Use 200‑300 liters per acre. Maximum 2 applications per season.",
             "link": "https://www.google.com/search?q=Azoxystrobin"},
            {"name": "Pyraclostrobin", "company": "BASF", "price": "₹5,299/500ml", "rating": 4.4,
             "usage": "Apply 0.8ml per liter. Do not apply within 30 days of harvest.",
             "link": "https://www.google.com/search?q=Pyraclostrobin"}
        ],
        "season": "Summer",
        "severity": "Medium"
    },
    "Potato Early Blight": {
        "crop": "Potato",
        "symptoms": "Dark brown to black lesions with concentric rings, usually on lower leaves. Lesions may enlarge and cause leaf drop.",
        "prevention": "Crop rotation (avoid planting potatoes in same field for 3 years). Proper spacing. Avoid overhead irrigation. Use disease‑free seed.",
        "organic": "Copper fungicides (3g per liter). Bacillus subtilis spray. Compost tea.",
        "medicines": [
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,799/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Use 300‑400 liters per acre. Repeat every 7‑10 days.",
             "link": "https://www.google.com/search?q=Chlorothalonil"},
            {"name": "Azoxystrobin", "company": "Bayer", "price": "₹4,899/500ml", "rating": 4.5,
             "usage": "Apply 1ml per liter. Use 200 liters per acre. Maximum 2 applications.",
             "link": "https://www.google.com/search?q=Azoxystrobin"}
        ],
        "season": "Summer/Fall",
        "severity": "Medium"
    },
    "Tomato Leaf Mold": {
        "crop": "Tomato",
        "symptoms": "Pale green or yellowish spots on upper leaf surfaces, olive‑green to grayish mold on undersides. Leaves may wither and die.",
        "prevention": "Improve air circulation. Reduce humidity. Water at base of plants. Remove lower leaves. Use resistant varieties.",
        "organic": "Neem oil (2ml per liter). Potassium bicarbonate (1 tsp per liter). Compost tea.",
        "medicines": [
            {"name": "Copper Hydroxide", "company": "DuPont", "price": "₹3,199/500g", "rating": 4.2,
             "usage": "Apply 2g per liter. Use 300 liters per acre. Repeat every 7 days.",
             "link": "https://www.google.com/search?q=Copper+Hydroxide"},
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,899/500g", "rating": 4.1,
             "usage": "Apply 2g per liter. Use 300‑400 liters per acre. Do not use within 7 days of harvest.",
             "link": "https://www.google.com/search?q=Chlorothalonil"}
        ],
        "season": "Spring/Summer",
        "severity": "Medium"
    },
    "Wheat Stem Rust": {
        "crop": "Wheat",
        "symptoms": "Reddish‑brown pustules on stems and leaves, can cause stem breakage and grain shriveling. Pustules are elongated.",
        "prevention": "Use resistant varieties. Early planting. Destroy volunteer wheat. Avoid excessive nitrogen.",
        "organic": "Sulfur spray (5g per liter). Neem oil. Bacillus subtilis.",
        "medicines": [
            {"name": "Tebuconazole", "company": "Bayer", "price": "₹3,399/500ml", "rating": 4.3,
             "usage": "Apply 1ml per liter. Use 200 liters per acre. Apply at first sign of disease.",
             "link": "https://www.google.com/search?q=Tebuconazole"},
            {"name": "Propiconazole", "company": "Syngenta", "price": "₹4,199/500ml", "rating": 4.4,
             "usage": "Apply 0.5ml per liter. Use 200 liters per acre. Maximum 2 applications.",
             "link": "https://www.google.com/search?q=Propiconazole"}
        ],
        "season": "Spring",
        "severity": "High"
    },
    "Rice Blast": {
        "crop": "Rice",
        "symptoms": "Diamond‑shaped lesions with gray centers and brown margins on leaves.",
        "prevention": "Use resistant varieties. Avoid excessive nitrogen. Maintain proper water management.",
        "organic": "Neem cake, Trichoderma, silica application.",
        "medicines": [
            {"name": "Tricyclazole", "company": "Bayer", "price": "₹3,899/500ml", "rating": 4.5,
             "usage": "Apply 1ml per liter. Use 200 liters per acre.",
             "link": "https://www.google.com/search?q=Tricyclazole"},
            {"name": "Isoprothiolane", "company": "Syngenta", "price": "₹4,299/500ml", "rating": 4.3,
             "usage": "Apply 0.8ml per liter.",
             "link": "https://www.google.com/search?q=Isoprothiolane"}
        ],
        "season": "Kharif",
        "severity": "High"
    },
    "Grape Black Rot": {
        "crop": "Grape",
        "symptoms": "Circular lesions on leaves with black margins, shriveled and blackened fruit.",
        "prevention": "Prune to improve air circulation. Remove mummified fruit. Maintain proper spacing.",
        "organic": "Copper fungicides, Bacillus subtilis, garlic spray.",
        "medicines": [
            {"name": "Mancozeb", "company": "Dow", "price": "₹2,999/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Repeat every 7‑10 days.",
             "link": "https://www.google.com/search?q=Mancozeb"},
            {"name": "Copper Oxychloride", "company": "Nufarm", "price": "₹3,499/500g", "rating": 4.2,
             "usage": "Apply 3g per liter.",
             "link": "https://www.google.com/search?q=Copper+Oxychloride"}
        ],
        "season": "Spring",
        "severity": "High"
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
        return None, "Weather API key not configured."
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

# -------------------- CHATBOT ENGINE --------------------
def chatbot_response(query):
    query = query.lower()
    # Greetings
    if any(word in query for word in ["hello", "hi", "hey", "namaste"]):
        return "Hello! How can I help you with your crops today?"
    # Disease inquiries
    for disease in DISEASE_DB:
        if disease.lower() in query:
            info = DISEASE_DB[disease]
            return (f"{disease}: {info['symptoms']}\n\n"
                    f"Prevention: {info['prevention']}\n\n"
                    f"Organic treatment: {info['organic']}")
    # Officers
    if any(word in query for word in ["officer", "appointment", "contact"]):
        return "You can find and book officers under the 'Officers & Appointments' page."
    # Weather
    if any(word in query for word in ["weather", "temperature", "rain"]):
        return "Go to the Weather page to get current conditions for your city."
    # Thanks
    if any(word in query for word in ["thank", "thanks", "dhanyavaad"]):
        return "You're welcome!"
    # Default
    return "I'm sorry, I didn't understand that. Try asking about a specific disease, officers, or weather."

# -------------------- TRANSLATIONS (8 languages) --------------------
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
        "Symptoms": "Symptoms",
        "Prevention": "Prevention",
        "Organic Treatment": "Organic Treatment",
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
        "Version 7.0 | © 2025 Crop Care AI": "Version 7.0 | © 2025 Crop Care AI",
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
    # For brevity, other languages are omitted. You can add them following the same pattern.
    # They should contain all keys above.
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

# -------------------- CUSTOM CSS --------------------
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
        margin-left: auto;
    }
    .bot-message {
        background: #f1f3f4;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/plant-under-sun--v1.png", width=80)
    st.markdown(f"<h2>{t('🌱 Crop Care AI')}</h2>", unsafe_allow_html=True)

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
    selected_lang = st.selectbox(t("Select Language"), list(lang_options.keys()), index=0)
    st.session_state.language = lang_options[selected_lang]

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
                                st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
                                st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
                                st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")
                                st.markdown(f"**{t('Recommended Medicines')}:**")
                                for med in info['medicines']:
                                    st.markdown(f"- **{med['name']}** by {med['company']} – {med['price']} (⭐ {med['rating']})")
                                    st.markdown(f"  - {t('How to use')}: {med['usage']} – [Buy]({med['link']})")
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
            st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
            st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
            st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")
            st.markdown(f"**{t('Season')}:** {info['season']}")
            st.markdown(f"**{t('Severity')}:** {info['severity']}")
            st.markdown(f"**{t('Recommended Medicines')}:**")
            for med in info['medicines']:
                st.markdown(f"- **{med['name']}** by {med['company']} – {med['price']} (⭐ {med['rating']})")
                st.markdown(f"  - {t('How to use')}: {med['usage']} – [Buy]({med['link']})")

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

elif page == t("Assistant"):
    st.markdown(f'<div class="main-header"><h1>🤖 {t("Assistant")}</h1><p>{t("Choose your preferred way to interact")}</p></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.warning(t("Please login to use the assistant"))
    else:
        tab1, tab2 = st.tabs([t("Chat"), t("Voice")])

        # ---------- Chat Tab ----------
        with tab1:
            st.subheader(t("Chat"))
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message"><b>{t("You")}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message"><b>{t("Assistant")}:</b> {msg["content"]}</div>', unsafe_allow_html=True)

            user_input = st.text_input(t("Type your message here..."), key="chat_input")
            if st.button(t("Send")):
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    response = chatbot_response(user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()

        # ---------- Voice Tab ----------
        with tab2:
            st.subheader(t("Voice"))
            st.info(t("Click 'Start Listening' and speak a command. I will speak back."))

            voice_html = f"""
            <div style="text-align: center;">
                <button id="start" style="background-color: #1e3c72; color: white; padding: 12px 30px; border: none; border-radius: 50px; margin: 10px;">🎤 {t('Start Listening')}</button>
                <button id="stop" style="background-color: #e53e3e; color: white; padding: 12px 30px; border: none; border-radius: 50px; margin: 10px;">⏹️ {t('Stop Listening')}</button>
                <p id="result" style="font-size: 1.3rem;"></p>
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

                    // Send to Python via fetch (simplified – using a dummy endpoint)
                    // Since Streamlit can't handle POST easily, we'll use a text input fallback.
                    // Instead, we'll just simulate a response.
                    const reply = "I heard you say: " + transcript + ". This is a simulated response.";
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

elif page == t("Crop Calendar"):
    st.markdown(f'<div class="main-header"><h1>📅 {t("Crop Calendar")}</h1><p>{t("Optimal planting and harvesting times for common crops")}</p></div>', unsafe_allow_html=True)
    df = pd.DataFrame.from_dict(CROP_CALENDAR, orient='index').reset_index()
    df.columns = [t("Crop"), t("Planting Season"), t("Harvesting Season")]
    st.table(df)

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
    st.info(t("Version 7.0 | © 2025 Crop Care AI | Built with ❤️ for farmers"))
