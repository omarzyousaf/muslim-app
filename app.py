import streamlit as st
import requests
from datetime import datetime, date, timedelta
import math
import pytz
import uuid
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Salah", page_icon="🕌", layout="centered")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

is_dark = st.session_state.dark_mode
bg          = "#0a0a0a" if is_dark else "#f5f0eb"
card_bg     = "#111111" if is_dark else "#ffffff"
text        = "#e8e2d9" if is_dark else "#1a1a1a"
muted       = "#7a6f63" if is_dark else "#8a7f73"
border      = "#1e1e1e" if is_dark else "#e0d8d0"
dim         = "#4a4540" if is_dark else "#aaa099"
very_dim    = "#2e2e2e" if is_dark else "#ccc5bc"
gold        = "#c8a96e"
streak_bg   = "#131210" if is_dark else "#fdf6ec"
tracker_done_bg = "#0f130f" if is_dark else "#f0f7f0"
tracker_done_border = "#2a3a2a" if is_dark else "#a0c8a0"

ramadan_border_color = "#c8692e" if is_dark else "#d4783a"
ramadan_title_color  = "#e8a05a" if is_dark else "#7a3010"
ramadan_arabic_color = "#c8692e" if is_dark else "#a04820"
ramadan_bg = "linear-gradient(135deg, #1a0d0a 0%, #2a1505 100%)" if is_dark else "linear-gradient(135deg, #fdf6ed 0%, #faecd8 100%)"

_cached_tz = st.session_state.get("cached_timezone", "UTC")
try:
    _tz = pytz.timezone(_cached_tz)
    _local_now = datetime.now(_tz)
except Exception:
    _local_now = datetime.now()
_h = _local_now.hour
if is_dark:
    if   4 <= _h <  6: _bg_gradient = "linear-gradient(170deg, #0d0820 0%, #1e103a 60%, #2d1a4a 100%)"
    elif 6 <= _h <  8: _bg_gradient = "linear-gradient(170deg, #0d0810 0%, #2a1008 50%, #5a2e0a 100%)"
    elif 8 <= _h < 12: _bg_gradient = "linear-gradient(170deg, #040c18 0%, #071828 60%, #0a2035 100%)"
    elif 12 <= _h < 15: _bg_gradient = "linear-gradient(170deg, #04080f 0%, #06101e 50%, #0a1830 100%)"
    elif 15 <= _h < 17: _bg_gradient = "linear-gradient(170deg, #06050f 0%, #180f28 50%, #2a1a08 100%)"
    elif 17 <= _h < 20: _bg_gradient = "linear-gradient(170deg, #08030a 0%, #280a10 30%, #3a1208 60%, #1a0808 100%)"
    else:               _bg_gradient = "linear-gradient(170deg, #020205 0%, #06060f 60%, #0a0a18 100%)"
else:
    if   4 <= _h <  6: _bg_gradient = "linear-gradient(170deg, #e0d8f0 0%, #f0e8f8 100%)"
    elif 6 <= _h <  8: _bg_gradient = "linear-gradient(170deg, #fef0d8 0%, #fde0c0 50%, #fac8a0 100%)"
    elif 8 <= _h < 12: _bg_gradient = "linear-gradient(170deg, #e8f0fc 0%, #d8e8f8 100%)"
    elif 12 <= _h < 15: _bg_gradient = "linear-gradient(170deg, #e0eaf8 0%, #cce0f4 100%)"
    elif 15 <= _h < 17: _bg_gradient = "linear-gradient(170deg, #fef4e0 0%, #fde8c8 100%)"
    elif 17 <= _h < 20: _bg_gradient = "linear-gradient(170deg, #fde8d8 0%, #f8d0c0 40%, #f0c0d0 100%)"
    else:               _bg_gradient = "linear-gradient(170deg, #e8e4f4 0%, #d8d0ec 100%)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Inconsolata:wght@300;400&display=swap');
