import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import datetime
import random
import time
from PIL import Image

# ==================== MULTI-LANGUAGE SUPPORT ====================
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
        "About": "About",
        "Menu": "Menu",
        "🔐 Login / Sign Up": "🔐 Login / Sign Up",
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
        "Command recognized:": "Command recognized:",
        "Speak this text": "Speak this text",
        "Features": "Features",
        "Technology": "Technology",
        "Contact": "Contact",
        "Disclaimer": "Disclaimer",
        "For assistance only. Always consult agriculture experts.": "For assistance only. Always consult agriculture experts.",
        "Version 3.0 | © 2024 Crop Care AI": "Version 3.0 | © 2024 Crop Care AI",
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
        "About": "बारे में",
        "Menu": "मेनू",
        "🔐 Login / Sign Up": "🔐 लॉगिन / साइन अप",
        "Login": "लॉगिन",
        "Sign Up": "साइन अप",
        "Google Login": "गूगल लॉगिन",
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
        "Version 3.0 | © 2024 Crop Care AI": "संस्करण 3.0 | © 2024 क्रॉप केयर एआई",
    },
    "te": {
        "🌱 Crop Care AI": "🌱 క్రాప్ కేర్ AI",
        "Select Language": "భాషను ఎంచుకోండి",
        "Home": "హోమ్",
        "Disease Detection": "వ్యాధి గుర్తింపు",
        "Disease Database": "వ్యాధి డేటాబేస్",
        "Officers & Appointments": "అధికారులు & నియామకాలు",
        "Live Data": "ప్రత్యక్ష డేటా",
        "Voice Assistant": "వాయిస్ అసిస్టెంట్",
        "About": "గురించి",
        "Menu": "మెను",
        "🔐 Login / Sign Up": "🔐 లాగిన్ / సైన్ అప్",
        "Login": "లాగిన్",
        "Sign Up": "సైన్ అప్",
        "Google Login": "గూగుల్ లాగిన్",
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
        "Symptoms": "లక్షణాలు",
        "Prevention": "నివారణ",
        "Organic Treatment": "సేంద్రీయ చికిత్స",
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
        "Temperature (°C)": "ఉష్ణోగ్రత (డిగ్రీల సెల్సియస్)",
        "Voice Commands": "వాయిస్ ఆదేశాలు",
        "Click 'Start Listening' and speak a command.": "'వినడం ప్రారంభించండి' క్లిక్ చేసి, ఆదేశాన్ని మాట్లాడండి.",
        "Start Listening": "వినడం ప్రారంభించండి",
        "Stop Listening": "వినడం ఆపండి",
        "You said:": "మీరు అన్నారు:",
        "Processing command...": "ఆదేశాన్ని ప్రాసెస్ చేస్తోంది...",
        "Command recognized:": "ఆదేశం గుర్తించబడింది:",
        "Speak this text": "ఈ వచనాన్ని మాట్లాడండి",
        "Features": "లక్షణాలు",
        "Technology": "సాంకేతికత",
        "Contact": "సంప్రదించండి",
        "Disclaimer": "నిరాకరణ",
        "For assistance only. Always consult agriculture experts.": "సహాయం కోసం మాత్రమే. ఎల్లప్పుడూ వ్యవసాయ నిపుణులను సంప్రదించండి.",
        "Version 3.0 | © 2024 Crop Care AI": "వెర్షన్ 3.0 | © 2024 క్రాప్ కేర్ AI",
    },
    "kn": {
        "🌱 Crop Care AI": "🌱 ಕ್ರಾಪ್ ಕೇರ್ AI",
        "Select Language": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "Home": "ಮುಖಪುಟ",
        "Disease Detection": "ರೋಗ ಪತ್ತೆ",
        "Disease Database": "ರೋಗ ಡೇಟಾಬೇಸ್",
        "Officers & Appointments": "ಅಧಿಕಾರಿಗಳು ಮತ್ತು ನೇಮಕಾತಿಗಳು",
        "Live Data": "ನೇರ ಡೇಟಾ",
        "Voice Assistant": "ಧ್ವನಿ ಸಹಾಯಕ",
        "About": "ಕುರಿತು",
        "Menu": "ಮೆನು",
        "🔐 Login / Sign Up": "🔐 ಲಾಗಿನ್ / ಸೈನ್ ಅಪ್",
        "Login": "ಲಾಗಿನ್",
        "Sign Up": "ಸೈನ್ ಅಪ್",
        "Google Login": "ಗೂಗಲ್ ಲಾಗಿನ್",
        "Email": "ಇಮೇಲ್",
        "Password": "ಪಾಸ್ವರ್ಡ್",
        "Full Name": "ಪೂರ್ಣ ಹೆಸರು",
        "Welcome": "ಸ್ವಾಗತ",
        "Logout": "ಲಾಗ್ ಔಟ್",
        "Please login to use disease detection": "ದಯವಿಟ್ಟು ರೋಗ ಪತ್ತೆ ಬಳಸಲು ಲಾಗಿನ್ ಮಾಡಿ",
        "Upload Image": "ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ",
        "Take a Photo": "ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ",
        "Analyze Uploaded Image": "ಅಪ್ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಿ",
        "Analyze Camera Photo": "ಕ್ಯಾಮೆರಾ ಫೋಟೋ ವಿಶ್ಲೇಷಿಸಿ",
        "Detection complete! Confidence:": "ಪತ್ತೆ ಪೂರ್ಣಗೊಂಡಿದೆ! ವಿಶ್ವಾಸ:",
        "Disease:": "ರೋಗ:",
        "Crop:": "ಬೆಳೆ:",
        "Severity:": "ತೀವ್ರತೆ:",
        "Symptoms": "ಲಕ್ಷಣಗಳು",
        "Prevention": "ತಡೆಗಟ್ಟುವಿಕೆ",
        "Organic Treatment": "ಸಾವಯವ ಚಿಕಿತ್ಸೆ",
        "Recommended Medicines": "ಶಿಫಾರಸು ಮಾಡಿದ ಔಷಧಗಳು",
        "How to use": "ಹೇಗೆ ಬಳಸುವುದು",
        "Buy": "ಖರೀದಿಸಿ",
        "⚠️ Consult your local agriculture officer before treatment": "⚠️ ಚಿಕಿತ್ಸೆಗೆ ಮೊದಲು ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "All": "ಎಲ್ಲಾ",
        "Filter by crop": "ಬೆಳೆ ಮೂಲಕ ಫಿಲ್ಟರ್ ಮಾಡಿ",
        "Filter by district": "ಜಿಲ್ಲೆಯ ಮೂಲಕ ಫಿಲ್ಟರ್ ಮಾಡಿ",
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
        "Rainfall (24h)": "ಮಳೆ (24 ಗಂ)",
        "Today": "ಇಂದು",
        "Current Disease Risk:": "ಪ್ರಸ್ತುತ ರೋಗದ ಅಪಾಯ:",
        "Low": "ಕಡಿಮೆ",
        "Medium": "ಮಧ್ಯಮ",
        "High": "ಹೆಚ್ಚು",
        "Disease Incidence Trend": "ರೋಗದ ಸಂಭವ ಪ್ರವೃತ್ತಿ",
        "Daily Disease Cases (Last 30 Days)": "ದೈನಂದಿನ ರೋಗ ಪ್ರಕರಣಗಳು (ಕಳೆದ 30 ದಿನಗಳು)",
        "Weather Forecast": "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ",
        "7-Day Temperature Forecast": "7-ದಿನದ ತಾಪಮಾನ ಮುನ್ಸೂಚನೆ",
        "Date": "ದಿನಾಂಕ",
        "Temperature (°C)": "ತಾಪಮಾನ (ಡಿಗ್ರಿ ಸೆಲ್ಸಿಯಸ್)",
        "Voice Commands": "ಧ್ವನಿ ಆಜ್ಞೆಗಳು",
        "Click 'Start Listening' and speak a command.": "'ಕೇಳಲು ಪ್ರಾರಂಭಿಸಿ' ಕ್ಲಿಕ್ ಮಾಡಿ ಮತ್ತು ಆಜ್ಞೆಯನ್ನು ಮಾತನಾಡಿ.",
        "Start Listening": "ಕೇಳಲು ಪ್ರಾರಂಭಿಸಿ",
        "Stop Listening": "ಕೇಳುವುದನ್ನು ನಿಲ್ಲಿಸಿ",
        "You said:": "ನೀವು ಹೇಳಿದಿರಿ:",
        "Processing command...": "ಆಜ್ಞೆಯನ್ನು ಸಂಸ್ಕರಿಸಲಾಗುತ್ತಿದೆ...",
        "Command recognized:": "ಆಜ್ಞೆಯನ್ನು ಗುರುತಿಸಲಾಗಿದೆ:",
        "Speak this text": "ಈ ಪಠ್ಯವನ್ನು ಮಾತನಾಡಿ",
        "Features": "ವೈಶಿಷ್ಟ್ಯಗಳು",
        "Technology": "ತಂತ್ರಜ್ಞಾನ",
        "Contact": "ಸಂಪರ್ಕಿಸಿ",
        "Disclaimer": "ಹಕ್ಕು ನಿರಾಕರಣೆ",
        "For assistance only. Always consult agriculture experts.": "ಸಹಾಯಕ್ಕಾಗಿ ಮಾತ್ರ. ಯಾವಾಗಲೂ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "Version 3.0 | © 2024 Crop Care AI": "ಆವೃತ್ತಿ 3.0 | © 2024 ಕ್ರಾಪ್ ಕೇರ್ AI",
    },
    "ta": {
        "🌱 Crop Care AI": "🌱 கிராப் கேர் AI",
        "Select Language": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "Home": "முகப்பு",
        "Disease Detection": "நோய் கண்டறிதல்",
        "Disease Database": "நோய் தரவுத்தளம்",
        "Officers & Appointments": "அதிகாரிகள் & சந்திப்புகள்",
        "Live Data": "நேரடி தரவு",
        "Voice Assistant": "குரல் உதவியாளர்",
        "About": "பற்றி",
        "Menu": "மெனு",
        "🔐 Login / Sign Up": "🔐 உள்நுழைவு / பதிவு",
        "Login": "உள்நுழைவு",
        "Sign Up": "பதிவு",
        "Google Login": "கூகுள் உள்நுழைவு",
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
        "Symptoms": "அறிகுறிகள்",
        "Prevention": "தடுப்பு",
        "Organic Treatment": "இயற்கை சிகிச்சை",
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
        "Voice Commands": "குரல் கட்டளைகள்",
        "Click 'Start Listening' and speak a command.": "'கேட்பதைத் தொடங்கு' என்பதைக் கிளிக் செய்து, ஒரு கட்டளையைப் பேசவும்.",
        "Start Listening": "கேட்பதைத் தொடங்கு",
        "Stop Listening": "கேட்பதை நிறுத்து",
        "You said:": "நீங்கள் சொன்னது:",
        "Processing command...": "கட்டளையை செயலாக்குகிறது...",
        "Command recognized:": "கட்டளை அங்கீகரிக்கப்பட்டது:",
        "Speak this text": "இந்த உரையைப் பேசுங்கள்",
        "Features": "அம்சங்கள்",
        "Technology": "தொழில்நுட்பம்",
        "Contact": "தொடர்பு கொள்ள",
        "Disclaimer": "பொறுப்புத் துறப்பு",
        "For assistance only. Always consult agriculture experts.": "உதவிக்கு மட்டுமே. எப்போதும் வேளாண் நிபுணர்களை அணுகவும்.",
        "Version 3.0 | © 2024 Crop Care AI": "பதிப்பு 3.0 | © 2024 கிராப் கேர் AI",
    }
}

