import streamlit as st
import sqlite3
import requests
import re

from datetime import datetime, date, timedelta
from urllib.parse import quote

from ai_planner import generate_ai_plan
from travel_chatbot import travel_chatbot
from hotel_recommender import recommend_hotels
from tour_guide import get_tour_guide
from transport_recommender import recommend_transport
from auth import register_user, login_user

from pathlib import Path

CSS_FILE = Path(__file__).with_name("style.css")

st.markdown(
    f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True
)

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="🌍 AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "logged_in": False,
    "username": "",
    "plan_created": False,
    "ai_plan": "",
    "location": None,
    "saved_message": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# COMMON CSS
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(59,130,246,.20), transparent 25%),
            radial-gradient(circle at 90% 20%, rgba(14,165,233,.16), transparent 25%),
            radial-gradient(circle at 50% 90%, rgba(99,102,241,.15), transparent 30%),
            linear-gradient(135deg, #020617 0%, #07111f 50%, #0b1f3a 100%);
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .stButton > button {
        border-radius: 13px;
        min-height: 48px;
        font-weight: 800;
        box-shadow: 0 10px 25px rgba(0,0,0,.20);
        transition: all .2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(0,0,0,.32);
    }

    label {
        font-weight: 650 !important;
    }

    .travel-hero {
        position: relative;
        overflow: hidden;
        border-radius: 28px;
        min-height: 350px;
        padding: 38px;
        margin-bottom: 24px;
        background:
            linear-gradient(100deg, rgba(2,6,23,.97) 0%,
            rgba(2,6,23,.76) 45%, rgba(2,6,23,.18) 100%),
            url('https://images.unsplash.com/photo-1488085061387-422e29b40080?auto=format&fit=crop&w=1800&q=85')
            center/cover;
        border: 1px solid rgba(255,255,255,.12);
        box-shadow: 0 30px 70px rgba(0,0,0,.45);
    }

    .hero-pill {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 999px;
        background: rgba(14,165,233,.18);
        border: 1px solid rgba(125,211,252,.30);
        color: #bae6fd;
        font-weight: 800;
    }

    .hero-title {
        font-size: 50px;
        font-weight: 900;
        color: white;
        line-height: 1.05;
        margin-top: 18px;
        max-width: 650px;
    }

    .hero-sub {
        font-size: 18px;
        color: #dbeafe;
        max-width: 700px;
        margin-top: 14px;
        line-height: 1.6;
    }

    .hero-plane {
        position: absolute;
        right: 8%;
        top: 14%;
        font-size: 70px;
        animation: heroPlane 7s ease-in-out infinite;
        filter: drop-shadow(0 16px 20px rgba(0,0,0,.55));
    }

    .hero-globe {
        position: absolute;
        right: 7%;
        bottom: -25px;
        font-size: 170px;
        opacity: .18;
        animation: heroGlobe 8s ease-in-out infinite;
        filter: drop-shadow(0 25px 30px rgba(0,0,0,.65));
    }

    @keyframes heroPlane {
        0%,100% { transform: translate(0,0) rotate(-10deg); }
        50% { transform: translate(-45px,-25px) rotate(-2deg); }
    }

    @keyframes heroGlobe {
        0%,100% { transform: translate(0,0) rotate(0); }
        50% { transform: translate(-18px,-18px) rotate(8deg); }
    }

    .destination-grid {
        display: grid;
        grid-template-columns: repeat(3,1fr);
        gap: 16px;
        margin: 10px 0 25px;
    }

    .destination-card {
        height: 155px;
        border-radius: 18px;
        overflow: hidden;
        position: relative;
        background-size: cover;
        background-position: center;
        box-shadow: 0 14px 30px rgba(0,0,0,.28);
        transition: transform .25s ease;
    }

    .destination-card:hover {
        transform: translateY(-5px) scale(1.01);
    }

    .destination-card:after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(transparent 25%,rgba(0,0,0,.84));
    }

    .destination-name {
        position: absolute;
        z-index: 2;
        bottom: 14px;
        left: 16px;
        color: white;
        font-size: 21px;
        font-weight: 850;
    }

    .map-strip {
        border-radius: 20px;
        padding: 18px 22px;
        margin: 10px 0 28px;
        background:
            linear-gradient(90deg,rgba(15,23,42,.95),rgba(15,23,42,.72)),
            repeating-linear-gradient(0deg,transparent 0 28px,
            rgba(56,189,248,.08) 29px 30px),
            repeating-linear-gradient(90deg,transparent 0 45px,
            rgba(56,189,248,.08) 46px 47px);
        border: 1px solid rgba(125,211,252,.14);
        color: #e0f2fe;
    }

    .login-logo {
        text-align: center;
        font-size: 80px;
        margin-top: 10px;
        animation: logoFloat 4s ease-in-out infinite;
    }

    @keyframes logoFloat {
        0%,100% { transform: translateY(0); }
        50% { transform: translateY(-9px); }
    }

    .login-title {
        text-align: center;
        color: white;
        font-size: 46px;
        font-weight: 900;
        margin-top: 5px;
    }

    .login-subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 17px;
        margin-bottom: 28px;
    }

    .feature-card {
        background: linear-gradient(145deg,rgba(255,255,255,.11),
        rgba(255,255,255,.035));
        border: 1px solid rgba(255,255,255,.13);
        border-radius: 18px;
        padding: 19px;
        margin-bottom: 14px;
        color: white;
        box-shadow: 0 15px 30px rgba(0,0,0,.25);
        transition: transform .25s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .feature-title {
        font-size: 18px;
        font-weight: 800;
    }

    .feature-text {
        color: #cbd5e1;
        font-size: 14px;
        margin-top: 5px;
    }

    .day-card {
        position: relative;
        margin: 18px 0 24px;
        padding: 24px 26px;
        border-radius: 20px;
        background: linear-gradient(145deg,
        rgba(15,23,42,.94),rgba(30,41,59,.72));
        border: 1px solid rgba(125,211,252,.16);
        box-shadow: 0 18px 40px rgba(0,0,0,.30),
        inset 0 1px 0 rgba(255,255,255,.06);
        overflow: hidden;
    }

    .day-card:before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: linear-gradient(180deg,#38bdf8,#818cf8,#22c55e);
    }

    .day-title {
        font-size: 28px;
        font-weight: 900;
        color: #f8fafc;
        margin-bottom: 16px;
    }

    .day-date {
        color: #93c5fd;
        font-size: 15px;
        font-weight: 700;
        margin-left: 8px;
    }

    .activity {
        margin: 13px 0;
        padding: 14px 16px;
        border-radius: 14px;
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.08);
        color: #e2e8f0;
        line-height: 1.55;
        transition: all .2s ease;
    }

    .activity:hover {
        transform: translateX(5px);
        background: rgba(56,189,248,.08);
    }

    @media(max-width:800px) {
        .destination-grid { grid-template-columns: 1fr; }
        .hero-title { font-size: 36px; }
        .hero-plane { font-size: 48px; }
        .hero-globe { font-size: 110px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# =========================================================
# PREMIUM TRAVEL UI OVERRIDE
# =========================================================
st.markdown(
    """
    <style>
    /* Full premium travel background */
    .stApp {
        background:
          linear-gradient(135deg, rgba(3,7,18,.94), rgba(15,23,42,.82)),
          url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=2200&q=90")
          center/cover fixed no-repeat !important;
        color: #f8fafc !important;
    }

    .main .block-container {
        max-width: 1280px !important;
        padding-top: 1.2rem !important;
    }

    /* Glass panels */
    [data-testid="stVerticalBlockBorderWrapper"],
    .feature-card,
    .day-card {
        background: rgba(15,23,42,.58) !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        box-shadow: 0 20px 55px rgba(0,0,0,.35) !important;
        backdrop-filter: blur(18px);
    }

    /* Login */
    .login-logo {
        font-size: 62px !important;
        margin-top: 15px !important;
        text-shadow: 0 8px 30px rgba(59,130,246,.45);
    }

    .login-title {
        font-size: clamp(38px,5vw,62px) !important;
        letter-spacing: -2px;
        background: linear-gradient(90deg,#fff,#93c5fd,#c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .login-subtitle {
        color: #dbeafe !important;
        font-size: 18px !important;
    }

    .feature-card {
        padding: 22px !important;
        border-radius: 22px !important;
        background: rgba(15,23,42,.48) !important;
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,.08) !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        border-radius: 14px !important;
    }

    input, textarea {
        color: white !important;
    }

    /* Gradient buttons */
    .stButton > button,
    .stLinkButton > a {
        background: linear-gradient(135deg,#2563eb,#7c3aed) !important;
        color: white !important;
        border: 0 !important;
        border-radius: 14px !important;
        min-height: 50px !important;
        font-weight: 800 !important;
        box-shadow: 0 12px 30px rgba(37,99,235,.28) !important;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover {
        transform: translateY(-2px);
        box-shadow: 0 18px 38px rgba(124,58,237,.38) !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 750 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #93c5fd !important;
    }

    /* Main hero */
    .travel-hero {
        min-height: 430px !important;
        padding: 48px !important;
        border-radius: 30px !important;
        background:
          linear-gradient(90deg,rgba(2,6,23,.96),rgba(2,6,23,.62),rgba(2,6,23,.12)),
          url("https://images.unsplash.com/photo-1527631746610-bca00a040d60?auto=format&fit=crop&w=2000&q=90")
          center/cover !important;
    }

    .hero-title {
        font-size: clamp(42px,6vw,72px) !important;
        letter-spacing: -3px;
    }

    .hero-sub {
        max-width: 760px !important;
        color: #e0e7ff !important;
    }

    .destination-card {
        border-radius: 22px !important;
    }

    .map-strip {
        background: rgba(15,23,42,.62) !important;
        backdrop-filter: blur(16px);
    }

    /* Headers and metrics */
    h1,h2,h3,h4,p,label,span {
        color: inherit;
    }

    [data-testid="stMetric"] {
        background: rgba(15,23,42,.48);
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 18px;
        padding: 14px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#020617,#0f172a) !important;
        border-right: 1px solid rgba(255,255,255,.10);
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {background:transparent !important;}

    @media(max-width:800px) {
        .travel-hero { padding: 28px !important; min-height: 380px !important; }
        .hero-title { font-size: 42px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOGIN / REGISTER
# =========================================================

if not st.session_state.logged_in:

    st.markdown('<div class="login-logo">🌍✈️</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="login-title">AI Travel Planner</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="login-subtitle">'
        'Plan smarter • Travel better • Explore the world'
        '</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🌎 Worldwide Planning</div>
                <div class="feature-text">
                    Search destinations around the world.
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-title">🤖 AI Travel Plans</div>
                <div class="feature-text">
                    Get personalized day-by-day itineraries.
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-title">🏨 Complete Assistance</div>
                <div class="feature-text">
                    Weather, maps, hotels, guides and transport.
                </div>
            </div>

            <div class="feature-card">
                <div class="feature-title">💾 Save Your Trips</div>
                <div class="feature-text">
                    Save and view your travel plans later.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        login_tab, register_tab = st.tabs(
            ["🔐 Login", "📝 Create Account"]
        )

        with login_tab:
            st.subheader("Welcome Back 👋")

            username = st.text_input(
                "👤 Username",
                key="login_username",
            )

            password = st.text_input(
                "🔒 Password",
                type="password",
                key="login_password",
            )

            if st.button("🚀 LOGIN", use_container_width=True):
                if not username.strip() or not password:
                    st.warning("⚠️ Please enter username and password.")
                else:
                    try:
                        user = login_user(
                            username.strip(),
                            password,
                        )

                        if user:
                            st.session_state.logged_in = True
                            st.session_state.username = user[1]
                            st.session_state.plan_created = False
                            st.session_state.ai_plan = ""
                            st.session_state.location = None
                            st.rerun()
                        else:
                            st.error("❌ Incorrect username or password.")
                    except Exception as error:
                        st.error("❌ Login error.")
                        st.code(str(error))

        with register_tab:
            st.subheader("Create Your Account ✨")

            new_username = st.text_input(
                "👤 Username",
                key="register_username",
            )

            new_password = st.text_input(
                "🔒 Password",
                type="password",
                key="register_password",
            )

            confirm_password = st.text_input(
                "🔒 Confirm Password",
                type="password",
                key="confirm_password",
            )

            if st.button(
                "✨ CREATE ACCOUNT",
                use_container_width=True,
            ):
                if (
                    not new_username.strip()
                    or not new_password
                    or not confirm_password
                ):
                    st.warning("⚠️ Please fill in all fields.")

                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match.")

                elif len(new_password) < 6:
                    st.warning(
                        "⚠️ Password must contain at least 6 characters."
                    )

                else:
                    try:
                        created = register_user(
                            new_username.strip(),
                            new_password,
                        )

                        if created:
                            st.success(
                                "🎉 Account created successfully!"
                            )
                            st.info(
                                "Open the Login tab and sign in."
                            )
                        else:
                            st.error("❌ Username already exists.")
                    except Exception as error:
                        st.error("❌ Registration error.")
                        st.code(str(error))

    st.caption("🌍 AI Travel Planner | Final Year Project")
    st.stop()


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("travel_planner.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        destination TEXT,
        start_date TEXT,
        days INTEGER,
        travelers INTEGER,
        budget REAL,
        interest TEXT,
        created_at TEXT
    )
    """
)

# Upgrade older database versions safely.
cursor.execute("PRAGMA table_info(trips)")
columns = [row[1] for row in cursor.fetchall()]

for column, definition in [
    ("username", "TEXT"),
    ("start_date", "TEXT"),
    ("days", "INTEGER"),
    ("travelers", "INTEGER"),
    ("budget", "REAL"),
    ("interest", "TEXT"),
    ("created_at", "TEXT"),
]:
    if column not in columns:
        try:
            cursor.execute(
                f"ALTER TABLE trips ADD COLUMN {column} {definition}"
            )
        except sqlite3.OperationalError:
            pass

conn.commit()
conn.close()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.success(
    f"👋 Welcome, {st.session_state.username}!"
)

st.sidebar.write("🌍 Worldwide Travel Planner")

if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.plan_created = False
    st.session_state.ai_plan = ""
    st.session_state.location = None
    st.rerun()


# =========================================================
# MAIN HERO
# =========================================================

st.html(
    """
    <div class="travel-hero">
        <div class="hero-pill">🌎 AI-POWERED WORLD TRAVEL</div>
        <div class="hero-title">
            Plan your next<br>great adventure ✈️
        </div>
        <div class="hero-sub">
            Discover destinations, build intelligent itineraries,
            check weather, explore maps, find hotels and transportation
            — all in one place.
        </div>
        <div class="hero-plane">✈️</div>
        <div class="hero-globe">🌍</div>
    </div>

    <div class="destination-grid">
        <div class="destination-card"
             style="background-image:url(
             'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=900&q=80')">
            <div class="destination-name">🇫🇷 Paris</div>
        </div>

        <div class="destination-card"
             style="background-image:url(
             'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=900&q=80')">
            <div class="destination-name">🇯🇵 Tokyo</div>
        </div>

        <div class="destination-card"
             style="background-image:url(
             'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=900&q=80')">
            <div class="destination-name">🇦🇪 Dubai</div>
        </div>
    </div>

    <div class="map-strip">
        🗺️ <b>WORLDWIDE EXPLORER</b>
        &nbsp; • &nbsp; 🌍 Search any destination
        &nbsp; • &nbsp; ✈️ Build your route
        &nbsp; • &nbsp; 📍 Explore the world
        </div>
    """)


# =========================================================
# TRIP INPUT
# =========================================================

st.header("🧳 Plan Your Trip")
origin = st.text_input(
    "🛫 From where are you travelling?",
    placeholder="Example: Bengaluru, Mumbai, Delhi"
)

destination = st.text_input(
    "📍 Where do you want to travel?",
    placeholder="Try: Goa, Paris, Tokyo, London, New York, Bali, Switzerland",
)

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "🗓️ When are you travelling?",
        value=date.today(),
    )

    days = st.number_input(
        "📅 Number of days",
        min_value=1,
        max_value=30,
        value=3,
        step=1,
    )

    travelers = st.number_input(
        "👥 Number of travelers",
        min_value=1,
        max_value=20,
        value=2,
        step=1,
    )

with col2:
    budget = st.number_input(
        "💰 Total budget (₹)",
        min_value=1000,
        value=50000,
        step=1000,
    )

    interests = st.multiselect(
    "❤️ What are your interests?",
    [
        "Beach",
        "Adventure",
        "Food",
        "History",
        "Nature",
        "Shopping",
        "Culture",
        "Nightlife"
    ],
    default=["Beach"]
)
    interest = ", ".join(interests)


# =========================================================
# WORLDWIDE GEOCODING
# =========================================================

@st.cache_data(ttl=3600, show_spinner=False)
def find_location(place):
    """
    Worldwide destination search.

    First uses OpenStreetMap Nominatim because it handles
    free-form worldwide searches well. If it fails, Open-Meteo
    is used as a fallback.

    Examples:
        Goa
        Goa, India
        Paris, France
        Tokyo, Japan
        New York, USA
        Bali, Indonesia
    """

    place = str(place).strip()

    if not place:
        return None

    # -----------------------------------------------------
    # Try Nominatim / OpenStreetMap first
    # -----------------------------------------------------

    nominatim_url = "https://nominatim.openstreetmap.org/search"

    nominatim_params = {
        "q": place,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 8,
        "accept-language": "en",
    }

    headers = {
        "User-Agent": "AI-Travel-Planner/1.0"
    }

    try:
        response = requests.get(
            nominatim_url,
            params=nominatim_params,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()
        results = response.json()

        if results:
            preferred_types = {
                "city",
                "town",
                "village",
                "municipality",
                "state",
                "region",
                "island",
                "administrative",
            }

            # Prefer a result that looks like a destination.
            for result in results:
                address = result.get("address", {})
                result_type = result.get("type", "").lower()

                if (
                    result_type in preferred_types
                    or address.get("city")
                    or address.get("town")
                    or address.get("municipality")
                    or address.get("state")
                ):
                    return {
                        "name": (
                            result.get("name")
                            or address.get("city")
                            or address.get("town")
                            or place
                        ),
                        "country": address.get("country", ""),
                        "latitude": float(result["lat"]),
                        "longitude": float(result["lon"]),
                        "display_name": result.get(
                            "display_name",
                            place,
                        ),
                    }

            # If no preferred result exists, use the first valid result.
            for result in results:
                if "lat" in result and "lon" in result:
                    address = result.get("address", {})

                    return {
                        "name": result.get("name", place),
                        "country": address.get("country", ""),
                        "latitude": float(result["lat"]),
                        "longitude": float(result["lon"]),
                        "display_name": result.get(
                            "display_name",
                            place,
                        ),
                    }

    except Exception:
        pass

    # -----------------------------------------------------
    # Fallback to Open-Meteo
    # -----------------------------------------------------

    try:
        open_meteo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        params = {
            "name": place,
            "count": 10,
            "language": "en",
            "format": "json",
        }

        response = requests.get(
            open_meteo_url,
            params=params,
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        if results:
            preferred = [
                item
                for item in results
                if item.get("feature_code", "").startswith(
                    ("PPL", "ADM")
                )
            ]

            result = preferred[0] if preferred else results[0]

            return {
                "name": result.get("name", place),
                "country": result.get("country", ""),
                "latitude": float(result["latitude"]),
                "longitude": float(result["longitude"]),
                "display_name": (
                    f"{result.get('name', place)}, "
                    f"{result.get('country', '')}"
                ),
            }

    except Exception:
        pass

    return None


# =========================================================
# WEATHER HELPER
# =========================================================

def get_weather(location):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "timezone": "auto",
    }

    response = requests.get(
        url,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()["current"]


def weather_description(code):
    if code == 0:
        return "☀️ Clear Sky"
    if code in [1, 2, 3]:
        return "⛅ Cloudy"
    if code in [45, 48]:
        return "🌫️ Fog"
    if code in [51, 53, 55]:
        return "🌦️ Drizzle"
    if code in [61, 63, 65]:
        return "🌧️ Rain"
    if code in [66, 67]:
        return "🌧️ Freezing Rain"
    if code in [71, 73, 75, 77]:
        return "❄️ Snow"
    if code in [80, 81, 82]:
        return "🌦️ Rain Showers"
    if code in [85, 86]:
        return "🌨️ Snow Showers"
    if code in [95, 96, 99]:
        return "⛈️ Thunderstorm"

    return "🌤️ Unknown"


# =========================================================
# GENERATE PLAN
# =========================================================

if st.button(
    "🤖 GENERATE WORLDWIDE TRAVEL PLAN",
    use_container_width=True,
):

    if not destination.strip():
        st.warning("⚠️ Please enter a destination.")
        st.session_state.plan_created = False
        st.session_state.ai_plan = ""
        st.session_state.location = None

    else:
        clean_destination = destination.strip()

        with st.spinner("🌍 Finding destination..."):
            location = find_location(clean_destination)

        if location is None:
            st.error(
                "❌ Destination could not be found."
            )
            st.info(
                "💡 Try entering the city with its country, "
                "for example: Goa, India or Paris, France."
            )

            st.session_state.plan_created = False
            st.session_state.ai_plan = ""
            st.session_state.location = None

        else:
            st.session_state.location = location

            with st.spinner(
                "🤖 Creating your AI travel plan..."
            ):
                try:
                    ai_plan = generate_ai_plan(
                        clean_destination,
                        int(days),
                        float(budget),
                        interests,
                    )

                    st.session_state.ai_plan = ai_plan
                    st.session_state.plan_created = True

                except Exception as error:
                    st.session_state.plan_created = False
                    st.session_state.ai_plan = ""
                    st.error(
                        "❌ AI travel plan could not be generated."
                    )
                    st.code(str(error))

            if st.session_state.plan_created:
                st.success(
                    f"🎉 Plan created for "
                    f"{location['name']}, "
                    f"{location['country']}!"
                )


# =========================================================
# DISPLAY PLAN
# =========================================================

if (
    st.session_state.plan_created
    and st.session_state.location
    and destination.strip()
):

    location = st.session_state.location

    # -----------------------------------------------------
    # TRIP SUMMARY
    # -----------------------------------------------------

    st.divider()
    st.header("🧳 Trip Summary")

    end_date = (
        start_date
        + timedelta(days=int(days) - 1)
    )

    budget_per_person = (
        float(budget) / int(travelers)
    )

    summary1, summary2, summary3 = st.columns(3)

    with summary1:
        st.metric(
            "📍 Destination",
            location["name"],
        )
        st.metric(
            "📅 Days",
            int(days),
        )

    with summary2:
        st.metric(
            "👥 Travelers",
            int(travelers),
        )
        st.metric(
            "💰 Total Budget",
            f"₹{float(budget):,.0f}",
        )

    with summary3:
        st.metric(
            "👤 Per Person",
            f"₹{budget_per_person:,.0f}",
        )
        st.metric(
    "❤️ Interests",
    ", ".join(interests),
)

    st.write(
        f"🌍 **Country:** {location['country']}"
    )
    st.write(
        f"🗓️ **Start:** {start_date.strftime('%d %B %Y')}"
    )
    st.write(
        f"🏁 **End:** {end_date.strftime('%d %B %Y')}"
    )

    # -----------------------------------------------------
    # BUDGET BREAKDOWN
    # -----------------------------------------------------

    st.divider()
    st.header("💰 Budget Breakdown")

    hotel_budget = float(budget) * 0.40
    food_budget = float(budget) * 0.20
    transport_budget = float(budget) * 0.15
    activities_budget = float(budget) * 0.15
    other_budget = float(budget) * 0.10

    b1, b2, b3, b4, b5 = st.columns(5)

    with b1:
        st.metric("🏨 Hotel", f"₹{hotel_budget:,.0f}")
    with b2:
        st.metric("🍴 Food", f"₹{food_budget:,.0f}")
    with b3:
        st.metric("🚕 Transport", f"₹{transport_budget:,.0f}")
    with b4:
        st.metric("🎟️ Activities", f"₹{activities_budget:,.0f}")
    with b5:
        st.metric("🛍️ Other", f"₹{other_budget:,.0f}")

    # -----------------------------------------------------
    # WEATHER
    # -----------------------------------------------------

    st.divider()
    st.header("🌦️ Live Weather")

    try:
        weather = get_weather(location)

        w1, w2, w3, w4 = st.columns(4)

        with w1:
            st.metric(
                "🌡️ Temperature",
                f"{weather['temperature_2m']} °C",
            )

        with w2:
            st.metric(
                "🌡️ Feels Like",
                f"{weather['apparent_temperature']} °C",
            )

        with w3:
            st.metric(
                "💧 Humidity",
                f"{weather['relative_humidity_2m']}%",
            )

        with w4:
            st.metric(
                "💨 Wind",
                f"{weather['wind_speed_10m']} km/h",
            )

        st.success(
            weather_description(
                weather["weather_code"]
            )
        )

    except Exception as error:
        st.warning(
            "⚠️ Live weather is currently unavailable."
        )

   # -----------------------------------------------------
# MAP
# -----------------------------------------------------

st.divider()
st.header("🗺️ Destination Map")

map_location = st.session_state.get("location")

if map_location:
    map_data = {
        "latitude": [map_location["latitude"]],
        "longitude": [map_location["longitude"]],
    }

    st.map(map_data)

    st.caption(
        f"📍 {map_location['name']}, {map_location['country']}"
    )
else:
    st.info("📍 Generate a travel plan to display the destination map.")
# -----------------------------------------------------
# AI GENERATED PLAN
# -----------------------------------------------------

st.divider()
st.header("🤖 AI Generated Travel Plan")

st.markdown(
    st.session_state.ai_plan
)

   # =====================================================
# DATE-WISE ITINERARY
# =====================================================

st.header("📅 Date-Wise Itinerary")

import re

# Get the complete AI-generated plan
ai_text = st.session_state.get("ai_plan", "")

if ai_text:

    # Find Day 1, Day 2, Day 3, etc.
    day_matches = list(
        re.finditer(
            r"(?im)^\s*#+\s*(?:📅\s*)?Day\s+(\d+)\b.*$",
            ai_text
        )
    )

    for day_number in range(1, int(days) + 1):

        current_date = (
            start_date +
            timedelta(days=day_number - 1)
        )

        st.subheader(
            f"🌟 Day {day_number} — "
            f"{current_date.strftime('%d %B %Y')}"
        )

        day_content = ""

        # Find the correct Day
        for index, match in enumerate(day_matches):

            found_day = int(match.group(1))

            if found_day == day_number:

                start_position = match.end()

                if index + 1 < len(day_matches):
                    end_position = day_matches[index + 1].start()
                else:
                    end_position = len(ai_text)

                day_content = ai_text[
                    start_position:end_position
                ].strip()

                break

        if day_content:

            # Morning
            morning_match = re.search(
                r"(?is)"
                r"###\s*(?:🌅\s*)?Morning\s*"
                r"(.*?)"
                r"(?=###\s*(?:☀️\s*)?Afternoon|\Z)",
                day_content
            )

            if morning_match:
                st.markdown("### 🌅 Morning")
                st.markdown(
                    morning_match.group(1).strip()
                )

            # Afternoon
            afternoon_match = re.search(
                r"(?is)"
                r"###\s*(?:☀️\s*)?Afternoon\s*"
                r"(.*?)"
                r"(?=###\s*(?:🌆\s*)?Evening|\Z)",
                day_content
            )

            if afternoon_match:
                st.markdown("### ☀️ Afternoon")
                st.markdown(
                    afternoon_match.group(1).strip()
                )

            # Evening
            evening_match = re.search(
                r"(?is)"
                r"###\s*(?:🌆\s*)?Evening\s*"
                r"(.*?)(?=\n##\s|\Z)",
                day_content
            )

            if evening_match:
                st.markdown("### 🌆 Evening")
                st.markdown(
                    evening_match.group(1).strip()
                )

            # If Morning/Afternoon/Evening headings
            # were not detected, show the full day.
            if not (
                morning_match
                or afternoon_match
                or evening_match
            ):
                st.markdown(day_content)

        else:
            st.info(
                f"⚠️ No activities found for Day {day_number}."
            )

        st.divider()

else:

    st.info(
        "🤖 Generate an AI travel plan first."
    )
   # =====================================================
# HOTEL RECOMMENDATIONS
# =====================================================

st.header("🏨 Hotel Recommendations")

try:

    hotels = recommend_hotels(
        destination,
        budget,
        days,
        travelers
    )

    if hotels:

        for number, hotel in enumerate(
            hotels,
            start=1
        ):

            st.subheader(
                f"🏨 Hotel Option {number}"
            )

            st.write(
                f"**{hotel.get('name', 'Hotel')}**"
            )

            st.write(
                f"💰 **Price:** "
                f"{hotel.get('price', 'Check live price')}"
            )

            st.write(
                f"⭐ **Rating:** "
                f"{hotel.get('rating', 'Check live rating')}"
            )

            st.write(
                f"📝 **About:** "
                f"{hotel.get('description', '')}"
            )

            # Open the real hotel search
            if hotel.get("link"):
                st.link_button(
                    "🔗 Search / View Hotels",
                    hotel["link"],
                    use_container_width=True
                )

            st.divider()

    else:

        st.info(
            "No hotel recommendations found."
        )

except Exception as error:

    st.error(
        "❌ Hotel recommendation error."
    )

    st.code(
        str(error)
    )

    # -----------------------------------------------------
    # AI TOUR GUIDE
    # -----------------------------------------------------

    st.divider()
    st.header("🧑‍🏫 AI Tour Guide")

    guide_place = st.text_input(
        "📍 What place do you want to know about?",
        placeholder="Example: Eiffel Tower",
        key="guide_place",
    )

    if st.button(
        "🧑‍🏫 SHOW TOUR GUIDE",
        use_container_width=True,
    ):

        if not guide_place.strip():
            st.warning(
                "⚠️ Please enter a place."
            )

        else:
            try:
                guide = get_tour_guide(
                    guide_place,
                    interests,
                )

                st.success(
                    f"📍 {guide['name']}"
                )

                st.subheader("📖 About")
                st.write(guide["about"])

                st.subheader("⏰ Best Time to Visit")
                st.write(guide["best_time"])

                st.subheader("⏱️ Recommended Duration")
                st.write(guide["duration"])

                st.subheader("💡 Travel Tips")

                for tip in guide["tips"]:
                    st.write(f"• {tip}")

            except Exception as error:
                st.error(
                    "❌ Tour guide error."
                )
                st.code(str(error))

    # =====================================================
# TRANSPORTATION RECOMMENDATIONS
# =====================================================

st.header("🚕 Transportation Recommendations")

try:

    transport_options = recommend_transport(
    origin,
    destination,
    travelers,
    budget,
    start_date
)

    if transport_options:

        for number, transport in enumerate(
            transport_options,
            start=1
        ):

            st.subheader(
                f"🚗 Option {number}"
            )

            st.write(
                f"**{transport.get('name', 'Transportation')}**"
            )

            st.write(
                f"💰 **Price:** "
                f"{transport.get('price', 'Check current price')}"
            )

            st.write(
                f"👥 **Best For:** "
                f"{transport.get('best_for', 'Travelers')}"
            )

            st.write(
                f"📝 **Description:** "
                f"{transport.get('description', '')}"
            )

            if transport.get("link"):

                st.link_button(
                    "🔗 View Transportation",
                    transport["link"],
                    use_container_width=True
                )

            st.divider()

    else:

        st.info(
            "No transportation recommendations found."
        )

except Exception as error:

    st.error(
        "❌ Transportation recommendation error."
    )

    st.code(
        str(error)
    )
    # -----------------------------------------------------
    # SAVE TRIP
    # -----------------------------------------------------

    st.divider()
    st.header("💾 Save Your Trip")

    if st.button(
        "💾 SAVE MY TRIP",
        use_container_width=True,
    ):

        try:
            conn = sqlite3.connect(
                "travel_planner.db"
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO trips
                (
                    username,
                    destination,
                    start_date,
                    days,
                    travelers,
                    budget,
                    interest,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    st.session_state.username,
                    destination.strip(),
                    start_date.strftime("%Y-%m-%d"),
                    int(days),
                    int(travelers),
                    float(budget),
                    interests,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                ),
            )

            conn.commit()
            conn.close()

            st.success(
                "✅ Trip saved successfully!"
            )

        except Exception as error:
            st.error(
                "❌ Could not save the trip."
            )
            st.code(str(error))


# =========================================================
# SAVED TRIPS
# =========================================================

st.divider()
st.header(
    f"📂 {st.session_state.username}'s Saved Trips"
)

if st.button(
    "📂 VIEW MY SAVED TRIPS",
    use_container_width=True,
):

    try:
        conn = sqlite3.connect(
            "travel_planner.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                destination,
                start_date,
                days,
                travelers,
                budget,
                interest,
                created_at
            FROM trips
            WHERE username = ?
            ORDER BY id DESC
            """,
            (
                st.session_state.username,
            ),
        )

        saved_trips = cursor.fetchall()
        conn.close()

        if not saved_trips:
            st.info(
                "You don't have any saved trips yet."
            )

        else:
            st.success(
                f"Found {len(saved_trips)} saved trip(s)!"
            )

            for number, trip in enumerate(
                saved_trips,
                start=1,
            ):
                with st.expander(
                    f"✈️ Trip {number} — {trip[0]}"
                ):
                    st.write(
                        f"📍 **Destination:** {trip[0]}"
                    )
                    st.write(
                        f"🗓️ **Start Date:** {trip[1]}"
                    )
                    st.write(
                        f"📅 **Days:** {trip[2]}"
                    )
                    st.write(
                        f"👥 **Travelers:** {trip[3]}"
                    )
                    st.write(
                        f"💰 **Budget:** ₹{trip[4]:,.0f}"
                    )
                    st.write(
                        f"❤️ **Interest:** {trip[5]}"
                    )
                    st.write(
                        f"🕐 **Saved:** {trip[6]}"
                    )

    except Exception as error:
        st.error(
            "❌ Could not load saved trips."
        )
        st.code(str(error))


# =========================================================
# AI TRAVEL ASSISTANT
# =========================================================

st.divider()
st.header("🤖 AI Travel Assistant")
st.caption("Ask anything about your destination, food, activities, safety, or budget.")

question = st.text_input(
    "💬 Ask your travel question:",
    placeholder="Example: What should I visit first?",
    key="travel_question",
)

if st.button("🤖 ASK ASSISTANT", use_container_width=True, key="ask_travel_assistant"):
    if not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        try:
            with st.spinner("🤖 Thinking... Llama 3.2 is preparing your answer. Please wait."):
                answer = travel_chatbot(
                    question=question.strip(),
                    destination=destination.strip() if destination.strip() else "Worldwide",
                    interests=interests,
                    budget=budget,
                )
            st.session_state["travel_assistant_answer"] = answer
        except Exception as error:
            st.session_state["travel_assistant_answer"] = (
                "AI assistant error. Please check that Ollama is running.\n\n"
                f"Technical details: {error}"
            )

if st.session_state.get("travel_assistant_answer"):
    st.markdown("### ✨ Your answer")
    st.markdown(st.session_state["travel_assistant_answer"])

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌍 AI Travel Planner | Worldwide Travel Assistant | "
    "Final Year Project"
)