html, body, [class*="css"] {{ font-family: 'Cormorant Garamond', serif; color: {text}; }}
[class*="css"] {{ background-color: {bg}; }}
html, body {{ background: {_bg_gradient}; background-attachment: fixed; }}
.stApp {{ background: {_bg_gradient} !important; background-attachment: fixed; min-height: 100vh; }}
.stTabs [data-baseweb="tab-list"] {{ background-color: {bg}; border-bottom: 1px solid {border}; gap: 0; }}
.stTabs [data-baseweb="tab"] {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: {dim}; padding: 0.6rem 1.2rem; }}
.stTabs [aria-selected="true"] {{ color: {gold} !important; border-bottom: 1px solid {gold} !important; }}
.main-title {{ font-size: 3.2rem; font-weight: 300; letter-spacing: 0.2em; text-transform: uppercase; color: {text}; margin-bottom: 0; line-height: 1; }}
.arabic-sub {{ font-size: 1.6rem; color: {muted}; letter-spacing: 0.05em; margin-top: 0.2rem; font-weight: 300; }}
.date-line {{ font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: {dim}; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.5rem; }}
.divider {{ border: none; border-top: 1px solid {border}; margin: 2rem 0; }}
.prayer-card {{ background: {card_bg}; border: 1px solid {border}; border-radius: 2px; padding: 1.4rem 1.8rem; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center; }}
.prayer-card.next {{ border-color: {gold}; background: {streak_bg}; }}
.prayer-name {{ font-size: 1.1rem; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; color: #c8b89a; }}
.prayer-name-arabic {{ font-size: 0.85rem; color: {dim}; margin-top: 0.1rem; }}
.prayer-time {{ font-family: 'Inconsolata', monospace; font-size: 1.3rem; color: {text}; font-weight: 300; }}
.next-badge {{ font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {gold}; letter-spacing: 0.2em; text-transform: uppercase; margin-left: 0.8rem; }}
.qibla-section {{ background: {card_bg}; border: 1px solid {border}; border-radius: 2px; padding: 2rem; text-align: center; margin-top: 1rem; }}
.qibla-degree {{ font-family: 'Inconsolata', monospace; font-size: 3rem; color: {gold}; font-weight: 300; line-height: 1; }}
.qibla-label {{ font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: {dim}; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.4rem; }}
.section-label {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {dim}; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 1rem; margin-top: 2rem; }}
.hijri-date {{ font-size: 1rem; color: {muted}; font-weight: 300; letter-spacing: 0.05em; }}
.surah-header {{ background: {card_bg}; border: 1px solid {border}; border-radius: 2px; padding: 1.8rem; text-align: center; margin-bottom: 1rem; }}
.surah-name-ar {{ font-size: 2.2rem; color: #c8b89a; font-weight: 300; line-height: 1.2; }}
.surah-name-en {{ font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: {dim}; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.4rem; }}
.surah-meta {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {very_dim}; margin-top: 0.3rem; letter-spacing: 0.1em; }}
.ayah-block {{ border-bottom: 1px solid {border}; padding: 1.4rem 0; }}
.ayah-arabic {{ font-size: 1.6rem; color: {text}; text-align: right; line-height: 2.2; font-weight: 300; direction: rtl; }}
.ayah-number {{ font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {gold}; letter-spacing: 0.15em; margin-bottom: 0.4rem; }}
.ayah-translit {{ font-size: 0.9rem; color: {dim}; line-height: 1.7; font-weight: 300; margin-top: 0.5rem; font-style: italic; letter-spacing: 0.02em; }}
.ayah-english {{ font-size: 0.95rem; color: {muted}; line-height: 1.7; font-weight: 300; margin-top: 0.4rem; font-style: italic; }}
.bismillah {{ font-size: 1.8rem; color: {gold}; text-align: center; padding: 1.5rem 0; direction: rtl; }}
.location-info {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {dim}; letter-spacing: 0.1em; margin-bottom: 0.5rem; }}
.dua-card {{ background: {card_bg}; border: 1px solid {border}; border-radius: 2px; padding: 1.6rem 1.8rem; margin-bottom: 0.8rem; }}
.dua-title {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {gold}; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.8rem; }}
.dua-arabic {{ font-size: 1.4rem; color: {text}; text-align: right; line-height: 2.1; font-weight: 300; direction: rtl; margin-bottom: 0.6rem; }}
.dua-translit {{ font-size: 0.85rem; color: {dim}; line-height: 1.7; font-style: italic; margin-bottom: 0.4rem; }}
.dua-english {{ font-size: 0.9rem; color: {muted}; line-height: 1.7; font-style: italic; }}
.streak-banner {{ background: {streak_bg}; border: 1px solid {gold}; border-radius: 2px; padding: 1.8rem; text-align: center; margin-bottom: 1rem; }}
.streak-number {{ font-family: 'Inconsolata', monospace; font-size: 3.5rem; color: {gold}; font-weight: 300; line-height: 1; }}
.streak-label {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {dim}; letter-spacing: 0.25em; text-transform: uppercase; margin-top: 0.4rem; }}
.tracker-card {{ background: {card_bg}; border: 1px solid {border}; border-radius: 2px; padding: 1.2rem 1.8rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }}
.tracker-card.done {{ border-color: {tracker_done_border}; background: {tracker_done_bg}; }}
.tracker-prayer-name {{ font-size: 1rem; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; color: #c8b89a; }}
.tracker-status {{ font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {very_dim}; letter-spacing: 0.15em; }}
.tracker-status.done {{ color: #4a8a4a; }}
.today-progress {{ font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: {dim}; letter-spacing: 0.1em; text-align: center; margin-bottom: 1rem; }}
.cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 0.5rem; }}
.cal-day {{ aspect-ratio: 1; border-radius: 2px; display: flex; align-items: center; justify-content: center; font-family: 'Inconsolata', monospace; font-size: 0.6rem; color: {dim}; }}
.cal-empty {{ aspect-ratio: 1; }}
.cal-0 {{ background: {card_bg}; border: 1px solid {border}; }}
.cal-1 {{ background: #1a2a1a; }}
.cal-2 {{ background: #1f3a1f; }}
.cal-3 {{ background: #254d25; }}
.cal-4 {{ background: #2a6a2a; }}
.cal-5 {{ background: #2e8b2e; }}
.cal-dow {{ font-family: 'Inconsolata', monospace; font-size: 0.55rem; color: {very_dim}; text-align: center; padding-bottom: 4px; }}
.cal-month-label {{ font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {dim}; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.5rem; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 3rem; max-width: 680px; }}
.countdown-card {{ background: {streak_bg}; border: 1px solid {border}; border-radius: 2px; padding: 1.2rem 1.8rem; margin: 0.5rem 0 1rem; display: flex; flex-direction: column; align-items: center; gap: 0.15rem; }}
.countdown-label {{ font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {dim}; letter-spacing: 0.2em; text-transform: uppercase; }}
.countdown-prayer-name {{ font-size: 1.05rem; color: #c8b89a; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; }}
.countdown-timer {{ font-family: 'Inconsolata', monospace; font-size: 2.6rem; color: {gold}; font-weight: 300; line-height: 1.1; letter-spacing: 0.05em; margin-top: 0.15rem; }}
.ramadan-banner {{ border-radius: 2px; padding: 1.4rem 1.8rem; margin-bottom: 1rem; text-align: center; border: 1px solid {ramadan_border_color}; background: {ramadan_bg}; }}
.ramadan-title {{ font-size: 1.4rem; font-weight: 300; letter-spacing: 0.15em; color: {ramadan_title_color}; margin-bottom: 0.2rem; }}
.ramadan-arabic {{ font-size: 1.1rem; color: {ramadan_arabic_color}; margin-bottom: 0.8rem; direction: rtl; }}
.ramadan-times {{ display: flex; justify-content: center; gap: 2.5rem; }}
.ramadan-time-block {{ text-align: center; }}
.ramadan-time-label {{ font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {dim}; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.2rem; }}
.ramadan-time-val {{ font-family: 'Inconsolata', monospace; font-size: 1.2rem; color: {ramadan_title_color}; font-weight: 300; }}
.ramadan-time-val.next {{ color: {gold}; }}
</style>
""", unsafe_allow_html=True)

ARABIC_NAMES = {
    "Fajr": "\u0627\u0644\u0641\u062c\u0631", "Sunrise": "\u0627\u0644\u0634\u0631\u0648\u0642",
    "Dhuhr": "\u0627\u0644\u0638\u0647\u0631", "Asr": "\u0627\u0644\u0639\u0635\u0631",
    "Maghrib": "\u0627\u0644\u0645\u063a\u0631\u0628", "Isha": "\u0627\u0644\u0639\u0634\u0627\u0621",
}
PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
TRACKED_PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Argentina", "Australia", "Austria", "Azerbaijan",
    "Bahrain", "Bangladesh", "Belgium", "Bosnia and Herzegovina", "Brazil", "Brunei",
    "Canada", "Chad", "China", "Comoros", "Denmark", "Djibouti", "Egypt", "Ethiopia",
    "Finland", "France", "Gambia", "Germany", "Ghana", "Guinea", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Italy", "Ivory Coast", "Japan", "Jordan", "Kazakhstan",
    "Kenya", "Kosovo", "Kuwait", "Kyrgyzstan", "Lebanon", "Libya", "Malaysia", "Maldives",
    "Mali", "Mauritania", "Morocco", "Mozambique", "Netherlands", "New Zealand", "Niger",
    "Nigeria", "Norway", "Oman", "Pakistan", "Palestine", "Philippines", "Qatar",
    "Russia", "Saudi Arabia", "Senegal", "Sierra Leone", "Somalia", "South Africa",
    "Spain", "Sudan", "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania",
    "Tunisia", "Turkey", "Turkmenistan", "UAE", "Uganda", "UK", "US", "Uzbekistan",
    "Yemen", "Zambia",
]

DUAS = {
    "Morning & Evening": [
        {"title": "Morning Remembrance", "arabic": "\u0623\u0635\u0628\u062d\u0646\u0627 \u0648\u0623\u0635\u0628\u062d \u0627\u0644\u0645\u0644\u0643 \u0644\u0644\u0647\u060c \u0648\u0627\u0644\u062d\u0645\u062f \u0644\u0644\u0647", "translit": "Asbahna wa asbahal mulku lillah, walhamdu lillah", "english": "We have entered the morning and the whole kingdom belongs to Allah. All praise is for Allah."},
        {"title": "Evening Remembrance", "arabic": "\u0623\u0645\u0633\u064a\u0646\u0627 \u0648\u0623\u0645\u0633\u0649 \u0627\u0644\u0645\u0644\u0643 \u0644\u0644\u0647\u060c \u0648\u0627\u0644\u062d\u0645\u062f \u0644\u0644\u0647", "translit": "Amsayna wa amsal mulku lillah, walhamdu lillah", "english": "We have entered the evening and the whole kingdom belongs to Allah. All praise is for Allah."},
        {"title": "Protection Morning & Evening", "arabic": "\u0627\u0644\u0644\u0647\u0645 \u0628\u0643 \u0623\u0635\u0628\u062d\u0646\u0627\u060c \u0648\u0628\u0643 \u0623\u0645\u0633\u064a\u0646\u0627\u060c \u0648\u0628\u0643 \u0646\u062d\u064a\u0627\u060c \u0648\u0628\u0643 \u0646\u0645\u0648\u062a \u0648\u0625\u0644\u064a\u0643 \u0627\u0644\u0646\u0634\u0648\u0631", "translit": "Allahumma bika asbahna, wa bika amsayna, wa bika nahya, wa bika namutu wa ilaykan-nushur", "english": "O Allah, by You we enter the morning, by You we enter the evening, by You we live, by You we die, and to You is the resurrection."},
    ],
    "Meals & Eating": [
        {"title": "Before Eating", "arabic": "\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650", "translit": "Bismillah", "english": "In the name of Allah."},
        {"title": "After Eating", "arabic": "\u0627\u0644\u062d\u0645\u062f \u0644\u0644\u0647 \u0627\u0644\u0630\u064a \u0623\u0637\u0639\u0645\u0646\u0627 \u0648\u0633\u0642\u0627\u0646\u0627 \u0648\u062c\u0639\u0644\u0646\u0627 \u0645\u0633\u0644\u0645\u064a\u0646", "translit": "Alhamdu lillahil-ladhi at'amana wa saqana wa ja'alana muslimin", "english": "All praise is for Allah who fed us, gave us drink, and made us Muslims."},
        {"title": "If You Forget Bismillah", "arabic": "\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u0623\u0648\u0651\u064e\u0644\u064e\u0647\u064f \u0648\u064f\u0622\u062e\u0650\u0631\u064e\u0647\u064f", "translit": "Bismillahi awwalahu wa akhirahu", "english": "In the name of Allah at the beginning and end of it."},
    ],
    "Sleep & Waking Up": [
        {"title": "Before Sleeping", "arabic": "\u0628\u0650\u0627\u0633\u0652\u0645\u0650\u0643\u064e \u0627\u0644\u0644\u0651\u064e\u0647\u064f\u0645\u0651\u064e \u0623\u0645\u0648\u062a\u064f \u0648\u0623\u062d\u064a\u0627", "translit": "Bismika Allahumma amutu wa ahya", "english": "In Your name, O Allah, I die and I live."},
        {"title": "Upon Waking Up", "arabic": "\u0627\u0644\u062d\u0645\u062f \u0644\u0644\u0647 \u0627\u0644\u0630\u064a \u0623\u062d\u064a\u0627\u0646\u0627 \u0628\u0639\u062f \u0645\u0627 \u0623\u0645\u0627\u062a\u0646\u0627 \u0648\u0625\u0644\u064a\u0647 \u0627\u0644\u0646\u0634\u0648\u0631", "translit": "Alhamdu lillahil-ladhi ahyana ba'da ma amatana wa ilayhin-nushur", "english": "All praise is for Allah who gave us life after having taken it from us, and unto Him is the resurrection."},
        {"title": "Dua Before Sleep", "arabic": "\u0627\u0644\u0644\u0647\u0645 \u0625\u0646\u064a \u0623\u0639\u0648\u0630 \u0628\u0643 \u0645\u0646 \u0627\u0644\u0634\u064a\u0637\u0627\u0646 \u0627\u0644\u0631\u062c\u064a\u0645", "translit": "Allahumma inni a'udhu bika minash-shaytanir-rajim", "english": "O Allah, I seek refuge in You from the accursed devil."},
    ],
    "Entering & Leaving Home": [
        {"title": "Entering the Home", "arabic": "\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u0648\u064e\u0644\u064e\u062c\u0652\u0646\u064e\u0627\u060c \u0648\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u062e\u064e\u0631\u064e\u062c\u0652\u0646\u064e\u0627\u060c \u0648\u0639\u064e\u0644\u0649 \u0627\u0644\u0644\u0647\u0650 \u0631\u064e\u0628\u0651\u0650\u0646\u064e\u0627 \u062a\u064e\u0648\u064e\u0643\u0651\u064e\u0644\u0652\u0646\u064e\u0627", "translit": "Bismillahi walajna, wa bismillahi kharajna, wa 'alallahi rabbina tawakkalna", "english": "In the name of Allah we enter, in the name of Allah we leave, and upon Allah our Lord we rely."},
        {"title": "Leaving the Home", "arabic": "\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650\u060c \u062a\u064e\u0648\u064e\u0643\u0651\u064e\u0644\u0652\u062a\u064f \u0639\u064e\u0644\u0649 \u0627\u0644\u0644\u0651\u064e\u0647\u0650\u060c \u0648\u0644\u0627 \u062d\u064e\u0648\u0652\u0644\u064e \u0648\u0644\u0627 \u0642\u064f\u0648\u0651\u064e\u0629\u064e \u0625\u0650\u0644\u0651\u064e\u0627 \u0628\u0650\u0627\u0644\u0644\u0651\u064e\u0647\u0650", "translit": "Bismillah, tawakkaltu 'alallah, wa la hawla wa la quwwata illa billah", "english": "In the name of Allah, I place my trust in Allah, and there is no power nor strength except with Allah."},
    ],
}

SURAHS = [
    (1,"Al-Fatiha","The Opening"),(2,"Al-Baqarah","The Cow"),(3,"Al-Imran","Family of Imran"),
    (4,"An-Nisa","The Women"),(5,"Al-Maidah","The Table Spread"),(6,"Al-Anam","The Cattle"),
    (7,"Al-Araf","The Heights"),(8,"Al-Anfal","The Spoils of War"),(9,"At-Tawbah","The Repentance"),
    (10,"Yunus","Jonah"),(11,"Hud","Hud"),(12,"Yusuf","Joseph"),(13,"Ar-Rad","The Thunder"),
    (14,"Ibrahim","Abraham"),(15,"Al-Hijr","The Rocky Tract"),(16,"An-Nahl","The Bee"),
    (17,"Al-Isra","The Night Journey"),(18,"Al-Kahf","The Cave"),(19,"Maryam","Mary"),
    (20,"Ta-Ha","Ta-Ha"),(21,"Al-Anbiya","The Prophets"),(22,"Al-Hajj","The Pilgrimage"),
    (23,"Al-Muminun","The Believers"),(24,"An-Nur","The Light"),(25,"Al-Furqan","The Criterion"),
    (26,"Ash-Shuara","The Poets"),(27,"An-Naml","The Ant"),(28,"Al-Qasas","The Stories"),
    (29,"Al-Ankabut","The Spider"),(30,"Ar-Rum","The Romans"),(31,"Luqman","Luqman"),
    (32,"As-Sajdah","The Prostration"),(33,"Al-Ahzab","The Combined Forces"),(34,"Saba","Sheba"),
    (35,"Fatir","Originator"),(36,"Ya-Sin","Ya Sin"),(37,"As-Saffat","Those Who Set The Ranks"),
    (38,"Sad","The Letter Sad"),(39,"Az-Zumar","The Troops"),(40,"Ghafir","The Forgiver"),
    (41,"Fussilat","Explained in Detail"),(42,"Ash-Shura","The Consultation"),(43,"Az-Zukhruf","The Ornaments of Gold"),
    (44,"Ad-Dukhan","The Smoke"),(45,"Al-Jathiyah","The Crouching"),(46,"Al-Ahqaf","The Wind-Curved Sandhills"),
    (47,"Muhammad","Muhammad"),(48,"Al-Fath","The Victory"),(49,"Al-Hujurat","The Rooms"),
    (50,"Qaf","The Letter Qaf"),(51,"Adh-Dhariyat","The Winnowing Winds"),(52,"At-Tur","The Mount"),
    (53,"An-Najm","The Star"),(54,"Al-Qamar","The Moon"),(55,"Ar-Rahman","The Beneficent"),
    (56,"Al-Waqiah","The Inevitable"),(57,"Al-Hadid","The Iron"),(58,"Al-Mujadila","The Pleading Woman"),
    (59,"Al-Hashr","The Exile"),(60,"Al-Mumtahanah","She That is to be Examined"),(61,"As-Saf","The Ranks"),
    (62,"Al-Jumuah","The Congregation"),(63,"Al-Munafiqun","The Hypocrites"),(64,"At-Taghabun","The Mutual Disillusion"),
    (65,"At-Talaq","The Divorce"),(66,"At-Tahrim","The Prohibition"),(67,"Al-Mulk","The Sovereignty"),
    (68,"Al-Qalam","The Pen"),(69,"Al-Haqqah","The Reality"),(70,"Al-Maarij","The Ascending Stairways"),
    (71,"Nuh","Noah"),(72,"Al-Jinn","The Jinn"),(73,"Al-Muzzammil","The Enshrouded One"),
    (74,"Al-Muddaththir","The Cloaked One"),(75,"Al-Qiyamah","The Resurrection"),(76,"Al-Insan","The Man"),
    (77,"Al-Mursalat","The Emissaries"),(78,"An-Naba","The Tidings"),(79,"An-Naziat","Those Who Drag Forth"),
    (80,"Abasa","He Frowned"),(81,"At-Takwir","The Overthrowing"),(82,"Al-Infitar","The Cleaving"),
    (83,"Al-Mutaffifin","The Defrauding"),(84,"Al-Inshiqaq","The Sundering"),(85,"Al-Buruj","The Mansions of the Stars"),
    (86,"At-Tariq","The Nightcommer"),(87,"Al-Ala","The Most High"),(88,"Al-Ghashiyah","The Overwhelming"),
    (89,"Al-Fajr","The Dawn"),(90,"Al-Balad","The City"),(91,"Ash-Shams","The Sun"),
    (92,"Al-Layl","The Night"),(93,"Ad-Duhaa","The Morning Hours"),(94,"Ash-Sharh","The Relief"),
    (95,"At-Tin","The Fig"),(96,"Al-Alaq","The Clot"),(97,"Al-Qadr","The Power"),
    (98,"Al-Bayyinah","The Clear Proof"),(99,"Az-Zalzalah","The Earthquake"),(100,"Al-Adiyat","The Courser"),
    (101,"Al-Qariah","The Calamity"),(102,"At-Takathur","The Rivalry in World Increase"),(103,"Al-Asr","The Declining Day"),
    (104,"Al-Humazah","The Traducer"),(105,"Al-Fil","The Elephant"),(106,"Quraysh","Quraysh"),
    (107,"Al-Maun","The Small Kindnesses"),(108,"Al-Kawthar","The Abundance"),(109,"Al-Kafirun","The Disbelievers"),
    (110,"An-Nasr","The Divine Support"),(111,"Al-Masad","The Palm Fiber"),(112,"Al-Ikhlas","The Sincerity"),
    (113,"Al-Falaq","The Daybreak"),(114,"An-Nas","The Mankind"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_location_from_ip():
    for url in ["https://ipapi.co/json/", "https://ip-api.com/json/?fields=city,country,lat,lon,timezone"]:
        try:
            r = requests.get(url, timeout=8)
            r.raise_for_status()
            d = r.json()
            city = d.get("city", "New York")
            country = d.get("country_name") or d.get("country", "US")
            lat = d.get("latitude") or d.get("lat", 40.7128)
            lon = d.get("longitude") or d.get("lon", -74.0060)
            tz = d.get("timezone", "America/New_York")
            if city and lat:
                return city, country, lat, lon, tz
        except:
            continue
    return "New York", "US", 40.7128, -74.0060, "America/New_York"

def get_data_by_city(city, country):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_data_by_coords(lat, lon):
    url = f"https://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=2"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_qibla(lat, lon):
    url = f"https://api.aladhan.com/v1/qibla/{lat}/{lon}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()["data"]["direction"]

def get_surah(number):
    url = f"https://api.alquran.cloud/v1/surah/{number}/editions/quran-uthmani,en.transliteration,en.sahih"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()["data"]

def to_12h(time_str):
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%-I:%M %p")
    except:
        return time_str

def find_next_prayer(timings, timezone_str):
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
    except:
        now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    for name in PRAYER_ORDER:
        if name in timings:
            t = datetime.strptime(timings[name], "%H:%M")
            if (t.hour * 60 + t.minute) > current_minutes:
                return name
    return "Fajr"

def compass_svg(degrees):
    rad = math.radians(degrees - 90)
    cx, cy, r = 70, 70, 55
    ax = cx + r * math.cos(rad)
    ay = cy + r * math.sin(rad)
    rad2 = math.radians(degrees + 90)
    tx = cx + 20 * math.cos(rad2)
    ty = cy + 20 * math.sin(rad2)
    return (
        '<svg width="140" height="140" viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="70" cy="70" r="65" fill="none" stroke="#1e1e1e" stroke-width="1"/>'
        '<circle cx="70" cy="70" r="3" fill="#4a4540"/>'
        '<text x="70" y="16" text-anchor="middle" font-family="Inconsolata,monospace" font-size="10" fill="#4a4540">N</text>'
        '<text x="70" y="132" text-anchor="middle" font-family="Inconsolata,monospace" font-size="10" fill="#4a4540">S</text>'
        '<text x="8" y="74" text-anchor="middle" font-family="Inconsolata,monospace" font-size="10" fill="#4a4540">W</text>'
        '<text x="132" y="74" text-anchor="middle" font-family="Inconsolata,monospace" font-size="10" fill="#4a4540">E</text>'
        f'<line x1="{tx}" y1="{ty}" x2="{ax}" y2="{ay}" stroke="#c8a96e" stroke-width="1.5" stroke-linecap="round"/>'
        f'<circle cx="{ax}" cy="{ay}" r="4" fill="#c8a96e"/>'
        '</svg>'
    )

def get_device_id():
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id

def load_prayer_log(device_id):
    try:
        res = supabase.table("prayer_log").select("*").eq("device_id", device_id).execute()
        log = {}
        for row in res.data:
            d = str(row["prayer_date"])
            if d not in log:
                log[d] = {}
            log[d][row["prayer_name"]] = row["prayed"]
        return log
    except:
        return {}

def set_prayer(device_id, prayer_date, prayer_name, prayed):
    try:
        supabase.table("prayer_log").upsert({
            "device_id": device_id,
            "prayer_date": str(prayer_date),
            "prayer_name": prayer_name,
            "prayed": prayed
        }, on_conflict="device_id,prayer_date,prayer_name").execute()
    except Exception as e:
        st.error(f"Could not save: {e}")

def is_prayer_done(log, prayer, d=None):
    if d is None:
        d = str(date.today())
    return log.get(d, {}).get(prayer, False)

def count_today(log):
    return sum(1 for p in TRACKED_PRAYERS if log.get(str(date.today()), {}).get(p, False))

def calculate_streak(log):
    streak = 0
    check_date = date.today()
    today_count = sum(1 for p in TRACKED_PRAYERS if log.get(str(check_date), {}).get(p, False))
    if today_count < 5:
        check_date -= timedelta(days=1)
    while True:
        key = str(check_date)
        day = log.get(key, {})
        if all(day.get(p, False) for p in TRACKED_PRAYERS):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

def render_calendar(log):
    today = date.today()
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    last_day = next_month - timedelta(days=1)
    first_day = today.replace(day=1)
    dow_labels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    dow_html = "".join(f'<div class="cal-dow">{d}</div>' for d in dow_labels)
    start_offset = first_day.weekday()
    empty_cells = "".join('<div class="cal-empty"></div>' for _ in range(start_offset))
    cells = ""
    for day_num in range(1, last_day.day + 1):
        d = str(today.replace(day=day_num))
        count = sum(1 for p in TRACKED_PRAYERS if log.get(d, {}).get(p, False))
        border = f"border: 1px solid {gold};" if day_num == today.day else ""
        cells += f'<div class="cal-day cal-{count}" style="{border}">{day_num}</div>'
    month_name = today.strftime("%B %Y")
    return (
        f'<p class="cal-month-label">{month_name}</p>'
        f'<div class="cal-grid">{dow_html}{empty_cells}{cells}</div>'
        f'<div style="display:flex;gap:6px;margin-top:0.8rem;align-items:center;">'
        f'<div class="cal-day cal-0" style="width:16px;height:16px;"></div><span style="font-family:Inconsolata,monospace;font-size:0.6rem;color:{very_dim};">0</span>'
        f'<div class="cal-day cal-2" style="width:16px;height:16px;"></div><span style="font-family:Inconsolata,monospace;font-size:0.6rem;color:{very_dim};">1-2</span>'
        f'<div class="cal-day cal-4" style="width:16px;height:16px;"></div><span style="font-family:Inconsolata,monospace;font-size:0.6rem;color:{very_dim};">3-4</span>'
        f'<div class="cal-day cal-5" style="width:16px;height:16px;"></div><span style="font-family:Inconsolata,monospace;font-size:0.6rem;color:{very_dim};">5</span>'
        f'</div>'
    )

# ── Header ────────────────────────────────────────────────────────────────────
now_utc = datetime.now()
col_title, col_theme = st.columns([6, 1])
with col_title:
    st.markdown('<p class="main-title">Salah</p>', unsafe_allow_html=True)
    st.markdown('<p class="arabic-sub">\u0623\u0648\u0642\u0627\u062a \u0627\u0644\u0635\u0644\u0627\u0629</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="date-line">{now_utc.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)
with col_theme:
    st.write("")
    st.write("")
    if st.button("☀️" if is_dark else "🌙", help="Toggle light/dark mode"):
        st.session_state.dark_mode = not is_dark
        st.rerun()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🕌 Prayer", "📿 Tracker", "🤲 Duas", "📖 Quran"])

# ════════════════════════════════════════════════════════════
# TAB 1 — PRAYER TIMES + QIBLA
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-label">Location</p>', unsafe_allow_html=True)
    use_gps = st.toggle("Use my current location", value=True)
    city, country, lat, lon, timezone_str = "New York", "US", 40.7128, -74.0060, "America/New_York"

    if use_gps:
        try:
            with st.spinner("Detecting location..."):
                city, country, lat, lon, timezone_str = get_location_from_ip()
            st.markdown(f'<p class="location-info">\u25cf  {city}, {country}</p>', unsafe_allow_html=True)
        except:
            st.warning("Could not detect location. Please enter manually.")
            use_gps = False

    if not use_gps:
        col1, col2 = st.columns([3, 2])
        with col1:
            city = st.text_input("City", value="New York", placeholder="e.g. London, Dubai, Karachi")
        with col2:
            country = st.selectbox("Country", COUNTRIES, index=COUNTRIES.index("US") if "US" in COUNTRIES else 0)

    try:
        with st.spinner(""):
            if use_gps:
                data = get_data_by_coords(lat, lon)
            else:
                data = get_data_by_city(city, country)
            timings = data["data"]["timings"]
            hijri = data["data"]["date"]["hijri"]
            meta = data["data"]["meta"]
            if not use_gps:
                lat = meta["latitude"]
                lon = meta["longitude"]
            timezone_str = meta.get("timezone", timezone_str)
            st.session_state["cached_timezone"] = timezone_str
            qibla_deg = get_qibla(lat, lon)

        hijri_str = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
        st.markdown(f'<p class="hijri-date">{hijri_str}</p>', unsafe_allow_html=True)

        # ── Ramadan banner ────────────────────────────────────────────
        is_ramadan = int(hijri.get("month", {}).get("number", 0)) == 9
        if is_ramadan:
            _suhoor_t = to_12h(timings.get("Fajr", "05:00"))
            _iftar_t  = to_12h(timings.get("Maghrib", "18:00"))
            try:
                _rtz   = pytz.timezone(timezone_str)
                _now_r = datetime.now(_rtz)
            except Exception:
                _now_r = datetime.now()
            _fajr_raw  = timings.get("Fajr", "05:00")
            _fajr_mins = int(_fajr_raw.split(":")[0]) * 60 + int(_fajr_raw.split(":")[1])
            _now_mins  = _now_r.hour * 60 + _now_r.minute
            _sc = "ramadan-time-val next" if _now_mins < _fajr_mins else "ramadan-time-val"
            _ic = "ramadan-time-val next" if _now_mins >= _fajr_mins else "ramadan-time-val"
            st.markdown(
                f'<div class="ramadan-banner">'
                f'<div class="ramadan-title">Ramadan Mubarak</div>'
                f'<div class="ramadan-arabic">\u0631\u0645\u0636\u0627\u0646 \u0645\u0628\u0627\u0631\u0643</div>'
                f'<div class="ramadan-times">'
                f'<div class="ramadan-time-block"><div class="ramadan-time-label">Suhoor ends</div>'
                f'<div class="{_sc}">{_suhoor_t}</div></div>'
                f'<div class="ramadan-time-block"><div class="ramadan-time-label">Iftar</div>'
                f'<div class="{_ic}">{_iftar_t}</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

        st.markdown('<p class="section-label">Prayer Times</p>', unsafe_allow_html=True)
        next_prayer = find_next_prayer(timings, timezone_str)

        # ── Countdown timer ───────────────────────────────────────────
        try:
            _ctz   = pytz.timezone(timezone_str)
            _now_c = datetime.now(_ctz)
        except Exception:
            _now_c = datetime.now()
        _nts     = timings.get(next_prayer, "00:00")
        _nh, _nm = int(_nts.split(":")[0]), int(_nts.split(":")[1])
        _ntgt    = _now_c.replace(hour=_nh, minute=_nm, second=0, microsecond=0)
        if _ntgt <= _now_c:
            _ntgt += timedelta(days=1)
        _tms     = int(_ntgt.timestamp() * 1000)
        _sdiff   = int((_ntgt - _now_c).total_seconds())
        _sh, _sr = divmod(_sdiff, 3600)
        _sm, _ss = divmod(_sr, 60)
        _static  = f"{_sh:02d}:{_sm:02d}:{_ss:02d}"
        import streamlit.components.v1 as components
        _card_bg  = "#131210" if is_dark else "#fdf6ec"
        _border_c = "#1e1e1e" if is_dark else "#e0d8d0"
        _dim_c    = "#4a4540" if is_dark else "#aaa099"
        components.html(f"""
<!DOCTYPE html><html><head><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:{_card_bg};border:1px solid {_border_c};border-radius:2px;
     display:flex;flex-direction:column;align-items:center;justify-content:center;
     height:100px;font-family:'Inconsolata',monospace;}}
.lbl{{font-size:0.62rem;color:{_dim_c};letter-spacing:0.2em;text-transform:uppercase;margin-bottom:2px;}}
.name{{font-size:1rem;color:#c8b89a;font-weight:400;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;}}
.cd{{font-size:2.4rem;color:#c8a96e;font-weight:300;line-height:1;letter-spacing:0.06em;}}
</style></head><body>
<div class="lbl">next prayer in</div>
<div class="name">{next_prayer}</div>
<div class="cd" id="cd">{_static}</div>
<script>
var t=new Date({_tms});
function tick(){{var d=t-Date.now();if(d<0)d=0;
  var h=Math.floor(d/3600000),m=Math.floor(d%3600000/60000),s=Math.floor(d%60000/1000);
  document.getElementById('cd').textContent=
    String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
}}
tick();setInterval(tick,1000);
</script></body></html>
""", height=108)

        for name in PRAYER_ORDER:
            if name not in timings:
                continue
            is_next = name == next_prayer
            card_class = "prayer-card next" if is_next else "prayer-card"
            badge = '<span class="next-badge">\u00b7 next</span>' if is_next else ""
            arabic = ARABIC_NAMES.get(name, "")
            time_12 = to_12h(timings[name])
            st.markdown(
                f'<div class="{card_class}">'
                f'<div><div class="prayer-name">{name}{badge}</div>'
                f'<div class="prayer-name-arabic">{arabic}</div></div>'
                f'<div class="prayer-time">{time_12}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown('<p class="section-label">Qibla Direction</p>', unsafe_allow_html=True)
        svg = compass_svg(qibla_deg)
        st.markdown(
            f'<div class="qibla-section">{svg}'
            f'<div class="qibla-degree">{qibla_deg:.1f}\u00b0</div>'
            f'<div class="qibla-label">from North \u00b7 toward Makkah</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    except requests.exceptions.ConnectionError:
        st.error("Could not connect. Please check your internet connection.")
    except Exception as e:
        st.error(f"Prayer times error: {e}")

# ════════════════════════════════════════════════════════════
# TAB 2 — TRACKER
# ════════════════════════════════════════════════════════════
with tab2:
    device_id = get_device_id()
    log = load_prayer_log(device_id)
    streak = calculate_streak(log)

    st.markdown(
        f'<div class="streak-banner">'
        f'<div class="streak-number">{streak}</div>'
        f'<div class="streak-label">day streak</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    selected_date = st.date_input(
        "Log prayers for:",
        value=date.today(),
        max_value=date.today(),
    )

    selected_count = sum(1 for p in TRACKED_PRAYERS if is_prayer_done(log, p, str(selected_date)))
    label = "today" if selected_date == date.today() else selected_date.strftime("%B %d")
    st.markdown(f'<p class="today-progress">{selected_count} of 5 prayers completed {label}</p>', unsafe_allow_html=True)

    for prayer in TRACKED_PRAYERS:
        done = is_prayer_done(log, prayer, str(selected_date))
        col1, col2 = st.columns([4, 1])
        with col1:
            card_class = "tracker-card done" if done else "tracker-card"
            status_class = "tracker-status done" if done else "tracker-status"
            checkmark = "\u2713 prayed" if done else "\u00b7 not yet"
            st.markdown(
                f'<div class="{card_class}">'
                f'<div class="tracker-prayer-name">{prayer}</div>'
                f'<div class="{status_class}">{checkmark}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            btn_label = "Undo" if done else "Prayed"
            if st.button(btn_label, key=f"track_{prayer}"):
                set_prayer(device_id, selected_date, prayer, not done)
                st.rerun()

    st.markdown('<p class="section-label">This Month</p>', unsafe_allow_html=True)
    st.markdown(render_calendar(log), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — DUAS
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-label">Daily Duas</p>', unsafe_allow_html=True)
    dua_category = st.selectbox("Dua category", list(DUAS.keys()), label_visibility="collapsed")
    for dua in DUAS[dua_category]:
        st.markdown(
            f'<div class="dua-card">'
            f'<div class="dua-title">{dua["title"]}</div>'
            f'<div class="dua-arabic">{dua["arabic"]}</div>'
            f'<div class="dua-translit">{dua["translit"]}</div>'
            f'<div class="dua-english">{dua["english"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ════════════════════════════════════════════════════════════
# TAB 4 — QURAN
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-label">Quran</p>', unsafe_allow_html=True)

    from streamlit_searchbox import st_searchbox

    def search_surahs(query):
        if not query:
            return [f"{n}. {name} \u2014 {meaning}" for n, name, meaning in SURAHS]
        return [
            f"{n}. {name} \u2014 {meaning}"
            for n, name, meaning in SURAHS
            if query.lower() in name.lower() or query.lower() in meaning.lower() or query == str(n)
        ]

    selected = st_searchbox(
        search_surahs,
        placeholder="Search surah by name, number, or meaning...",
        key="surah_search",
        default="1. Al-Fatiha \u2014 The Opening",
    )
    surah_number = int(selected.split(".")[0]) if selected else 1

    try:
        with st.spinner("Loading surah..."):
            editions = get_surah(surah_number)
            arabic_edition = editions[0]
            translit_edition = editions[1]
            english_edition = editions[2]

        surah_info = next((s for s in SURAHS if s[0] == surah_number), None)
        revelation = arabic_edition.get("revelationType", "")

        st.markdown(
            f'<div class="surah-header">'
            f'<div class="surah-name-ar">{arabic_edition["name"]}</div>'
            f'<div class="surah-name-en">{surah_info[1]} \u2014 {surah_info[2]}</div>'
            f'<div class="surah-meta">{arabic_edition["numberOfAyahs"]} verses \u00b7 {revelation}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if surah_number != 9:
            st.markdown('<div class="bismillah">\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u0651\u064e\u0647\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0652\u0645\u064e\u0670\u0646\u0650 \u0627\u0644\u0631\u0651\u064e\u062d\u0650\u064a\u0645\u0650</div>', unsafe_allow_html=True)

        for ar, tr, en in zip(arabic_edition["ayahs"], translit_edition["ayahs"], english_edition["ayahs"]):
            st.markdown(
                f'<div class="ayah-block">'
                f'<div class="ayah-number">Ayah {ar["numberInSurah"]}</div>'
                f'<div class="ayah-arabic">{ar["text"]}</div>'
                f'<div class="ayah-translit">{tr["text"]}</div>'
                f'<div class="ayah-english">{en["text"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    except Exception as e:
        st.error(f"Could not load surah: {e}")