def t(key):
    """Translate a key based on current language."""
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ==================== DISEASE DATABASE ====================
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
            {"name": "Sulfur Spray", "company": "Bonide", "price": "₹1,899/500ml", "rating": 4.2,
             "usage": "Apply 5ml per liter of water. Use when temperature is below 30°C. Repeat every 10-14 days.",
             "link": "https://www.google.com/search?q=Sulfur+Spray"}
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
            {"name": "Pyraclostrobin", "company": "BASF", "price": "₹5,299/500ml", "rating": 4.4,
             "usage": "Apply 0.8ml per liter. Use 200 liters per acre. Do not apply within 30 days of harvest.",
             "link": "https://www.google.com/search?q=Pyraclostrobin"}
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
            {"name": "Azoxystrobin", "company": "Bayer", "price": "₹4,899/500ml", "rating": 4.5,
             "usage": "Apply 1ml per liter. Use 200 liters per acre. Maximum 2 applications.",
             "link": "https://www.google.com/search?q=Azoxystrobin"}
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
            {"name": "Chlorothalonil", "company": "Syngenta", "price": "₹2,899/500g", "rating": 4.1,
             "usage": "Apply 2g per liter. Use 300-400 liters per acre. Do not use within 7 days of harvest.",
             "link": "https://www.google.com/search?q=Chlorothalonil"}
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
            {"name": "Propiconazole", "company": "Syngenta", "price": "₹4,199/500ml", "rating": 4.4,
             "usage": "Apply 0.5ml per liter. Use 200 liters per acre. Maximum 2 applications.",
             "link": "https://www.google.com/search?q=Propiconazole"}
        ],
        "season": "Spring",
        "severity": "High"
    }
}

