import os
import requests
import streamlit as st
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# =============================
# GEMINI CONFIG
# =============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=(
            "You are a helpful movie expert assistant. You ONLY answer questions related to "
            "movies, cinema, actors, directors, and the film industry. If a user asks "
            "anything outside of these topics, politely decline and steer the conversation "
            "back to movies. Keep your responses concise and engaging."
        )
    )

# =============================
# CONFIG
# =============================
API_BASE = os.getenv("API_BASE", "https://movie-rec-466x.onrender.com")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="Movie Recommender", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# ANIMATED THEME CONFIGURATION (CRYSTAL-LUMINA)
# =============================
def get_theme_styles():
    """Crystal-Lumina with enhanced animations"""
    return {
        "bg": "#fdfdfd",
        "card_bg": "rgba(255, 255, 255, 0.75)",
        "card_blur": "blur(30px)",
        "text": "#1e293b",
        "text_muted": "rgba(30, 41, 59, 0.65)",
        "border": "rgba(0, 0, 0, 0.04)",
        "accent": "#0ea5e9",
        "accent_hover": "#d946ef",
        "gradient": "linear-gradient(135deg, #0ea5e9 0%, #d946ef 50%, #f59e0b 100%)",
        "shadow": "0 25px 60px rgba(0, 0, 0, 0.05), 0 5px 15px rgba(0, 0, 0, 0.02)",
        "button_text": "#ffffff",
        "input_text": "#2563eb",
        "input_bg": "rgba(255, 255, 255, 0.95)",
        "sidebar_bg": "#ffffff",
        "link_color": "#d946ef",
    }

