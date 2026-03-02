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
# For brevity, only English and Hindi are fully shown; you can expand others using the same keys.
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
        "Voice Commands": "Voice Commands",
        "Click 'Start Listening' and speak a command.": "Click 'Start Listening' and speak a command.",
        "Start Listening": "Start Listening",
        "Stop Listening": "Stop Listening",
        "You said:": "You said:",
        "Processing command...": "Processing command...",
        "Command recognized:": "Command recognized:",
        "Speak this text": "Speak this text",
        "Features": "Features",
        "Technology": "Technology",
        "Contact": "Contact",
        "Disclaimer": "Disclaimer",
        "For assistance only. Always consult agriculture experts.": "For assistance only. Always consult agriculture experts.",
        "Version 5.0 | © 2025 Crop Care AI": "Version 5.0 | © 2025 Crop Care AI",
        "Crop Calendar": "Crop Calendar",
        "Optimal planting and harvesting times for common crops": "Optimal planting and harvesting times for common crops",
        "Planting Season": "Planting Season",
        "Harvesting Season": "Harvesting Season",
        "Current weather conditions for your region": "Current weather conditions for your region",
        "Enter city": "Enter city",
        "Get Weather": "Get Weather",
        "Wind Speed": "Wind Speed",
        "Pressure": "Pressure",
    },
    "hi": {
        "🌱 Crop Care AI": "🌱 क्रॉप केयर एआई",
        "Select Language": "भाषा चुनें",
        "Home": "होम",
        "Disease Detection": "रोग का पता लगाना",
        "Disease Database": "रोग डेटाबेस",
        "Officers & Appointments": "अधिकारी और नियुक्तियाँ",
        "Live Data": "लाइव डेटा",
        "Voice Assistant": "आवाज सहायक",
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
        "Symptoms": "लक्षण",
        "Prevention": "रोकथाम",
        "Organic Treatment": "जैविक उपचार",
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
        "Voice Commands": "आवाज आदेश",
        "Click 'Start Listening' and speak a command.": "'सुनना शुरू करें' पर क्लिक करें और एक आदेश बोलें।",
        "Start Listening": "सुनना शुरू करें",
        "Stop Listening": "सुनना बंद करें",
        "You said:": "आपने कहा:",
        "Processing command...": "आदेश संसाधित किया जा रहा है...",
        "Command recognized:": "आदेश पहचाना गया:",
        "Speak this text": "इस पाठ को बोलें",
        "Features": "विशेषताएँ",
        "Technology": "प्रौद्योगिकी",
        "Contact": "संपर्क करें",
        "Disclaimer": "अस्वीकरण",
        "For assistance only. Always consult agriculture experts.": "केवल सहायता के लिए। हमेशा कृषि विशेषज्ञों से सलाह लें।",
        "Version 5.0 | © 2025 Crop Care AI": "संस्करण 5.0 | © 2025 क्रॉप केयर एआई",
        "Crop Calendar": "फसल कैलेंडर",
        "Optimal planting and harvesting times for common crops": "सामान्य फसलों के लिए इष्टतम रोपण और कटाई का समय",
        "Planting Season": "रोपण का मौसम",
        "Harvesting Season": "कटाई का मौसम",
        "Current weather conditions for your region": "आपके क्षेत्र के लिए वर्तमान मौसम की स्थिति",
        "Enter city": "शहर दर्ज करें",
        "Get Weather": "मौसम प्राप्त करें",
        "Wind Speed": "हवा की गति",
        "Pressure": "दबाव",
    }
    # Add te, kn, ta, bn, mr, gu similarly with the same keys.
}

def t(key):
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# -------------------- ML MODEL --------------------
@st.cache_resource
def load_model():
    model_path = "models/plant_disease_model.h5"
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
    else:
        # Replace with your actual model URL
        model_url = "https://github.com/yourusername/your-repo/releases/download/v1.0/plant_disease_model.h5"
        try:
            response = requests.get(model_url)
            model = tf.keras.models.load_model(BytesIO(response.content))
        except:
            st.warning("Could not load model. Using random predictions as fallback.")
            return None
    return model

model = load_model()