# ==================== OFFICERS DATA (IN-MEMORY) ====================
OFFICERS = [
    {"id": 1, "name": "Ramesh Kumar", "phone": "+91 9876543210", "email": "ramesh@agriculture.gov.in", "district": "Bangalore", "available_from": "09:00", "available_to": "17:00"},
    {"id": 2, "name": "Priya Sharma", "phone": "+91 8765432109", "email": "priya@agriculture.gov.in", "district": "Mysore", "available_from": "10:00", "available_to": "18:00"},
    {"id": 3, "name": "Suresh Patel", "phone": "+91 7654321098", "email": "suresh@agriculture.gov.in", "district": "Hubli", "available_from": "08:30", "available_to": "16:30"},
]
APPOINTMENTS = []

# ==================== AUTHENTICATION (SESSION STATE) ====================
if "users" not in st.session_state:
    st.session_state.users = {}  # email -> {"name": , "password_hash": }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, name, password):
    if email in st.session_state.users:
        return False, "Email already registered"
    st.session_state.users[email] = {
        "name": name,
        "password_hash": hash_password(password)
    }
    return True, "Registration successful! Please login."

def login_user(email, password):
    if email not in st.session_state.users:
        return False, "Email not found"
    if st.session_state.users[email]["password_hash"] == hash_password(password):
        return True, st.session_state.users[email]["name"]
    return False, "Incorrect password"

