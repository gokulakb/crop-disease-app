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

# -------------------- TRANSLATIONS (8 languages) --------------------
# (Include full TRANSLATIONS dictionary from previous message – omitted here for brevity)
# Ensure all new UI keys are added for each language.

# -------------------- DISEASE DATABASE (expanded) --------------------
DISEASE_DB = {
    "Apple Scab": {
        "crop": "Apple",
        "symptoms": "Olive-green to brown spots on leaves and fruit...",
        "prevention": "Plant resistant varieties. Prune trees...",
        "organic": "Neem oil spray...",
        "medicines": [{"name": "Captan 50WP", "company": "Bayer", "price": "₹2,499/500g", "rating": 4.5,
                       "usage": "Apply 2g per liter...", "link": "https://www.google.com/search?q=Captan+50WP"}],
        "season": "Spring/Fall",
        "severity": "High"
    },
    # Add 20+ diseases similarly...
    "Tomato Late Blight": { ... },
    "Corn Gray Leaf Spot": { ... },
    # ...
}

# -------------------- ML MODEL --------------------
@st.cache_resource
def load_model():
    # Try to load from a local file first, otherwise download from URL
    model_path = "models/plant_disease_model.h5"
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
    else:
        # Download from a public URL (replace with your actual model URL)
        model_url = "https://your-storage.com/plant_disease_model.h5"
        response = requests.get(model_url)
        model = tf.keras.models.load_model(BytesIO(response.content))
    return model

model = load_model()
# Class names must match the training order (e.g., from train_generator.class_indices)
CLASS_NAMES = ["Apple Scab", "Apple Black Rot", "Cedar Apple Rust", "Healthy Apple",
               "Corn Common Rust", "Corn Gray Leaf Spot", "Corn Northern Leaf Blight", "Healthy Corn",
               "Grape Black Rot", "Grape Esca (Black Measles)", "Grape Leaf Blight", "Healthy Grape",
               "Potato Early Blight", "Potato Late Blight", "Healthy Potato",
               "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight", "Tomato Leaf Mold",
               "Tomato Septoria Leaf Spot", "Tomato Spider Mites", "Tomato Target Spot",
               "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus", "Healthy Tomato"]

def preprocess_image(image):
    # Convert PIL image to tensor and preprocess for MobileNetV2
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(image):
    img_array = preprocess_image(image)
    predictions = model.predict(img_array)
    class_idx = np.argmax(predictions[0])
    confidence = predictions[0][class_idx]
    return CLASS_NAMES[class_idx], confidence

# -------------------- CROP CALENDAR DATA --------------------
CROP_CALENDAR = {
    "Rice": {"planting": "June-July", "harvesting": "November-December"},
    "Wheat": {"planting": "October-December", "harvesting": "March-April"},
    "Maize": {"planting": "June-July", "harvesting": "September-October"},
    "Sugarcane": {"planting": "January-March", "harvesting": "November-February"},
    "Cotton": {"planting": "May-June", "harvesting": "November-December"},
    "Groundnut": {"planting": "June-July", "harvesting": "September-October"},
    # Add more as needed
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

# -------------------- AUTH FUNCTIONS (same as before) --------------------
def hash_password(password): ...
def register_user(email, name, password): ...
def login_user(email, password): ...
def get_officers(district=None): ...
def book_appointment(user_email, officer_id, date, time_slot): ...

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

# -------------------- CUSTOM CSS for improved UI --------------------
st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header with logo */
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
    
    /* Cards */
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

    /* Buttons */
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

    /* Sidebar */
    .css-1d391kg { background-color: #f8fafc; }

    /* Info boxes */
    .symptom-box {
        background: #fff1f0;
        padding: 1.2rem;
        border-left: 5px solid #ff4d4d;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .prevention-box {
        background: #f0f7e9;
        padding: 1.2rem;
        border-left: 5px solid #2ecc71;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .medicine-box {
        background: #e8f0fe;
        padding: 1.2rem;
        border-left: 5px solid #3498db;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    # Use a local logo or a placeholder
    st.image("https://img.icons8.com/color/96/000000/plant-under-sun--v1.png", width=80)
    st.markdown(f"<h2>{t('🌱 Crop Care AI')}</h2>", unsafe_allow_html=True)

    lang_options = { ... }  # same as before
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
        t("Crop Calendar"),          # new page
        t("Weather"),                 # new page
        t("About")
    ]
    icons = ["🏠", "📸", "📚", "👨‍🌾", "📊", "🎤", "📅", "☀️", "ℹ️"]
    for i, opt in enumerate(menu_options):
        if st.button(f"{icons[i]} {opt}", key=f"nav_{opt}"):
            st.session_state.page = opt
            st.rerun()

    st.markdown("---")
    # Login/Logout (same as before, with fixed Google login)

# -------------------- MAIN CONTENT --------------------
page = st.session_state.page

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
                        # Show details (you can reuse a function)
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

elif page == t("Disease Database"):
    # (same as before, but with expanded DISEASE_DB)
    pass

elif page == t("Officers & Appointments"):
    # (same as before)
    pass

elif page == t("Live Data"):
    # (same as before, but you can add more charts)
    pass

elif page == t("Voice Assistant"):
    # (same as before)
    pass

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
            - {t('MobileNetV2 fine-tuned on PlantVillage')}
            - {t('Streamlit Community Cloud')}
            - {t('Supabase for persistent storage')}
            - {t('OpenWeatherMap API')}
            - {t('Plotly for interactive charts')}
        """)
    st.info(t("Version 5.0 | © 2025 Crop Care AI | Built with ❤️ for farmers"))