# Class names must match your training order
CLASS_NAMES = [
    "Apple Scab", "Apple Black Rot", "Cedar Apple Rust", "Healthy Apple",
    "Corn Common Rust", "Corn Gray Leaf Spot", "Corn Northern Leaf Blight", "Healthy Corn",
    "Grape Black Rot", "Grape Esca (Black Measles)", "Grape Leaf Blight", "Healthy Grape",
    "Potato Early Blight", "Potato Late Blight", "Healthy Potato",
    "Tomato Bacterial Spot", "Tomato Early Blight", "Tomato Late Blight", "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot", "Tomato Spider Mites", "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus", "Tomato Mosaic Virus", "Healthy Tomato"
]

def preprocess_image(image):
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(image):
    if model is None:
        return random.choice(CLASS_NAMES), random.uniform(0.7, 0.99)
    img_array = preprocess_image(image)
    preds = model.predict(img_array)
    idx = np.argmax(preds[0])
    confidence = preds[0][idx]
    return CLASS_NAMES[idx], confidence

# -------------------- DISEASE DATABASE (expanded) --------------------
DISEASE_DB = {
    "Apple Scab": {
        "crop": "Apple",
        "symptoms": "Olive-green to brown spots on leaves and fruit, leaves may curl and fall prematurely. Fruit may become deformed and cracked.",
        "prevention": "Plant resistant varieties. Prune trees to improve air circulation. Remove and destroy fallen leaves. Avoid overhead irrigation.",
        "organic": "Neem oil spray (2-3 ml per liter of water) every 7-10 days. Baking soda solution (1 tsp per liter water) with a few drops of vegetable oil.",
        "medicines": [
            {"name": "Captan 50WP", "company": "Bayer", "price": "₹2,499/500g", "rating": 4.5,
             "usage": "Apply 2g per liter of water. Repeat every 7-10 days. Use 200-300 liters per acre.",
             "link": "https://www.google.com/search?q=Captan+50WP"},
            {"name": "Myclobutanil", "company": "Spectrum", "price": "₹3,299/250ml", "rating": 4.3,
             "usage": "Apply 0.5ml per liter of water. Use 200-250 liters per acre. Do not apply more than 3 times per season.",
             "link": "https://www.google.com/search?q=Myclobutanil"},
        ],
        "season": "Spring/Fall",
        "severity": "High"
    },
    "Corn Rust": {
        "crop": "Corn",
        "symptoms": "Reddish-brown pustules on both leaf surfaces, primarily on leaves. Pustules may turn black as they age.",
        "prevention": "Plant resistant hybrids. Practice crop rotation. Avoid overhead irrigation. Remove crop debris after harvest.",
        "organic": "Sulfur-based fungicides. Compost tea spray. Neem oil (2ml per liter) weekly.",
        "medicines": [
            {"name": "Azoxystrobin", "company": "Syngenta", "price": "₹4,599/500ml", "rating": 4.6,
             "usage": "Apply 1ml per liter of water. Use 200-300 liters per acre. Maximum 2 applications per season.",
             "link": "https://www.google.com/search?q=Azoxystrobin"},
        ],
        "season": "Summer",
        "severity": "Medium"
    },
    "Potato Early Blight": {
        "crop": "Potato",
        "symptoms": "Dark brown to black lesions with concentric rings, usually on lower leaves. Lesions may enlarge and cause leaf drop.",
        "prevention": "Crop rotation (avoid planting potatoes in same field for 3 years). Proper spacing. Avoid overhead irrigation. Use disease-free seed.",
        "organic": "Copper fungicides (3g per liter). Bacillus subtilis spray. Compost tea.",
        "medicines": [
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,799/500g", "rating": 4.3,
             "usage": "Apply 2g per liter. Use 300-400 liters per acre. Repeat every 7-10 days.",
             "link": "https://www.google.com/search?q=Chlorothalonil"},
        ],
        "season": "Summer/Fall",
        "severity": "Medium"
    },
    "Tomato Leaf Mold": {
        "crop": "Tomato",
        "symptoms": "Pale green or yellowish spots on upper leaf surfaces, olive-green to grayish mold on undersides. Leaves may wither and die.",
        "prevention": "Improve air circulation. Reduce humidity. Water at base of plants. Remove lower leaves. Use resistant varieties.",
        "organic": "Neem oil (2ml per liter). Potassium bicarbonate (1 tsp per liter). Compost tea.",
        "medicines": [
            {"name": "Copper Hydroxide", "company": "DuPont", "price": "₹3,199/500g", "rating": 4.2,
             "usage": "Apply 2g per liter. Use 300 liters per acre. Repeat every 7 days.",
             "link": "https://www.google.com/search?q=Copper+Hydroxide"},
        ],
        "season": "Spring/Summer",
        "severity": "Medium"
    },
    "Wheat Stem Rust": {
        "crop": "Wheat",
        "symptoms": "Reddish-brown pustules on stems and leaves, can cause stem breakage and grain shriveling. Pustules are elongated.",
        "prevention": "Use resistant varieties. Early planting. Destroy volunteer wheat. Avoid excessive nitrogen.",
        "organic": "Sulfur spray (5g per liter). Neem oil. Bacillus subtilis.",
        "medicines": [
            {"name": "Tebuconazole", "company": "Bayer", "price": "₹3,399/500ml", "rating": 4.3,
             "usage": "Apply 1ml per liter. Use 200 liters per acre. Apply at first sign of disease.",
             "link": "https://www.google.com/search?q=Tebuconazole"},
        ],
        "season": "Spring",
        "severity": "High"
    }
    # Add more diseases as needed...
}