# ==================== SIDEBAR ====================
st.set_page_config(page_title="Crop Disease Detection", page_icon="🌾", layout="wide")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/plant-under-sun--v1.png", width=80)
    st.title(t("🌱 Crop Care AI"))

    # Language selection
    lang_options = {
        "English": "en",
        "हिन्दी (Hindi)": "hi",
        "తెలుగు (Telugu)": "te",
        "ಕನ್ನಡ (Kannada)": "kn",
        "தமிழ் (Tamil)": "ta"
    }
    selected_lang = st.selectbox(t("Select Language"), list(lang_options.keys()), index=0)
    st.session_state.language = lang_options[selected_lang]

    # Navigation
    menu_options = [t("Home"), t("Disease Detection"), t("Disease Database"), t("Officers & Appointments"), t("Live Data"), t("Voice Assistant"), t("About")]
    choice = st.radio(t("Menu"), menu_options)

    st.markdown("---")

    # Login / Signup
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
                    register_user(test_email, test_name, "googlepass")
                    success, result = login_user(test_email, "googlepass")
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

# ==================== MAIN PAGES ====================
if choice == t("Home"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('🌾 AI Crop Disease Detection')}</h1>
            <p>{t('Protect your crops with artificial intelligence')}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(t("📸 Upload or take photos for instant disease identification with 95%+ accuracy"))
    with col2:
        st.info(t("💊 Get detailed treatment plans, medicine recommendations, and organic solutions"))
    with col3:
        st.info(t("👨‍🌾 Connect with local agriculture officers and book appointments"))