# =============================
def apply_custom_styles():
    theme = get_theme_styles()
    
    # Base CSS with extensive animations
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Space+Grotesk:wght@300;500;700&display=swap');

        /* ===== GLOBAL ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes scaleIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px rgba(14, 165, 233, 0.3); }
            50% { box-shadow: 0 0 40px rgba(217, 70, 239, 0.5); }
        }
        
        @keyframes rotate-slow {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        @keyframes typewriter {
            from { width: 0; }
            to { width: 100%; }
        }
        
        @keyframes blink {
            50% { border-color: transparent; }
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes particle-float {
            0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            50% { transform: translateY(-100vh) translateX(50px); }
        }
        
        @property --border-angle {
            syntax: '<angle>';
            initial-value: 0deg;
            inherits: false;
        }

        /* ===== MAIN CONTAINER ===== */
        .stApp {
            background: [BG] !important;
            color: [TEXT];
            font-family: 'Space Grotesk', sans-serif !important;
            background-image: 
                radial-gradient(at 0% 0%, rgba(109, 40, 217, 0.2) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(219, 39, 119, 0.2) 0px, transparent 50%),
                radial-gradient(at 50% 50%, rgba(37, 99, 235, 0.1) 0px, transparent 70%) !important;
            animation: fadeIn 0.8s ease-out;
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: 
                radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.15) 0, transparent 50%), 
                radial-gradient(at 100% 0%, rgba(217, 70, 239, 0.15) 0, transparent 50%), 
                radial-gradient(at 50% 100%, rgba(245, 158, 11, 0.1) 0, transparent 50%);
            z-index: -1;
            pointer-events: none;
            animation: gradient-shift 15s ease infinite;
            background-size: 200% 200%;
        }

        /* ===== PARTICLE EFFECT ===== */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: [GRADIENT];
            border-radius: 50%;
            animation: particle-float 20s infinite linear;
            opacity: 0;
        }

        /* ===== SIDEBAR ANIMATIONS ===== */
        section[data-testid="stSidebar"] {
            background-color: [SIDEBAR_BG] !important;
            border-right: 1px solid [BORDER] !important;
            box-shadow: 10px 0 30px rgba(0,0,0,0.02);
            animation: slideInLeft 0.6s ease-out;
        }

        section[data-testid="stSidebar"] .stMarkdown p {
            color: [TEXT] !important;
            animation: fadeIn 0.5s ease-out;
        }

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: [GRADIENT];
            border-radius: 10px;
            animation: pulse-glow 3s infinite;
        }

        /* ===== TYPOGRAPHY ===== */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp li, .stApp label, .stMarkdown p {
            color: [TEXT] !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }
        
        /* ===== ANIMATED DATETIME ===== */
        .datetime-container {
            background: [CARD_BG];
            backdrop-filter: [CARD_BLUR];
            padding: 10px 25px;
            border-radius: 50px;
            display: inline-block;
            margin-bottom: 20px;
            border: 1px solid [BORDER];
            color: [TEXT] !important;
            font-weight: 600;
            box-shadow: [SHADOW];
            animation: fadeInUp 0.6s ease-out, float 6s ease-in-out infinite;
            transition: all 0.3s ease;
        }
        
        .datetime-container:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(14, 165, 233, 0.2);
        }

        /* ===== MOVIE CARDS WITH CRYSTAL LIQUID BORDER ===== */
        .movie-card {
            background: [CARD_BG] !important;
            backdrop-filter: [CARD_BLUR] !important;
            border-radius: 20px !important;
            padding: 12px;
            margin-bottom: 25px;
            transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            box-shadow: [SHADOW];
            height: 100%;
            display: flex;
            flex-direction: column;
            border: 3px solid transparent !important;
            background-image: linear-gradient([CARD_BG], [CARD_BG]), 
                               conic-gradient(from var(--border-angle, 0deg), #0ea5e9, #d946ef, #f59e0b, #0ea5e9) !important;
            background-origin: border-box !important;
            background-clip: padding-box, border-box !important;
            animation: fadeInUp 0.6s ease-out;
            opacity: 0;
            animation-fill-mode: forwards;
        }

        @keyframes border-run {
            to { --border-angle: 360deg; }
        }

        .movie-card:hover {
            transform: translateY(-10px) scale(1.02);
            animation: border-run 4s linear infinite, fadeInUp 0.6s ease-out;
            box-shadow: 0 30px 60px rgba(0,0,0,0.12) !important;
        }
        
        .movie-poster {
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 12px;
            aspect-ratio: 2/3;
            position: relative;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        
        .movie-poster::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
        }
        
        .movie-card:hover .movie-poster::after {
            left: 100%;
        }
        
        .movie-poster img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        
        .movie-card:hover .movie-poster img {
            transform: scale(1.08);
        }
        
        .movie-title {
            font-size: 1rem;
            font-weight: 700;
            color: [TEXT] !important;
            margin-bottom: 6px;
            line-height: 1.2;
            height: 2.4rem;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            font-family: 'Montserrat', sans-serif;
            transition: color 0.3s ease;
        }
        
        .movie-card:hover .movie-title {
            background: [GRADIENT];
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .movie-rating {
            color: [ACCENT] !important;
            font-size: 0.9rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 700;
            transition: transform 0.3s ease;
        }
        
        .movie-card:hover .movie-rating {
            transform: scale(1.1);
        }
        
        .movie-year {
            color: [TEXT_MUTED] !important;
            font-size: 0.85rem;
            font-weight: 500;
        }

        /* ===== SHIMMER LOADING EFFECT ===== */
        .shimmer-loading {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 1000px 100%;
            animation: shimmer 2s infinite linear;
            border-radius: 12px;
        }

        /* ===== BUTTONS WITH ENHANCED ANIMATIONS ===== */
        .stButton > button {
            background: [GRADIENT];
            background-size: 200% 200%;
            color: [BUTTON_TEXT] !important;
            border: none;
            border-radius: 50px;
            padding: 0.7rem 2.5rem;
            font-weight: 700;
            letter-spacing: 1px;
            transition: all 0.4s ease;
            width: 100%;
            box-shadow: 0 4px 15px [ACCENT]40;
            text-transform: uppercase;
            font-size: 0.85rem;
            font-family: 'Montserrat', sans-serif;
            position: relative;
            overflow: hidden;
            animation: gradient-shift 3s ease infinite;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 25px [ACCENT]60;
            filter: saturate(1.2);
        }
        
        .stButton > button:hover::before {
            left: 100%;
        }
        
        .stButton > button:active {
            transform: translateY(0) scale(0.98);
        }

        /* ===== SIDEBAR BUTTONS ===== */
        .stSidebar .stButton > button {
            color: [BUTTON_TEXT] !important;
            animation: slideInLeft 0.5s ease-out;
        }

        /* ===== LINK BUTTONS ===== */
        .stLinkButton > a {
            color: [LINK_COLOR] !important;
            background: [CARD_BG];
            border: 1px solid [BORDER];
            transition: all 0.3s ease;
        }
        
        .stLinkButton > a:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(217, 70, 239, 0.2);
        }

        /* ===== HEADERS WITH ANIMATED GRADIENT ===== */
        h1, h2, h3 {
            font-family: 'Montserrat', sans-serif !important;
            background: [GRADIENT];
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900 !important;
            letter-spacing: -1.5px !important;
            text-transform: uppercase;
            animation: gradient-shift 5s ease infinite;
        }
        
        /* ===== SIDEBAR HEADERS ===== */
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            background: [GRADIENT];
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 5s ease infinite;
        }

        /* ===== INPUT & SELECTBOX ===== */
        .stTextInput input, 
        .stSelectbox div[data-baseweb="select"] *, 
        .stSelectbox input,
        .stSlider label,
        .stSelectbox label {
            color: #2563eb !important;
            -webkit-text-fill-color: #2563eb !important;
            opacity: 1 !important;
            visibility: visible !important;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div, 
        .stSelectbox > div > div,
        .stSlider > div {
            background-color: #ffffff !important;
            border: 1px solid [BORDER] !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div:focus-within,
        .stSelectbox > div > div:focus-within {
            box-shadow: 0 0 20px rgba(14, 165, 233, 0.3) !important;
            border-color: #0ea5e9 !important;
            transform: translateY(-2px);
        }
        
        .stSelectbox svg {
            fill: #2563eb !important;
            transition: transform 0.3s ease;
        }
        
        .stSelectbox:hover svg {
            transform: rotate(180deg);
        }

        /* ===== DROPDOWN OPTIONS ===== */
        div[data-baseweb="popover"] ul li * {
            color: #2563eb !important;
            background-color: transparent !important;
            transition: all 0.2s ease;
        }
        
        div[data-baseweb="popover"] ul li:hover * {
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.1), transparent) !important;
            padding-left: 10px;
        }

        /* ===== SLIDER ===== */
        .stSlider > div > div {
            color: [TEXT] !important;
        }
        
        .stSlider [role="slider"] {
            transition: transform 0.2s ease;
        }
        
        .stSlider [role="slider"]:hover {
            transform: scale(1.2);
        }

        /* ===== DIVIDER ===== */
        hr {
            border-color: [BORDER];
            opacity: 0.1;
            animation: fadeIn 1s ease-out;
        }

        /* ===== THEME TOGGLE ===== */
        .theme-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: [GRADIENT];
            background-size: 200% 200%;
            border: none;
            border-radius: 50px;
            padding: 10px 20px;
            color: [BUTTON_TEXT] !important;
            font-weight: 600;
            cursor: pointer;
            box-shadow: [SHADOW];
            transition: all 0.3s ease;
            border: 1px solid [BORDER];
            animation: gradient-shift 3s ease infinite, float 4s ease-in-out infinite;
        }
        
        .theme-toggle:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 30px -5px [ACCENT];
        }

        /* ===== LOADING ANIMATIONS ===== */
        @keyframes pulse {
            0% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.05); }
            100% { opacity: 0.6; transform: scale(1); }
        }
        
        .loading {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        /* ===== SPINNER ENHANCEMENT ===== */
        .stSpinner > div {
            animation: rotate-slow 1s linear infinite, pulse-glow 2s infinite !important;
        }

        /* ===== BACKDROP WITH PARALLAX ===== */
        .backdrop-container {
            border-radius: 20px;
            overflow: hidden;
            margin: 20px 0;
            position: relative;
            animation: scaleIn 0.8s ease-out;
        }
        
        .backdrop-container img {
            width: 100%;
            max-height: 300px;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        
        .backdrop-container:hover img {
            transform: scale(1.05);
        }
        
        .backdrop-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, [BG], transparent);
            height: 50%;
            animation: fadeIn 1s ease-out;
        }

        /* ===== GENRE TAGS WITH HOVER ===== */
        .genre-tag {
            background: [GRADIENT];
            background-size: 200% auto;
            padding: 0.4rem 1.2rem;
            border-radius: 50px;
            margin-right: 0.6rem;
            display: inline-block;
            margin-bottom: 0.6rem;
            color: [BUTTON_TEXT] !important;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease-out;
            cursor: pointer;
        }
        
        .genre-tag:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);
            animation: gradient-shift 2s ease infinite;
        }

        /* ===== ALERT ANIMATIONS ===== */
        .stAlert {
            background: [CARD_BG] !important;
            backdrop-filter: [CARD_BLUR];
            border: 1px solid [BORDER] !important;
            border-radius: 15px !important;
            animation: slideInRight 0.5s ease-out, fadeIn 0.5s ease-out;
            transition: all 0.3s ease;
        }
        
        .stAlert:hover {
            transform: translateX(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }

        .stAlert > div {
            color: [TEXT] !important;
        }

        /* ===== INFO BOXES ===== */
        .stInfo {
            background-color: [CARD_BG] !important;
            color: [TEXT] !important;
            animation: fadeInUp 0.5s ease-out;
        }

        /* ===== METRICS WITH ANIMATION ===== */
        [data-testid="stMetricValue"] {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 900 !important;
            color: [TEXT] !important;
            animation: scaleIn 0.5s ease-out;
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetricValue"]:hover {
            transform: scale(1.1);
            background: [GRADIENT];
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stMetric label {
            color: [TEXT_MUTED] !important;
            animation: fadeIn 0.6s ease-out;
        }

        /* ===== CHAT MESSAGE ANIMATIONS ===== */
        .stChatMessage {
            animation: fadeInUp 0.4s ease-out;
            transition: all 0.3s ease;
        }
        
        .stChatMessage:hover {
            transform: translateX(5px);
        }

        /* ===== SEARCH INPUT ANIMATION ===== */
        .stTextInput input {
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
        }

        /* ===== GRID STAGGER ANIMATION ===== */
        @keyframes staggerIn {
            from { opacity: 0; transform: translateY(30px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* ===== SMOOTH SCROLL ===== */
        html {
            scroll-behavior: smooth;
        }

        /* ===== CUSTOM CURSOR ===== */
        .stApp {
            cursor: default;
        }
        
        .movie-card, .stButton > button, .genre-tag {
            cursor: pointer;
        }

        /* ===== PAGE TRANSITION OVERLAY ===== */
        .page-transition {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: [GRADIENT];
            z-index: 9999;
            animation: fadeOut 0.5s ease-out forwards;
            pointer-events: none;
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    """
    
    # Add stagger delay for cards
    for i in range(24):
        css += f"""
        .movie-card:nth-child({i+1}) {{
            animation-delay: {i * 0.05}s;
        }}
        """
    
    # Close style tag
    css += "</style>"
    
    # Replace placeholders with theme values
    for key, value in theme.items():
        css = css.replace(f"[{key.upper()}]", value)
        
    st.markdown(css, unsafe_allow_html=True)

# Apply styles
apply_custom_styles()

# Add particle effects
def add_particles():
    particles_html = """
    <div class="particles">
    """
    for i in range(20):
        left = (i * 5) % 100
        delay = i * 0.5
        duration = 15 + (i % 10)
        particles_html += f'<div class="particle" style="left: {left}%; animation-delay: {delay}s; animation-duration: {duration}s;"></div>'
    particles_html += "</div>"
    st.markdown(particles_html, unsafe_allow_html=True)

add_particles()

# =============================
# ANIMATED DATE AND TIME DISPLAY
# =============================
def display_datetime():
    now = datetime.now()
    formatted_date = now.strftime("%A, %B %d, %Y")
    formatted_time = now.strftime("%I:%M:%S %p")
    
    datetime_placeholder = st.empty()
    
    with datetime_placeholder.container():
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <div class='datetime-container'>
                <span style='font-size: 1.1rem; margin-right: 10px; color: #1e293b !important;'>📅 {formatted_date}</span>
                <span style='font-size: 1.1rem; color: #1e293b !important;'>⏰ {formatted_time}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-refresh every second using JavaScript with smooth transitions
    st.markdown("""
    <script>
        function updateTime() {
            var elements = document.getElementsByClassName('datetime-container');
            if (elements.length > 0) {
                var now = new Date();
                var dateStr = now.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
                var timeStr = now.toLocaleTimeString('en-US', { 
                    hour12: true,
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                elements[0].style.opacity = '0.7';
                setTimeout(() => {
                    elements[0].innerHTML = '<span style="font-size: 1.1rem; margin-right: 10px;">📅 ' + dateStr + '</span>' +
                                           '<span style="font-size: 1.1rem;">⏰ ' + timeStr + '</span>';
                    elements[0].style.opacity = '1';
                }, 150);
            }
            setTimeout(updateTime, 1000);
        }
        setTimeout(updateTime, 1000);
    </script>
    """, unsafe_allow_html=True)

display_datetime()

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "page_transition" not in st.session_state:
    st.session_state.page_transition = False

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details", "sentiment"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass

def goto_home():
    st.session_state.page_transition = True
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()

def goto_details(tmdb_id: int):
    st.session_state.page_transition = True
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()

def goto_sentiment():
    st.session_state.page_transition = True
    st.session_state.view = "sentiment"
    st.query_params["view"] = "sentiment"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()

# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"

def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")
            year = m.get("release_date", "")[:4] if m.get("release_date") else ""
            
            rating = m.get("vote_average")
            rating_display = f"{float(rating):.1f}" if rating is not None else ""

            with colset[c]:
                rating_html = f"<div class='movie-rating'>⭐ {rating_display}</div>" if rating_display else ""
                year_html = f"<div class='movie-year'>{year}</div>" if year else ""
                
                poster_url = poster if poster else "https://via.placeholder.com/500x750?text=No+Poster"
                
                # Add shimmer loading effect initially
                card_html = f"""
                <div class='movie-card' style='animation-delay: {idx * 0.05}s'>
                    <div class='movie-poster'>
                        <img src='{poster_url}' alt='{title}' loading='lazy'>
                    </div>
                    <div class='movie-title'>{title}</div>
                    {rating_html}
                    {year_html}
                </div>
                """
                
                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button("🎬 View Details", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date"),
                    "vote_average": tmdb.get("vote_average"),
                }
            )
    return cards

def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average", 0),
                }
            )

    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average", 0),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {
            "tmdb_id": x["tmdb_id"], 
            "title": x["title"], 
            "poster_url": x["poster_url"],
            "release_date": x["release_date"],
            "vote_average": x["vote_average"]
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards

# =============================
# SIDEBAR WITH ANIMATIONS
# =============================
home_category = "trending"
with st.sidebar:
    # Animated logo
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0; animation: fadeInUp 0.8s ease-out;'>
        <h1 style='font-size: 2.5rem; margin: 0; animation: float 3s ease-in-out infinite;'>🌌</h1>
        <h2 style='margin: 0; font-size: 1.4rem; letter-spacing: 1px; animation: gradient-shift 5s ease infinite; background-size: 200% auto;'>LUMINA ENGINE</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Animated home button
    if st.button("🏠 Home", use_container_width=True):
        goto_home()

    st.markdown("---")

    st.markdown("### 💬 Movie Analysis Tools")

    if st.button("🎭 Sentiment Analysis 🎭", use_container_width=True):
        goto_sentiment()

    st.markdown("---")
    st.markdown("### 🎯 Feed Category")
    home_category = st.selectbox(
        "Select category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0
    )
    
    grid_cols = st.slider("Grid columns", 4, 8, 6)
    
    st.markdown("---")
    st.markdown("### 🤖 Movie Expert AI")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat history container with animations
    with st.container(height=350):
        if not st.session_state.chat_history:
            st.info("👋 Ask me anything about movies!")
        for i, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(f'<div style="animation: fadeInUp 0.3s ease-out {i*0.1}s both;">{message["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask about movies...", key="sidebar_chat"):
        if not GEMINI_API_KEY:
            st.error("Gemini API key not found in .env")
        else:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            try:
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.chat_history[:-1]
                ]
                chat_session = model.start_chat(history=history)
                response = chat_session.send_message(prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"Chat Error: {e}")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.8rem; animation: fadeIn 1s ease-out;'>
        Made with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True)

# =============================
# ANIMATED HEADER
# =============================
st.markdown("""
<div style='text-align: center; padding: 3rem 0; animation: fadeInUp 1s ease-out;'>
    <h1 style='font-size: 3.8rem; margin-bottom: 0.5rem; letter-spacing: -2px; animation: gradient-shift 5s ease infinite; background-size: 200% auto;'>🎬 MOVIE DISCOVERY ENGINE</h1>
    <p style='color: #64748b; font-size: 1.2rem; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; animation: fadeInUp 1s ease-out 0.3s both;'>
        The Future of Cinematic Exploration
    </p>
</div>
""", unsafe_allow_html=True)

# Page transition effect
if st.session_state.page_transition:
    st.markdown('<div class="page-transition"></div>', unsafe_allow_html=True)
    st.session_state.page_transition = False

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    # Animated search input
    typed = st.text_input(
        "🔍 Search movies",
        placeholder="Type movie title (e.g., Avengers, Batman, Inception...)",
        help="Start typing to search for movies"
    )

    if typed.strip():
        if len(typed.strip()) < 2:
            st.info("💡 Type at least 2 characters to see suggestions")
        else:
            # Animated spinner
            with st.spinner("🔍 Searching movies..."):
                # Add a small delay for animation effect
                time.sleep(0.3)
                data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                if suggestions:
                    st.markdown("### 📝 Quick Select")
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0, label_visibility="collapsed")

                    if selected != "-- Select a movie --":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### 🎬 Search Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE with animated title
    category_display = str(home_category).replace('_', ' ').title() if home_category else "Movies"
    st.markdown(f"""
    <h3 style='animation: slideInLeft 0.6s ease-out;'>📈 {category_display}</h3>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading movies..."):
        time.sleep(0.2)  # Subtle animation delay
        home_cards, err = api_get_json(
            "/home", params={"category": home_category, "limit": 24}
        )
    
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("← Back to Home", use_container_width=True):
            goto_home()

    with st.spinner("Loading movie details..."):
        time.sleep(0.2)
        data, err = api_get_json(f"/movie/id/{tmdb_id}")
    
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Animated backdrop
    if data.get("backdrop_url"):
        st.markdown(f"""
        <div class='backdrop-container'>
            <img src='{data["backdrop_url"]}' alt='Backdrop'>
            <div class='backdrop-overlay'></div>
        </div>
        """, unsafe_allow_html=True)

    # Main content with staggered animations
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown("<div class='movie-card' style='animation: slideInLeft 0.6s ease-out;'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.markdown("""
            <div style='background: #1e293b; border-radius: 12px; padding: 2rem; text-align: center; animation: pulse 2s infinite;'>
                🖼️ No poster available
            </div>
            """, unsafe_allow_html=True)
        
        vote_average = data.get("vote_average")
        if vote_average is not None:
            st.markdown(f"<div class='movie-rating' style='justify-content: center; animation: scaleIn 0.5s ease-out;'>⭐ {float(vote_average):.1f}/10</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(f"<h1 style='animation: fadeInUp 0.6s ease-out;'>{data.get('title','')}</h1>", unsafe_allow_html=True)
        
        release = data.get("release_date")
        release_year = release[:4] if release and len(release) >= 4 else "N/A"
        
        genres = data.get("genres", [])
        genres_str = ", ".join([g["name"] for g in genres]) if genres else "Genres not specified"
        
        col1, col2, col3 = st.columns(3)
        metrics = [
            ("Release Year", release_year),
            ("Runtime", f"{data.get('runtime')} min" if data.get('runtime') else "N/A"),
            ("Status", data.get("status", "N/A"))
        ]
        for i, (col, (label, value)) in enumerate(zip([col1, col2, col3], metrics)):
            with col:
                st.metric(label, value)
        
        st.markdown("---")
        st.markdown("<h3 style='animation: fadeInUp 0.5s ease-out;'>📖 Overview</h3>", unsafe_allow_html=True)
        st.write(data.get("overview") or "No overview available.")
        
        if genres:
            st.markdown("<h3 style='animation: fadeInUp 0.5s ease-out 0.1s both;'>🎭 Genres</h3>", unsafe_allow_html=True)
            genre_html = ""
            for i, genre in enumerate(genres):
                genre_html += f"<span class='genre-tag' style='animation-delay: {i * 0.1}s'>{genre['name']}</span>"
            st.markdown(genre_html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <h2 style='animation: fadeInUp 0.6s ease-out;'>🎯 You Might Also Like</h2>
    """, unsafe_allow_html=True)

    title = (data.get("title") or "").strip()
    if title:
        with st.spinner("Finding recommendations..."):
            time.sleep(0.3)
            bundle, err2 = api_get_json(
                "/movie/search",
                params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
            )

        if not err2 and bundle:
            tfidf_recs = bundle.get("tfidf_recommendations")
            if tfidf_recs:
                st.markdown("<h3 style='animation: slideInLeft 0.5s ease-out;'>📊 Based on Plot Similarity</h3>", unsafe_allow_html=True)
                poster_grid(
                    to_cards_from_tfidf_items(tfidf_recs),
                    cols=grid_cols,
                    key_prefix="details_tfidf",
                )

            genre_recs = bundle.get("genre_recommendations", [])
            if genre_recs:
                st.markdown("<h3 style='animation: slideInLeft 0.5s ease-out 0.1s both;'>🎭 Based on Genre</h3>", unsafe_allow_html=True)
                poster_grid(
                    genre_recs,
                    cols=grid_cols,
                    key_prefix="details_genre",
                )
            
            if not tfidf_recs and not genre_recs:
                st.info("No recommendations available for this movie.")
        else:
            st.info("Showing Genre-based recommendations...")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")

# ==========================================================
# VIEW: SENTIMENT ANALYSIS
# ==========================================================
elif st.session_state.view == "sentiment":
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; animation: fadeInUp 0.8s ease-out;'>
        <h1 style='font-size: 3rem;'>🎭 SENTIMENT ANALYSIS</h1>
        <p style='color: #64748b; font-size: 1.1rem;'>Understand the emotion behind the reviews</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("← Back to Home", use_container_width=True):
            goto_home()

    st.markdown("<div class='movie-card' style='padding: 2rem; animation: scaleIn 0.6s ease-out;'>", unsafe_allow_html=True)
    review_text = st.text_area(
        "Enter Movie Review",
        placeholder="Type your thoughts about a movie here...",
        height=200
    )

    if st.button("🚀 Analyze Sentiment", use_container_width=True):
        if not review_text.strip():
            st.warning("Please enter some text to analyze.")
        elif not GEMINI_API_KEY:
            st.error("Gemini API key not found. Please configure it in .env")
        else:
            with st.spinner("Analyzing emotion..."):
                try:
                    prompt = f"""
                    Analyze the sentiment of the following movie review:
                    "{review_text}"
                    
                    Provide the result in the following format:
                    SENTIMENT: [Positive/Negative/Neutral]
                    SCORE: [0-100]
                    REASON: [One sentence explanation]
                    """
                    response = model.generate_content(prompt)
                    result = response.text
                    
                    # Simple parsing
                    sentiment = "Neutral"
                    if "Positive" in result: sentiment = "Positive"
                    elif "Negative" in result: sentiment = "Negative"
                    
                    color = "#00ff88" if sentiment == "Positive" else "#ff3333" if sentiment == "Negative" else "#ffcc00"
                    
                    st.markdown(f"""
                    <div style='text-align: center; padding: 2rem; border-top: 1px solid rgba(0,0,0,0.1); margin-top: 2rem; animation: fadeInUp 0.6s ease-out;'>
                        <h2 style='color: {color} !important; font-size: 2.5rem; margin-bottom: 0;'>{sentiment} Sentiment</h2>
                        <div style='margin-top: 1rem; color: #1e293b; font-size: 1.1rem;'>
                            {result.split('REASON:')[-1] if 'REASON:' in result else result}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)