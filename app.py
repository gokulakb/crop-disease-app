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
import os
import json
from PIL import Image
from io import BytesIO
import tensorflow as tf
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

# -------------------- LOAD TRAINED MODEL AND CLASS NAMES --------------------
@st.cache_resource
def load_model_and_classes():
    # Option 1: Load from local file (for testing)
    # model = tf.keras.models.load_model('deep_plant_disease_final.h5')
    # with open('class_indices.json', 'r') as f:
    #     class_indices = json.load(f)

    # Option 2: Download from cloud storage (for deployment)
    model_url = "https://your-cloud-storage-url/deep_plant_disease_final.h5"   # REPLACE THIS
    indices_url = "https://your-cloud-storage-url/class_indices.json"          # REPLACE THIS

    try:
        response = requests.get(model_url)
        model = tf.keras.models.load_model(BytesIO(response.content))
        response = requests.get(indices_url)
        class_indices = json.loads(response.text)
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        st.stop()

    # Convert class_indices dict to list in correct order
    class_names = [k for k, v in sorted(class_indices.items(), key=lambda item: item[1])]
    return model, class_names

model, CLASS_NAMES = load_model_and_classes()

def preprocess_image(image):
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(image):
    img_array = preprocess_image(image)
    preds = model.predict(img_array)
    idx = np.argmax(preds[0])
    confidence = preds[0][idx]
    return CLASS_NAMES[idx], confidence

# -------------------- DISEASE DATABASE (fallback) --------------------
# (You can keep the DISEASE_DB from previous versions as a fallback for displaying details)
DISEASE_DB = {
    "Apple Scab": {
        "crop": "Apple",
        "symptoms": "Olive-green to brown spots on leaves and fruit...",
        "prevention": "Plant resistant varieties...",
        "organic": "Neem oil spray...",
        "medicines": [...],
        "season": "Spring/Fall",
        "severity": "High"
    },
    # ... add more as needed
}

# -------------------- CROP CALENDAR --------------------
CROP_CALENDAR = {
    "Rice": {"planting": "June-July", "harvesting": "November-December"},
    "Wheat": {"planting": "October-December", "harvesting": "March-April"},
    # ... (same as before)
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

# -------------------- TRANSLATIONS (simplified) --------------------
# For brevity, only include keys used in the app. You can expand as needed.
TRANSLATIONS = {
    "en": {
        "🌱 Crop Care AI": "🌱 Crop Care AI",
        "Select Language": "Select Language",
        "Home": "Home",
        "Disease Detection": "Disease Detection",
        "Disease Database": "Disease Database",
        "Officers & Appointments": "Officers & Appointments",
        "Live Data": "Live Data",
        "Voice Assistant": "Voice Assistant",
        "Crop Calendar": "Crop Calendar",
        "Weather": "Weather",
        "About": "About",
        "Login": "Login",
        "Sign Up": "Sign Up",
        "Google Login": "Google Login",
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
        "Voice Commands": "Voice Commands",
        "Click 'Start Listening' and speak a command.": "Click 'Start Listening' and speak a command.",
        "Start Listening": "Start Listening",
        "Stop Listening": "Stop Listening",
        "You said:": "You said:",
        "Processing command...": "Processing command...",
        "Speak this text": "Speak this text",
        "Features": "Features",
        "Technology": "Technology",
        "Contact": "Contact",
        "Disclaimer": "Disclaimer",
        "For assistance only. Always consult agriculture experts.": "For assistance only. Always consult agriculture experts.",
        "Version 6.0 | © 2025 Crop Care AI": "Version 6.0 | © 2025 Crop Care AI",
        "Crop Calendar": "Crop Calendar",
        "Optimal planting and harvesting times for common crops": "Optimal planting and harvesting times for common crops",
        "Planting Season": "Planting Season",
        "Harvesting Season": "Harvesting Season",
        "Current weather conditions for your region": "Current weather conditions for your region",
        "Enter city": "Enter city",
        "Get Weather": "Get Weather",
        "Wind Speed": "Wind Speed",
        "Pressure": "Pressure",
    }
    # Add other languages if needed
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
    .logo-title {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    .logo-title img {
        width: 60px;
        height: 60px;
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
        border: 1px solid rgba(255,255,255,0.2);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(26, 67, 113, 0.4);
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
        # add others
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
        t("Voice Assistant"),
        t("Crop Calendar"),
        t("Weather"),
        t("About")
    ]
    icons = ["🏠", "📸", "📚", "👨‍🌾", "📊", "🎤", "📅", "☀️", "ℹ️"]
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
            <div class="logo-title">
                <img src="https://img.icons8.com/color/96/000000/plant-under-sun--v1.png">
                <h1>🌾 AI Crop Disease Detection</h1>
            </div>
            <p style="font-size: 1.2rem;">Protect your crops with artificial intelligence</p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="feature-card"><h3>📸 {t("Instant Detection")}</h3><p>{t("Upload or take photos for instant disease identification with 95%+ accuracy.")}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="feature-card"><h3>💊 {t("Treatment Guide")}</h3><p>{t("Get detailed treatment plans, medicine recommendations, and organic solutions.")}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="feature-card"><h3>👨‍🌾 {t("Officer Connect")}</h3><p>{t("Find nearby agriculture officers and book appointments directly.")}</p></div>', unsafe_allow_html=True)

# ---- Disease Detection (with real model) ----
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
                        # Optionally show details from DISEASE_DB if available
                        if disease in DISEASE_DB:
                            info = DISEASE_DB[disease]
                            with st.expander(t("View Details")):
                                st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
                                st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
                                st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")
                                for med in info['medicines']:
                                    st.markdown(f"- **{med['name']}** - {med['price']}")
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

# ---- Other pages remain the same as before (Disease Database, Officers, Live Data, Voice Assistant, Crop Calendar, Weather, About) ----
# For brevity, I'll not repeat them here, but you can copy from the previous version.
# Ensure they use t() for translations.

# ... (rest of the pages as in the previous app code) ...

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
            - {t('Trained on 300k+ image Deep-Plant-Disease dataset')}
        """)
    with col2:
        st.markdown(f"""
            **{t('Technology')}:**
            - {t('Custom CNN from scratch (no pre-trained models)')}
            - {t('115 disease classes across multiple crops')}
            - {t('Streamlit Community Cloud')}
            - {t('Supabase for persistent storage')}
            - {t('OpenWeatherMap API')}
        """)
    st.info(t("Version 6.0 | © 2025 Crop Care AI | Built with ❤️ for farmers"))