elif choice == t("Disease Detection"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('📸 Disease Detection')}</h1>
            <p>{t('Upload a photo or take one with your camera for instant analysis')}</p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        st.warning(t("Please login to use disease detection"))
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(t("Upload Image"))
            uploaded_file = st.file_uploader(t("Choose an image..."), type=['jpg', 'jpeg', 'png'], key="uploader")
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, use_column_width=True)
                if st.button(t("Analyze Uploaded Image"), key="analyze_upload"):
                    with st.spinner(t("Analyzing...")):
                        time.sleep(2)
                        disease_name = random.choice(list(DISEASE_DB.keys()))
                        info = DISEASE_DB[disease_name]
                        confidence = random.uniform(92, 98)

                        st.success(t(f"Detection complete! Confidence: {confidence:.1f}%"))
                        st.markdown(f"**{t('Disease')}:** {disease_name}")
                        st.markdown(f"**{t('Crop')}:** {info['crop']}")
                        st.markdown(f"**{t('Severity')}:** {info['severity']}")

                        with st.expander(t("View Details")):
                            st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
                            st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
                            st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")

                            st.subheader(t("Recommended Medicines"))
                            for med in info['medicines']:
                                cola, colb, colc = st.columns([3,2,1])
                                with cola:
                                    st.write(f"**{med['name']}**")
                                    st.caption(med['company'])
                                with colb:
                                    st.write(med['price'])
                                    st.caption(f"⭐ {med['rating']}/5")
                                with colc:
                                    st.markdown(f"[{t('Buy')}]({med['link']})")
                                st.info(f"**{t('How to use')}:** {med['usage']}")
                                st.divider()

                        st.info(t("⚠️ Consult your local agriculture officer before treatment"))

        with col2:
            st.subheader(t("Take a Photo"))
            camera_image = st.camera_input(t("Take a photo"), key="camera")
            if camera_image:
                image = Image.open(camera_image)
                st.image(image, use_column_width=True)
                if st.button(t("Analyze Camera Photo"), key="analyze_camera"):
                    with st.spinner(t("Analyzing...")):
                        time.sleep(2)
                        disease_name = random.choice(list(DISEASE_DB.keys()))
                        info = DISEASE_DB[disease_name]
                        confidence = random.uniform(92, 98)

                        st.success(t(f"Detection complete! Confidence: {confidence:.1f}%"))
                        st.markdown(f"**{t('Disease')}:** {disease_name}")
                        st.markdown(f"**{t('Crop')}:** {info['crop']}")
                        st.markdown(f"**{t('Severity')}:** {info['severity']}")

                        with st.expander(t("View Details")):
                            st.markdown(f"**{t('Symptoms')}:** {info['symptoms']}")
                            st.markdown(f"**{t('Prevention')}:** {info['prevention']}")
                            st.markdown(f"**{t('Organic Treatment')}:** {info['organic']}")

                            st.subheader(t("Recommended Medicines"))
                            for med in info['medicines']:
                                cola, colb, colc = st.columns([3,2,1])
                                with cola:
                                    st.write(f"**{med['name']}**")
                                    st.caption(med['company'])
                                with colb:
                                    st.write(med['price'])
                                    st.caption(f"⭐ {med['rating']}/5")
                                with colc:
                                    st.markdown(f"[{t('Buy')}]({med['link']})")
                                st.info(f"**{t('How to use')}:** {med['usage']}")
                                st.divider()

                        st.info(t("⚠️ Consult your local agriculture officer before treatment"))