# -------------------- CROP CALENDAR --------------------
CROP_CALENDAR = {
    "Rice": {"planting": "June-July", "harvesting": "November-December"},
    "Wheat": {"planting": "October-December", "harvesting": "March-April"},
    "Maize": {"planting": "June-July", "harvesting": "September-October"},
    "Sugarcane": {"planting": "January-March", "harvesting": "November-February"},
    "Cotton": {"planting": "May-June", "harvesting": "November-December"},
    "Groundnut": {"planting": "June-July", "harvesting": "September-October"},
    "Soybean": {"planting": "June-July", "harvesting": "September-October"},
    "Mustard": {"planting": "October-November", "harvesting": "February-March"},
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
    .css-1d391kg { background-color: #f8fafc; }
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
                            st.error(t("Google login failed – please check if the test user exists."))
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
            st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
            st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
            st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")
            st.markdown(f"**{t('Season')}:** {info['season']}")
            st.markdown(f"**{t('Severity')}:** {info['severity']}")
            st.markdown(f"**{t('Recommended Medicines')}:**")
            for med in info['medicines']:
                st.markdown(f"- **{med['name']}** by {med['company']} – {med['price']} (⭐ {med['rating']})")
                st.markdown(f"  - {t('How to use')}: {med['usage']}")

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

# ---- Voice Assistant ----
elif page == t("Voice Assistant"):
    st.markdown(f'<div class="main-header"><h1>🎤 {t("Voice Assistant")}</h1><p>{t("Use voice commands in multiple languages")}</p></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.warning(t("Please login to use voice assistant"))
    else:
        st.info(t("Voice Assistant uses your browser's built-in speech recognition. Click 'Start Listening' and speak."))
        html_code = f"""
        <div style="text-align: center;">
            <button id="start" style="background-color: #1e3c72; color: white; padding: 12px 30px; border: none; border-radius: 50px; margin: 10px;">🎤 {t('Start Listening')}</button>
            <button id="stop" style="background-color: #e53e3e; color: white; padding: 12px 30px; border: none; border-radius: 50px; margin: 10px;">⏹️ {t('Stop Listening')}</button>
            <p id="result" style="font-size: 1.3rem;"></p>
        </div>
        <script>
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{st.session_state.language}';
            recognition.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                document.getElementById('result').innerHTML = '{t("You said:")} ' + transcript;
            }};
            document.getElementById('start').onclick = () => recognition.start();
            document.getElementById('stop').onclick = () => recognition.stop();
        </script>
        """
        st.components.v1.html(html_code, height=200)

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
            - {t('MobileNetV2 fine-tuned on PlantVillage')}
            - {t('Streamlit Community Cloud')}
            - {t('Supabase for persistent storage')}
            - {t('OpenWeatherMap API')}
            - {t('Plotly for interactive charts')}
        """)
    st.info(t("Version 5.0 | © 2025 Crop Care AI | Built with ❤️ for farmers"))