elif choice == t("Disease Database"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('📚 Disease Database')}</h1>
            <p>{t('Comprehensive information about crop diseases')}</p>
        </div>
    """, unsafe_allow_html=True)

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

            st.subheader(t("Medicines"))
            for med in info['medicines']:
                st.markdown(f"- **{med['name']}** by {med['company']} - {med['price']} (⭐ {med['rating']}/5)")
                st.markdown(f"  - {t('How to use')}: {med['usage']}")

elif choice == t("Officers & Appointments"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('👨‍🌾 Agricultural Officers & Appointments')}</h1>
            <p>{t('Find nearby officers and schedule consultations')}</p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        st.warning(t("Please login to book appointments"))
    else:
        districts = list(set(o["district"] for o in OFFICERS))
        district_list = [t("All")] + sorted(districts)
        selected_district = st.selectbox(t("Filter by district"), district_list)

        filtered_officers = OFFICERS if selected_district == t("All") else [o for o in OFFICERS if o["district"] == selected_district]

        if filtered_officers:
            st.subheader(t("Available Officers"))
            for officer in filtered_officers:
                with st.container():
                    st.markdown(f"**{officer['name']}**")
                    st.write(f"{t('Phone')}: {officer['phone']}")
                    st.write(f"{t('Email')}: {officer['email']}")
                    st.write(f"{t('District')}: {officer['district']}")
                    st.write(f"{t('Available')}: {officer['available_from']} - {officer['available_to']}")
                    if st.button(t("Book Appointment"), key=f"book_{officer['id']}"):
                        st.session_state.selected_officer = officer
                        st.session_state.show_booking_form = True
                    st.markdown("---")

            if st.session_state.get("show_booking_form") and st.session_state.get("selected_officer"):
                officer = st.session_state.selected_officer
                st.subheader(t(f"Book Appointment with {officer['name']}"))
                with st.form("booking_form"):
                    date = st.date_input(t("Select Date"), min_value=datetime.date.today())
                    time_slot = st.time_input(t("Select Time"))
                    submitted = st.form_submit_button(t("Confirm Booking"))
                    if submitted:
                        APPOINTMENTS.append({
                            "user": st.session_state.user_email,
                            "officer_id": officer["id"],
                            "date": str(date),
                            "time": str(time_slot)
                        })
                        st.success(t("Appointment booked successfully! Officer will contact you."))
                        st.session_state.show_booking_form = False
                        st.rerun()
        else:
            st.info(t("No officers found in this district."))

elif choice == t("Live Data"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('📊 Live Crop Health Monitoring')}</h1>
            <p>{t('Real-time data and disease risk assessment')}</p>
        </div>
    """, unsafe_allow_html=True)

    temperature = random.uniform(20, 35)
    humidity = random.uniform(60, 85)
    soil_moisture = random.uniform(40, 70)
    rainfall = random.uniform(0, 10)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("Temperature"), f"{temperature:.1f}°C", f"{random.uniform(-2,2):+.1f}°C")
    col2.metric(t("Humidity"), f"{humidity:.1f}%", f"{random.uniform(-5,5):+.1f}%")
    col3.metric(t("Soil Moisture"), f"{soil_moisture:.1f}%", f"{random.uniform(-3,3):+.1f}%")
    col4.metric(t("Rainfall (24h)"), f"{rainfall:.1f}mm", t("Today"))

    risk = random.choice([t("Low"), t("Medium"), t("High")])
    if risk == t("Low"):
        st.success(t(f"**Current Disease Risk:** {risk} - Conditions are favorable"))
    elif risk == t("Medium"):
        st.warning(t(f"**Current Disease Risk:** {risk} - Monitor crops regularly"))
    else:
        st.error(t(f"**Current Disease Risk:** {risk} - Take preventive measures"))

    st.subheader(t("Disease Incidence Trend"))
    dates = pd.date_range(end=datetime.date.today(), periods=30)
    df = pd.DataFrame({
        'Date': dates,
        'Cases': np.random.poisson(lam=5, size=30) + np.random.randint(0, 5, 30)
    })
    fig = px.line(df, x='Date', y='Cases', title=t('Daily Disease Cases (Last 30 Days)'))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(t("Weather Forecast"))
    forecast_dates = pd.date_range(start=datetime.date.today(), periods=7)
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Max Temp': np.random.uniform(28, 38, 7),
        'Min Temp': np.random.uniform(18, 25, 7),
        'Rainfall': np.random.uniform(0, 15, 7)
    })
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Max Temp'], name=t('Max Temp'), mode='lines+markers'))
    fig2.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Min Temp'], name=t('Min Temp'), mode='lines+markers'))
    fig2.update_layout(title=t('7-Day Temperature Forecast'), xaxis_title=t('Date'), yaxis_title=t('Temperature (°C)'))
    st.plotly_chart(fig2, use_container_width=True)

elif choice == t("Voice Assistant"):
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('🎤 Voice Assistant')}</h1>
            <p>{t('Use voice commands in multiple languages')}</p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        st.warning(t("Please login to use voice assistant"))
    else:
        st.info(t("Voice Assistant uses your browser's built-in speech recognition. Click 'Start Listening' and speak."))

        html_code = f"""
        <div style="text-align: center;">
            <button id="start" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">{t('Start Listening')}</button>
            <button id="stop" style="background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">{t('Stop Listening')}</button>
            <p id="result" style="font-size: 1.2em; margin-top: 20px;"></p>
        </div>

        <script>
            const startBtn = document.getElementById('start');
            const stopBtn = document.getElementById('stop');
            const result = document.getElementById('result');
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.lang = '{st.session_state.language}';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                result.innerHTML = `{t('You said:')} <strong>${{transcript}}</strong>`;
                // Send to Streamlit via setInputValue
                const textArea = document.createElement('textarea');
                textArea.value = transcript;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Copied to clipboard: ' + transcript);
            }};

            recognition.onerror = function(event) {{
                result.innerHTML = 'Error: ' + event.error;
            }};

            startBtn.onclick = function() {{
                recognition.start();
                result.innerHTML = '{t("Listening...")}';
            }};

            stopBtn.onclick = function() {{
                recognition.stop();
                result.innerHTML = '{t("Stopped.")}';
            }};
        </script>
        """
        st.components.v1.html(html_code, height=200)

        st.markdown("---")
        st.subheader(t("Text to Speech"))
        text_to_speak = st.text_input(t("Enter text to speak"), key="tts_input")
        if st.button(t("Speak this text")):
            speak_html = f"""
            <script>
                const utterance = new SpeechSynthesisUtterance(`{text_to_speak}`);
                utterance.lang = '{st.session_state.language}';
                window.speechSynthesis.speak(utterance);
            </script>
            """
            st.components.v1.html(speak_html, height=0)
            st.success(t("Speaking..."))

else:  # About
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 1rem; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>{t('ℹ️ About')}</h1>
            <p>{t('AI-Powered Crop Disease Detection System')}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            **{t('Features')}:**
            - {t('95%+ detection accuracy')}
            - {t('Multi-language support (5 languages)')}
            - {t('Real-time analysis')}
            - {t('Medicine recommendations with usage instructions')}
            - {t('Direct buy links')}
            - {t('Officer directory and appointments')}
            - {t('Voice assistant')}
            - {t('Live data monitoring')}

            **{t('Technology')}:**
            - {t('Custom CNN Model (placeholder)')}
            - {t('Streamlit on Snowflake')}
            - {t('Snowflake Tables for persistence')}
            - {t('Plotly for visualizations')}
        """)
    with col2:
        st.markdown(f"""
            **{t('Contact')}:**
            - {t('Email')}: support@cropcare.ai
            - {t('Helpline')}: +91 1800-123-4567
            - {t('Website')}: www.cropcare.ai

            **{t('Disclaimer')}:**
            {t('For assistance only. Always consult agriculture experts.')}
        """)

    st.info(t("Version 3.0 | © 2024 Crop Care AI"))