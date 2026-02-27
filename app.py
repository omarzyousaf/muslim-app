import streamlit as st
import requests
import time
import random as _random_module
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
# ✅ Ensure timezone is populated immediately so background gradient renders on first load
if "cached_timezone" not in st.session_state or st.session_state["cached_timezone"] in (None, "", "UTC"):
    try:
        city, country, lat, lon, timezone_str = get_location_from_ip()
        st.session_state["cached_timezone"] = timezone_str
        st.rerun()
    except Exception:
        st.session_state["cached_timezone"] = "America/New_York"


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
shadow      = "0 4px 12px rgba(0, 0, 0, 0.3)" if is_dark else "0 4px 12px rgba(0, 0, 0, 0.05)"

# Card elevation system
card_radius  = "16px"
card_shadow  = ("0 2px 12px rgba(0,0,0,0.28), 0 0 0 1px rgba(255,255,255,0.025)"
                if is_dark else
                "0 2px 8px rgba(0,0,0,0.055), 0 0 0 1px rgba(0,0,0,0.022)")
hover_shadow = ("0 6px 28px rgba(0,0,0,0.44), 0 0 0 1px rgba(255,255,255,0.04)"
                if is_dark else
                "0 6px 20px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.03)")

# Scholar chat surface colours
sc_user_bg     = ("linear-gradient(135deg,rgba(200,169,110,0.21),rgba(200,169,110,0.10))"
                  if is_dark else
                  "linear-gradient(135deg,rgba(180,145,75,0.16),rgba(200,169,110,0.07))")
sc_user_shadow = "0 2px 10px rgba(0,0,0,0.28)" if is_dark else "0 2px 8px rgba(0,0,0,0.07)"
sc_asst_bg     = "#131210" if is_dark else "#fafaf8"
sc_input_bg    = "#0e0e0e" if is_dark else "#f7f4ef"

ramadan_border_color = "#c8692e" if is_dark else "#d4783a"
ramadan_title_color  = "#e8a05a" if is_dark else "#7a3010"
ramadan_arabic_color = "#c8692e" if is_dark else "#a04820"
ramadan_bg = "linear-gradient(135deg, #1a0d0a 0%, #2a1505 100%)" if is_dark else "linear-gradient(135deg, #fdf6ed 0%, #faecd8 100%)"

_cached_tz = st.session_state.get("cached_timezone", "America/New_York") or "America/New_York"
try:
    _tz = pytz.timezone(_cached_tz)
    _local_now = datetime.now(_tz)
except Exception:
    _local_now = datetime.now()
_h = _local_now.hour

# Time-of-day phase (used for dawn/sunset nuance on clear skies)
if 4 <= _h < 7:
    phase = "dawn"
elif 7 <= _h < 16:
    phase = "day"
elif 16 <= _h < 19:
    phase = "sunset"
else:
    phase = "night"

# ── Weather-reactive background ──────────────────────────────────────────────
_wcache  = st.session_state.get("cached_weather", {})
_wcode   = int(_wcache.get("weathercode", 0))
_wis_day = int(_wcache.get("is_day", 1 if phase in ("dawn", "day") else 0))
# Open-Meteo's is_day is binary (0 before astronomical sunrise).
# Dawn and sunset are transitional — always treat as "lit" so the
# correct dawn/sunset gradient renders even at 5:19am.
if phase in ("dawn", "sunset"):
    _wis_day = 1

# WMO code → condition label
if _wcode == 0:
    _wcond = "clear"
elif _wcode in (1, 2, 3):
    _wcond = "cloudy"
elif _wcode in (45, 48):
    _wcond = "fog"
elif _wcode in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
    _wcond = "rain"
elif _wcode in (71, 73, 75, 77):
    _wcond = "snow"
elif _wcode in (95, 96, 99):
    _wcond = "thunderstorm"
else:
    _wcond = "cloudy"

# Gradient: weather condition × day/night × dark/light theme
if _wcond == "clear":
    if _wis_day:
        if phase == "dawn":
            _bg_gradient = ("linear-gradient(180deg, #1a0838 0%, #7b3460 32%, #e8835a 68%, #f5c07a 100%)"
                            if is_dark else
                            "linear-gradient(180deg, #d4bae8 0%, #f0c8a0 50%, #fae0b8 100%)")
        elif phase == "sunset":
            _bg_gradient = ("linear-gradient(180deg, #0a0420 0%, #3d0e55 25%, #8a1e5e 55%, #de5818 82%, #f08838 100%)"
                            if is_dark else
                            "linear-gradient(180deg, #e0a0c8 0%, #f0b870 45%, #fad090 100%)")
        else:
            _bg_gradient = ("linear-gradient(180deg, #0a4fa0 0%, #1878d0 40%, #35a0e8 72%, #78cdf0 100%)"
                            if is_dark else
                            "linear-gradient(180deg, #c8dff8 0%, #d8eafe 50%, #eaf5ff 100%)")
    else:
        _bg_gradient = ("linear-gradient(180deg, #020408 0%, #050a1a 30%, #080f30 62%, #0c1438 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #1a1e38 0%, #242848 50%, #2c3258 100%)")
elif _wcond == "cloudy":
    if _wis_day:
        _bg_gradient = ("linear-gradient(180deg, #3a5060 0%, #5a7585 38%, #7a9aa8 70%, #a8c0ca 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #b8cad4 0%, #ccdae0 50%, #dde8ec 100%)")
    else:
        _bg_gradient = ("linear-gradient(180deg, #080c10 0%, #121a20 40%, #1a2430 72%, #20293a 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #28303a 0%, #323c48 50%, #3a4452 100%)")
elif _wcond == "fog":
    if _wis_day:
        _bg_gradient = ("linear-gradient(180deg, #909aa5 0%, #b0b8c2 40%, #c8d0d8 72%, #dde4ea 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #c8cfd5 0%, #d8dfe5 50%, #e8eef2 100%)")
    else:
        _bg_gradient = ("linear-gradient(180deg, #181c20 0%, #22282e 50%, #2a3038 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #303840 0%, #3a4248 50%, #424a52 100%)")
elif _wcond == "rain":
    if _wis_day:
        _bg_gradient = ("linear-gradient(180deg, #182535 0%, #253848 40%, #324e62 70%, #405a70 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #8090a0 0%, #9aacba 50%, #b0c0cc 100%)")
    else:
        _bg_gradient = ("linear-gradient(180deg, #04080e 0%, #080e18 40%, #0c1420 72%, #101828 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #1c2430 0%, #242c3a 50%, #2c3442 100%)")
elif _wcond == "snow":
    if _wis_day:
        _bg_gradient = ("linear-gradient(180deg, #7a8a98 0%, #98a8b5 40%, #bac8d2 70%, #d5e0e8 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #c8d4dc 0%, #d8e2e8 50%, #e8eef2 100%)")
    else:
        _bg_gradient = ("linear-gradient(180deg, #060c18 0%, #0c1425 40%, #121c30 72%, #182040 100%)"
                        if is_dark else
                        "linear-gradient(180deg, #1e2840 0%, #28324a 50%, #303a52 100%)")
elif _wcond == "thunderstorm":
    _bg_gradient = ("linear-gradient(180deg, #040208 0%, #0c0815 32%, #150e20 65%, #18102a 100%)"
                    if is_dark else
                    "linear-gradient(180deg, #1a1828 0%, #222030 50%, #2a2838 100%)")
else:
    _bg_gradient = ("linear-gradient(180deg, #122b59 0%, #1f4e8a 50%, #4784ba 100%)"
                    if is_dark else
                    "linear-gradient(180deg, #c8dff8 0%, #d8eafe 50%, #eaf5ff 100%)")

# ── Build weather particle overlay HTML (seeded RNG → stable positions) ──────
_prng = _random_module.Random(12345)
_overlay_html = '<div class="weather-overlay">'

if _wcond == "clear" and _wis_day:
    _overlay_html += '<div class="wx-sun"></div>'
    for _ct, _cw, _ch, _cc, _cd, _cdl in [
        ("8%",  "300px", "72px", "rgba(255,255,255,0.10)", "90s",  "-18s"),
        ("22%", "220px", "55px", "rgba(255,255,255,0.07)", "122s", "-55s"),
        ("14%", "165px", "42px", "rgba(255,255,255,0.06)", "108s", "-82s"),
    ]:
        _overlay_html += (f'<div class="wx-cloud" style="top:{_ct};width:{_cw};height:{_ch};'
                          f'background:{_cc};animation-duration:{_cd};animation-delay:{_cdl};left:-30%;"></div>')

elif _wcond == "clear" and not _wis_day:
    for _ in range(110):
        _sx  = _prng.randint(0, 100)
        _sy  = _prng.randint(0, 72)
        _ssz = round(_prng.uniform(1.0, 2.8), 1)
        _sop = round(_prng.uniform(0.35, 0.95), 2)
        _sdl = round(_prng.uniform(0, 8), 1)
        _sdr = round(_prng.uniform(3.5, 9.0), 1)   # slower twinkle = calmer night sky
        _overlay_html += (f'<div class="wx-star" style="left:{_sx}%;top:{_sy}%;'
                          f'width:{_ssz}px;height:{_ssz}px;'
                          f'--star-op:{_sop};animation-delay:{_sdl}s;animation-duration:{_sdr}s;"></div>')

elif _wcond == "cloudy":
    _cop = "0.14" if _wis_day else "0.07"
    _cc  = f"rgba(200,210,220,{_cop})" if _wis_day else f"rgba(55,65,75,{_cop})"
    for _ct, _cw, _ch, _cd, _cdl in [
        ("5%",  "400px", "95px", "95s",  "-12s"),
        ("26%", "280px", "68px", "138s", "-50s"),
        ("16%", "210px", "58px", "116s", "-78s"),
        ("38%", "170px", "48px", "128s", "-35s"),
    ]:
        _overlay_html += (f'<div class="wx-cloud" style="top:{_ct};width:{_cw};height:{_ch};'
                          f'background:{_cc};animation-duration:{_cd};animation-delay:{_cdl};left:-42%;"></div>')

elif _wcond == "fog":
    for _ft, _fh, _fd, _fdl in [
        ("18%", "95px",  "7s",  "0s"),
        ("36%", "72px",  "10s", "1.5s"),
        ("52%", "82px",  "8s",  "3.2s"),
        ("66%", "65px",  "12s", "0.8s"),
        ("78%", "78px",  "9s",  "5s"),
        ("8%",  "58px",  "6s",  "2.5s"),
        ("44%", "60px",  "11s", "4s"),
    ]:
        _overlay_html += f'<div class="wx-mist" style="top:{_ft};height:{_fh};animation-duration:{_fd};animation-delay:{_fdl};"></div>'

elif _wcond in ("rain", "thunderstorm"):
    # More drops, wider delay range, longer durations → smooth iOS-like curtain
    for _ in range(100):
        _rx  = _prng.randint(-8, 108)
        _rdl = round(_prng.uniform(0, 4.0), 2)    # wider stagger = no wave effect
        _rdr = round(_prng.uniform(0.65, 1.25), 2) # slower = longer visible streaks
        _rh  = _prng.randint(70, 130)
        _rop = round(_prng.uniform(0.20, 0.55), 2)
        _overlay_html += (f'<div class="wx-rain" style="left:{_rx}%;'
                          f'animation-delay:{_rdl}s;animation-duration:{_rdr}s;'
                          f'height:{_rh}px;opacity:{_rop};"></div>')
    if _wcond == "thunderstorm":
        _overlay_html += '<div class="wx-lightning" style="--lt-dur:9s;--lt-delay:0s;"></div>'
        _overlay_html += '<div class="wx-lightning" style="--lt-dur:13s;--lt-delay:4.7s;"></div>'
        _overlay_html += '<div class="wx-lightning" style="--lt-dur:7s;--lt-delay:2.1s;"></div>'

elif _wcond == "snow":
    for _ in range(70):
        _fnx  = _prng.randint(0, 100)
        _fnsz = round(_prng.uniform(3, 9), 1)
        _fndl = round(_prng.uniform(0, 12), 1)
        _fndr = round(_prng.uniform(5, 14), 1)
        _fndf = _prng.randint(-70, 70)
        _overlay_html += (f'<div class="wx-snow" style="left:{_fnx}%;'
                          f'width:{_fnsz}px;height:{_fnsz}px;'
                          f'animation-delay:{_fndl}s;animation-duration:{_fndr}s;'
                          f'--snow-drift:{_fndf}px;"></div>')

_overlay_html += '</div>'

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Inconsolata:wght@300;400&display=swap');

/* --- Animations & Global --- */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
html, body, [class*="css"] {{ font-family: 'Cormorant Garamond', serif; color: {text}; }}
html, body {{
    background: {_bg_gradient} !important;
    background-attachment: fixed;
    min-height: 100vh;
}}

.stApp {{
    background: transparent !important;
}}


/* ══════════════════════════════════════════════════════
   WEATHER PARTICLE OVERLAY
   ══════════════════════════════════════════════════════ */
.weather-overlay {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 1;
    overflow: hidden;
}}

/* ── Keyframes ───────────────────────────────────────── */
@keyframes sun-glow {{
    0%, 100% {{
        box-shadow: 0 0 60px 20px rgba(255,218,68,0.32),
                    0 0 140px 55px rgba(255,175,20,0.14),
                    0 0 280px 110px rgba(255,140,0,0.06);
    }}
    50% {{
        box-shadow: 0 0 85px 35px rgba(255,218,68,0.48),
                    0 0 200px 85px rgba(255,175,20,0.22),
                    0 0 400px 170px rgba(255,140,0,0.10);
    }}
}}

@keyframes wx-twinkle {{
    0%, 100% {{ opacity: var(--star-op, 0.7); transform: scale(1); }}
    45%       {{ opacity: calc(var(--star-op, 0.7) * 0.20); transform: scale(0.82); }}
}}

@keyframes wx-rain-fall {{
    0%   {{ transform: translateY(-150px); opacity: 0; }}
    6%   {{ opacity: 1; }}
    90%  {{ opacity: 1; }}
    100% {{ transform: translateY(110vh); opacity: 0; }}
}}

@keyframes wx-snow-fall {{
    0%   {{ transform: translateY(-20px) translateX(0px) rotate(0deg); opacity: 0.9; }}
    100% {{ transform: translateY(110vh) translateX(var(--snow-drift,40px)) rotate(600deg); opacity: 0.2; }}
}}

@keyframes wx-lightning {{
    0%, 86%, 100% {{ opacity: 0; }}
    87%  {{ opacity: 0.85; }}
    88%  {{ opacity: 0; }}
    89%  {{ opacity: 0.60; }}
    90%  {{ opacity: 0; }}
    91%  {{ opacity: 0.32; }}
    92%  {{ opacity: 0; }}
}}

@keyframes wx-mist {{
    0%   {{ transform: translateX(-14%) scaleY(1.00); opacity: 0.28; }}
    50%  {{ transform: translateX( 14%) scaleY(1.35); opacity: 0.55; }}
    100% {{ transform: translateX(-14%) scaleY(1.00); opacity: 0.28; }}
}}

@keyframes wx-cloud-drift {{
    from {{ transform: translateX(0); }}
    to   {{ transform: translateX(135vw); }}
}}

/* ── Sun ─────────────────────────────────────────────── */
.wx-sun {{
    position: absolute;
    width: 115px; height: 115px;
    border-radius: 50%;
    background: radial-gradient(circle at 42% 42%,
        #fffde0 0%, #ffe566 28%, #ffb830 62%, rgba(255,140,0,0) 100%);
    top: 7%; right: 12%;
    animation: sun-glow 5s ease-in-out infinite;
}}

/* ── Stars ───────────────────────────────────────────── */
.wx-star {{
    position: absolute;
    border-radius: 50%;
    background: #ffffff;
    animation: wx-twinkle var(--star-dur, 3s) ease-in-out infinite;
    animation-delay: var(--star-delay, 0s);
    opacity: var(--star-op, 0.7);
}}

/* ── Rain streaks — iOS-style long smooth streaks ────── */
.wx-rain {{
    position: absolute;
    top: -220px;
    width: 1.5px;
    height: 110px;
    background: linear-gradient(
        to bottom,
        transparent 0%,
        rgba(180, 210, 245, 0.35) 30%,
        rgba(200, 228, 255, 0.65) 65%,
        rgba(210, 235, 255, 0.50) 85%,
        transparent 100%
    );
    border-radius: 2px;
    animation: wx-rain-fall linear infinite;
    transform: rotate(14deg);
    transform-origin: top center;
    will-change: transform;
}}

/* ── Snowflakes ──────────────────────────────────────── */
.wx-snow {{
    position: absolute;
    top: -15px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.88);
    animation: wx-snow-fall ease-in infinite;
    filter: blur(0.4px);
}}

/* ── Lightning flash ─────────────────────────────────── */
.wx-lightning {{
    position: absolute;
    inset: 0;
    background: rgba(195, 210, 255, 0.88);
    animation: wx-lightning var(--lt-dur, 9s) ease-in-out var(--lt-delay, 0s) infinite;
    opacity: 0;
}}

/* ── Mist layers ─────────────────────────────────────── */
.wx-mist {{
    position: absolute;
    left: -22%; width: 144%;
    border-radius: 55%;
    filter: blur(22px);
    background: linear-gradient(
        90deg,
        transparent,
        rgba(225, 235, 248, 0.42),
        rgba(215, 228, 245, 0.65),
        rgba(225, 235, 248, 0.42),
        transparent
    );
    animation: wx-mist ease-in-out infinite;
}}

/* ── CSS clouds ──────────────────────────────────────── */
.wx-cloud {{
    position: absolute;
    border-radius: 55px;
    filter: blur(8px);
    animation: wx-cloud-drift linear infinite;
}}
.wx-cloud::before,
.wx-cloud::after {{
    content: '';
    position: absolute;
    background: inherit;
    border-radius: 50%;
}}
.wx-cloud::before {{ width: 58%; height: 155%; top: -42%; left: 16%; }}
.wx-cloud::after  {{ width: 38%; height: 125%; top: -32%; right: 16%; }}

/* App content sits above weather overlay */
.block-container {{
    position: relative;
    z-index: 2;
}}

/* ═══ App Chrome ═══════════════════════════════════════════════════════════ */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding-top: 3.5rem !important;
    padding-bottom: 5rem !important;
    max-width: 700px !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}}

/* ═══ Tab Bar — native-app feel ════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    background: {"rgba(9,9,9,0.88)" if is_dark else "rgba(248,245,241,0.92)"};
    border-bottom: 1px solid {border};
    gap: 0;
    padding: 0 0.25rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}}
.stTabs [data-baseweb="tab-panel"] {{
    animation: fadeIn 0.35s ease-out;
    padding-top: 2rem;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Inconsolata', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: {dim};
    padding: 1.05rem 1.2rem;
    border-bottom: 2px solid transparent;
    background: transparent;
    transition: color 0.2s ease, border-color 0.2s ease;
}}
.stTabs [aria-selected="true"] {{
    color: {text} !important;
    border-bottom: 2px solid {gold} !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {muted} !important; }}

/* ═══ Typography ════════════════════════════════════════════════════════════ */
.main-title {{
    font-size: 3.4rem; font-weight: 200; letter-spacing: 0.25em;
    text-transform: uppercase; color: {text}; margin-bottom: 0; line-height: 1;
}}
.arabic-sub {{
    font-size: 1.5rem; color: {muted}; letter-spacing: 0.08em;
    margin-top: 0.4rem; font-weight: 300; line-height: 1.4;
}}
.date-line {{
    font-family: 'Inconsolata', monospace; font-size: 0.67rem; color: {dim};
    letter-spacing: 0.18em; text-transform: uppercase; margin-top: 0.7rem;
}}
.clock-wrap {{
    display: flex; flex-direction: column;
    align-items: flex-end; justify-content: flex-start; padding-top: 0.1rem;
}}
.clock-time {{
    font-family: 'Inconsolata', monospace; font-size: 2.8rem; font-weight: 200;
    letter-spacing: 0.04em; color: {text}; line-height: 1; margin: 0;
}}
.clock-loc {{
    font-family: 'Inconsolata', monospace; font-size: 0.56rem; color: {dim};
    letter-spacing: 0.24em; text-transform: uppercase; margin-top: 0.5rem;
}}
.divider {{ border: none; border-top: 1px solid {border}; margin: 2.5rem 0; }}
.section-label {{
    font-family: 'Inconsolata', monospace; font-size: 0.6rem; color: {dim};
    letter-spacing: 0.32em; text-transform: uppercase;
    margin-bottom: 1.25rem; margin-top: 2.75rem;
}}
.hijri-date {{ font-size: 1rem; color: {muted}; font-weight: 300; letter-spacing: 0.06em; }}
.location-info {{
    font-family: 'Inconsolata', monospace; font-size: 0.67rem; color: {dim};
    letter-spacing: 0.1em; margin-bottom: 0.75rem;
}}
.bismillah {{ font-size: 1.9rem; color: {gold}; text-align: center; padding: 1.75rem 0; direction: rtl; opacity: 0.88; }}

/* ═══ Card System — 16px radius, layered shadows, hover lift ════════════════ */
.prayer-card {{
    background: {card_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 1.5rem 1.8rem; margin-bottom: 0.75rem;
    display: flex; justify-content: space-between; align-items: center;
    transition: box-shadow 0.22s ease, transform 0.22s ease;
}}
.prayer-card:hover {{ box-shadow: {hover_shadow}; transform: translateY(-1px); }}
.prayer-card.next {{ border-color: rgba(200,169,110,0.45); background: {streak_bg}; }}

.qibla-section {{
    background: {card_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 2.25rem 2rem; text-align: center; margin-top: 1.25rem;
}}
.surah-header {{
    background: {card_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 2rem; text-align: center; margin-bottom: 1.25rem;
}}
.ayah-block {{
    background: {card_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 1.5rem 1.8rem; margin-bottom: 1rem;
    transition: box-shadow 0.2s ease;
}}
.ayah-block:hover {{ box-shadow: {hover_shadow}; }}
.dua-card {{
    background: {card_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 1.75rem 1.8rem; margin-bottom: 1rem;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}}
.dua-card:hover {{ box-shadow: {hover_shadow}; transform: translateY(-1px); }}
.streak-banner {{
    background: {streak_bg}; border: 1px solid rgba(200,169,110,0.18);
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 2rem; text-align: center; margin-bottom: 1.25rem;
}}
.tracker-card {{
    background: {card_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 1.25rem 1.8rem; margin-bottom: 0.6rem;
    display: flex; justify-content: space-between; align-items: center;
    transition: box-shadow 0.2s ease;
}}
.tracker-card.done {{ border-color: {tracker_done_border}; background: {tracker_done_bg}; }}
.countdown-card {{
    background: {streak_bg}; border: 1px solid {border};
    border-radius: {card_radius}; box-shadow: {card_shadow};
    padding: 1.4rem 1.8rem; margin: 0.75rem 0 1.25rem;
    display: flex; flex-direction: column; align-items: center; gap: 0.2rem;
}}
.ramadan-banner {{
    border-radius: {card_radius}; padding: 1.6rem 1.8rem; margin-bottom: 1.25rem;
    text-align: center; border: 1px solid {ramadan_border_color};
    background: {ramadan_bg}; box-shadow: {card_shadow};
}}

/* ═══ Audio Player ══════════════════════════════════════════════════════════ */
.play-btn {{
    background: none; border: none; color: {dim};
    font-size: 1.1rem; cursor: pointer;
    transition: all 0.2s ease; padding: 0 0.5rem;
}}
.play-btn:hover {{ color: {gold}; transform: scale(1.1); }}
.playing-ayah {{
    border-color: rgba(200,169,110,0.4) !important;
    background-color: {"#1e1908" if is_dark else "#fdf3e1"} !important;
    box-shadow: 0 0 20px rgba(200,169,110,0.12) !important;
    transition: all 0.4s ease;
}}

/* ═══ Prayer Component ══════════════════════════════════════════════════════ */
.prayer-name {{
    font-size: 1rem; font-weight: 300; letter-spacing: 0.12em;
    text-transform: uppercase; color: {text}; opacity: 0.85;
}}
.prayer-name-arabic {{ font-size: 0.88rem; color: {muted}; margin-top: 0.15rem; }}
.prayer-time {{
    font-family: 'Inconsolata', monospace; font-size: 1.35rem;
    color: {text}; font-weight: 300; letter-spacing: 0.03em;
}}
.next-badge {{
    font-family: 'Inconsolata', monospace; font-size: 0.6rem; color: {gold};
    letter-spacing: 0.22em; text-transform: uppercase; margin-left: 0.75rem; opacity: 0.9;
}}
.qibla-degree {{
    font-family: 'Inconsolata', monospace; font-size: 3rem;
    color: {gold}; font-weight: 200; line-height: 1;
}}
.qibla-label {{
    font-family: 'Inconsolata', monospace; font-size: 0.68rem; color: {dim};
    letter-spacing: 0.22em; text-transform: uppercase; margin-top: 0.5rem;
}}

/* ═══ Quran Component ═══════════════════════════════════════════════════════ */
.surah-name-ar {{ font-size: 2.2rem; color: {text}; font-weight: 300; line-height: 1.25; opacity: 0.9; }}
.surah-name-en {{
    font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: {dim};
    letter-spacing: 0.22em; text-transform: uppercase; margin-top: 0.5rem;
}}
.surah-meta {{
    font-family: 'Inconsolata', monospace; font-size: 0.65rem;
    color: {very_dim}; margin-top: 0.35rem; letter-spacing: 0.1em;
}}
.ayah-number {{
    font-family: 'Inconsolata', monospace; font-size: 0.62rem;
    color: {gold}; letter-spacing: 0.18em; margin-bottom: 0.5rem; opacity: 0.7;
}}
.ayah-arabic {{
    font-size: 2.0rem; color: {text}; text-align: right;
    line-height: 2.25; font-weight: 300; direction: rtl;
}}
.ayah-translit {{
    font-size: 0.8rem; color: {dim}; line-height: 1.75; font-weight: 300;
    margin-top: 0.6rem; font-style: italic; letter-spacing: 0.02em;
}}
.ayah-english {{
    font-size: 0.88rem; color: {muted}; line-height: 1.75;
    font-weight: 300; margin-top: 0.45rem; font-style: italic;
}}

/* ═══ Duas Component ════════════════════════════════════════════════════════ */
.dua-title {{
    font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {gold};
    letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 1rem; opacity: 0.85;
}}
.dua-arabic {{
    font-size: 1.8rem; color: {text}; text-align: right;
    line-height: 2.15; font-weight: 300; direction: rtl; margin-bottom: 0.75rem;
}}
.dua-translit {{ font-size: 0.8rem; color: {dim}; line-height: 1.75; font-style: italic; margin-bottom: 0.5rem; }}
.dua-english {{ font-size: 0.88rem; color: {muted}; line-height: 1.75; font-style: italic; }}

/* ═══ Tracker Component ═════════════════════════════════════════════════════ */
.streak-number {{
    font-family: 'Inconsolata', monospace; font-size: 3.5rem;
    color: {gold}; font-weight: 200; line-height: 1;
}}
.streak-label {{
    font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {dim};
    letter-spacing: 0.28em; text-transform: uppercase; margin-top: 0.5rem;
}}
.tracker-prayer-name {{
    font-size: 0.95rem; font-weight: 300; letter-spacing: 0.12em;
    text-transform: uppercase; color: {text}; opacity: 0.85;
}}
.tracker-status {{
    font-family: 'Inconsolata', monospace; font-size: 0.65rem;
    color: {very_dim}; letter-spacing: 0.18em;
}}
.tracker-status.done {{ color: #4a8a4a; }}
.today-progress {{
    font-family: 'Inconsolata', monospace; font-size: 0.72rem; color: {dim};
    letter-spacing: 0.12em; text-align: center; margin-bottom: 1.25rem;
}}

/* ═══ Calendar ══════════════════════════════════════════════════════════════ */
.cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 0.5rem; }}
.cal-day {{
    aspect-ratio: 1; border-radius: 6px; display: flex; align-items: center;
    justify-content: center; font-family: 'Inconsolata', monospace; font-size: 0.6rem; color: {dim};
}}
.cal-empty {{ aspect-ratio: 1; }}
.cal-0 {{ background: {card_bg}; border: 1px solid {border}; }}
.cal-1 {{ background: #1a2a1a; }} .cal-2 {{ background: #1f3a1f; }}
.cal-3 {{ background: #254d25; }} .cal-4 {{ background: #2a6a2a; }} .cal-5 {{ background: #2e8b2e; }}
.cal-dow {{ font-family: 'Inconsolata', monospace; font-size: 0.55rem; color: {very_dim}; text-align: center; padding-bottom: 4px; }}
.cal-month-label {{
    font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {dim};
    letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 0.5rem;
}}

/* ═══ Hadith Card ═══════════════════════════════════════════════════════════ */
.hadith-card {{
    background: {"rgba(12,9,5,0.92)" if is_dark else "rgba(255,253,248,0.96)"};
    border: 1px solid {"rgba(200,169,110,0.10)" if is_dark else "rgba(200,169,110,0.12)"};
    border-left: 2px solid rgba(200,169,110,0.55);
    border-radius: 0 {card_radius} {card_radius} 0;
    box-shadow: {card_shadow};
    padding: 2rem 2.2rem 1.8rem 2rem;
    margin-bottom: 0.75rem;
    position: relative;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}
.hadith-label {{
    font-family: 'Inconsolata', monospace; font-size: 0.58rem; color: {gold};
    letter-spacing: 0.35em; text-transform: uppercase; margin-bottom: 1.25rem;
    display: block; opacity: 0.72;
}}
.hadith-quote-mark {{
    font-family: Georgia, serif; font-size: 4rem; color: {gold};
    line-height: 0.6; display: block; margin-bottom: 0.75rem;
    opacity: 0.38; user-select: none;
}}
.hadith-text {{
    font-family: 'Cormorant Garamond', serif; font-size: 1.18rem; line-height: 1.95;
    color: {"#d8ccb8" if is_dark else "#2a2018"}; font-weight: 300; font-style: italic; margin: 0;
}}
.hadith-ref {{
    font-family: 'Inconsolata', monospace; font-size: 0.6rem; color: {muted};
    letter-spacing: 0.1em; text-align: right; margin-top: 1.35rem; display: block; opacity: 0.62;
}}

/* ═══ Ramadan Banner ════════════════════════════════════════════════════════ */
.ramadan-title {{ font-size: 1.4rem; font-weight: 300; letter-spacing: 0.15em; color: {ramadan_title_color}; margin-bottom: 0.2rem; }}
.ramadan-arabic {{ font-size: 1.1rem; color: {ramadan_arabic_color}; margin-bottom: 0.8rem; direction: rtl; }}
.ramadan-times {{ display: flex; justify-content: center; gap: 2.5rem; }}
.ramadan-time-block {{ text-align: center; }}
.ramadan-time-label {{ font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: {dim}; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.2rem; }}
.ramadan-time-val {{ font-family: 'Inconsolata', monospace; font-size: 1.2rem; color: {ramadan_title_color}; font-weight: 300; }}
.ramadan-time-val.next {{ color: {gold}; }}

/* ═══ Default Streamlit Buttons — minimal transparent pill ═════════════════ */
div.stButton > button {{
    font-family: 'Inconsolata', monospace !important;
    font-size: 0.64rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    border-radius: 24px !important;
    border: 1px solid {border} !important;
    background: transparent !important;
    color: {dim} !important;
    padding: 0.45rem 1.4rem !important;
    min-height: 0 !important; height: auto !important;
    line-height: 1.6 !important;
    transition: all 0.22s ease !important;
}}
div.stButton > button:hover {{
    border-color: rgba(200,169,110,0.5) !important;
    color: {gold} !important;
    background: rgba(200,169,110,0.05) !important;
}}
/* ── Scholar Chat — Premium ──────────────────────────────────────────────── */
/* column-reverse: newest message is first in HTML → always at visual bottom.
   scrollTop=0 (default) reveals the bottom. No JS scroll needed. */
.sc-msgs {{
    display: flex;
    flex-direction: column-reverse;
    height: 65vh;
    min-height: 280px;
    overflow-y: auto;
    padding: 1.5rem 0.5rem 1rem;
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
}}
.sc-msgs::-webkit-scrollbar {{ width: 3px; }}
.sc-msgs::-webkit-scrollbar-track {{ background: transparent; }}
.sc-msgs::-webkit-scrollbar-thumb {{ background: {dim}; border-radius: 2px; opacity: 0.5; }}
/* Empty / welcome state */
.sc-empty {{
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 65vh; min-height: 280px; gap: 0.4rem; opacity: 0.45; pointer-events: none;
}}
.sc-empty-icon {{ font-size: 2rem; margin-bottom: 0.35rem; }}
.sc-empty-title {{
    font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: 400;
    letter-spacing: 0.12em; color: {text}; margin: 0;
}}
.sc-empty-sub {{
    font-family: 'Inconsolata', monospace; font-size: 0.56rem;
    letter-spacing: 0.22em; text-transform: uppercase; color: {dim}; margin: 0;
}}
/* Message row wrappers */
.sc-user-row {{
    display: flex; justify-content: flex-end; margin: 0.65rem 0; padding: 0 0.25rem;
    animation: sc-fadein 0.3s ease;
}}
.sc-asst-row {{
    display: flex; justify-content: flex-start; margin: 0.65rem 0; padding: 0 0.25rem;
    animation: sc-fadein 0.3s ease;
}}
/* Bubble + timestamp stacks */
.sc-user-stack {{ display: flex; flex-direction: column; align-items: flex-end; max-width: 72%; }}
.sc-asst-stack {{ display: flex; flex-direction: column; align-items: flex-start; max-width: 86%; }}
/* User bubble */
.sc-user-bbl {{
    background: {sc_user_bg};
    border-radius: 18px 18px 2px 18px;
    padding: 0.72rem 1rem;
    color: {text}; font-size: 0.9rem; line-height: 1.65;
    box-shadow: {sc_user_shadow};
}}
/* Assistant bubble */
.sc-asst-bbl {{
    background: {sc_asst_bg};
    border-left: 2px solid rgba(200,169,110,0.48);
    border-radius: 2px 18px 18px 18px;
    padding: 0.82rem 1.1rem 0.72rem;
    color: {text}; font-size: 0.9rem; line-height: 1.75;
}}
.sc-asst-lbl {{
    display: block; font-family: 'Inconsolata', monospace; font-size: 0.52rem;
    letter-spacing: 0.26em; text-transform: uppercase;
    color: {gold}; opacity: 0.65; margin-bottom: 0.5rem;
}}
/* Timestamps */
.sc-ts {{
    font-family: 'Inconsolata', monospace; font-size: 0.54rem;
    color: {dim}; letter-spacing: 0.04em; margin-top: 0.28rem;
    opacity: 0.6; padding: 0 0.15rem;
}}
/* Thinking animation */
.sc-thinking-wrap {{ display: flex; align-items: center; gap: 5px; padding: 0.25rem 0; }}
.sc-dot {{
    width: 5px; height: 5px; border-radius: 50%; background: {gold}; opacity: 0.35;
    animation: sc-dot-pulse 1.4s ease-in-out infinite;
}}
.sc-dot:nth-child(2) {{ animation-delay: 0.22s; }}
.sc-dot:nth-child(3) {{ animation-delay: 0.44s; }}
@keyframes sc-dot-pulse {{
    0%, 60%, 100% {{ opacity: 0.25; transform: scale(0.8); }}
    30%            {{ opacity: 1;    transform: scale(1.05); }}
}}
/* Streaming cursor */
.sc-cursor {{
    display: inline-block; color: {gold}; font-size: 0.85em;
    vertical-align: middle; margin-left: 2px;
    animation: sc-blink 0.85s step-end infinite;
}}
@keyframes sc-blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
/* Message fade-in */
@keyframes sc-fadein {{
    from {{ opacity: 0; transform: translateY(5px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
/* Starter chip label */
.sc-chips-lbl {{
    font-family: 'Inconsolata', monospace; font-size: 0.56rem;
    letter-spacing: 0.22em; text-transform: uppercase;
    color: {dim}; text-align: center; margin: 0.5rem 0 0.2rem; opacity: 0.6;
}}
/* Starter chip buttons — pill style via :has() marker */
div:has(> .sc-chips-marker) ~ [data-testid="stHorizontalBlock"] div.stButton > button {{
    background: transparent !important;
    border: 1px solid rgba(200,169,110,0.30) !important;
    border-radius: 50px !important;
    color: {gold} !important;
    font-family: 'Inconsolata', monospace !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.4rem 0.85rem !important;
    width: 100% !important;
    min-height: 0 !important;
    line-height: 1.5 !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
    opacity: 0.82;
}}
div:has(> .sc-chips-marker) ~ [data-testid="stHorizontalBlock"] div.stButton > button:hover {{
    background: rgba(200,169,110,0.09) !important;
    border-color: {gold} !important;
    opacity: 1 !important;
}}
/* Chat input — premium override */
[data-testid="stChatInput"] {{
    border-top: 1px solid {border} !important;
    padding: 0.75rem 1rem 0.85rem !important;
    background: {bg} !important;
}}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div {{
    background-color: {sc_input_bg} !important;
    border: 1px solid {border} !important;
    border-radius: 26px !important;
    padding: 0.12rem 0.25rem 0.12rem 1.1rem !important;
    box-shadow: none !important;
}}
[data-testid="stChatInput"] > div > div {{
    border: none !important;
    padding: 0 !important;
}}
[data-testid="stChatInput"] textarea {{
    color: {text} !important;
    font-size: 0.88rem !important;
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    padding: 0.55rem 0 !important;
    line-height: 1.5 !important;
    resize: none !important;
    caret-color: {gold} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {dim} !important;
    opacity: 0.55 !important;
}}
[data-testid="stChatInput"] button {{
    background: {gold} !important;
    border-radius: 50% !important;
    border: none !important;
    width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    min-height: 0 !important;
    flex-shrink: 0;
    margin: 3px !important;
    opacity: 1 !important;
    transition: background 0.2s ease !important;
}}
[data-testid="stChatInput"] button:hover {{ background: #d4b87a !important; }}
[data-testid="stChatInput"] button svg {{ fill: #111 !important; stroke: #111 !important; }}
/* Stop button — scoped via marker, centered pill */
div:has(> .sc-stop-marker) ~ [data-testid="stHorizontalBlock"] div.stButton > button {{
    background: {card_bg} !important;
    border: 1px solid {border} !important;
    color: {text} !important;
    border-radius: 20px !important;
    padding: 0.45rem 1.6rem !important;
    font-family: 'Inconsolata', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    min-height: 0 !important;
    transition: all 0.2s ease !important;
    opacity: 0.85;
}}
div:has(> .sc-stop-marker) ~ [data-testid="stHorizontalBlock"] div.stButton > button:hover {{
    background: rgba(200,169,110,0.07) !important;
    border-color: {gold} !important;
    opacity: 1 !important;
}}
</style>
""", unsafe_allow_html=True)

ARABIC_NAMES = {
    "Fajr": "\u0627\u0644\u0641\u062c\u0631", "Sunrise": "\u0627\u0644\u0634\u0648\u0642",
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

RECITERS = {
    "Mishary Rashid Alafasy": "ar.alafasy",
    "Abdul Basit 'Abd us-Samad": "ar.abdulbasitmurattal",
    "Mahmoud Khalil Al-Husary": "ar.husary",
    "Saud Al-Shuraim": "ar.saudashuraym",
    "Abdurrahmaan As-Sudais": "ar.abdurrahmaansudais"
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

def get_hadith():
    url = "https://random-hadith-generator.vercel.app/bukhari/"
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    data = r.json().get("data", {})
    text = (data.get("hadith_english") or "").strip()
    ref  = (data.get("refno") or "").strip()
    if not text:
        raise ValueError("empty hadith")
    return text, ref

@st.cache_data(ttl=300)
def search_cities(query: str):
    """Return up to 8 city matches from Open-Meteo geocoding (free, no key)."""
    q = query.strip()
    if len(q) < 2:
        return []
    url = (f"https://geocoding-api.open-meteo.com/v1/search"
           f"?name={q}&count=8&language=en&format=json")
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json().get("results", [])

def get_weather(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}&current_weather=true")
    r = requests.get(url, timeout=6)
    r.raise_for_status()
    cw = r.json()["current_weather"]
    return int(cw["weathercode"]), int(cw["is_day"])

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

def get_surah(number, audio_edition="ar.alafasy"):
    url = f"https://api.alquran.cloud/v1/surah/{number}/editions/quran-uthmani,en.transliteration,en.sahih,{audio_edition}"
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

def get_sun_arc_svg(timings, timezone_str, is_ramadan=False):
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    def to_min(t_str, default="00:00"):
        t_str = (t_str or default).split()[0]
        h, m = map(int, t_str.split(":"))
        return h * 60 + m

    fajr_min = to_min(timings.get("Fajr"), default="05:00")
    maghrib_min = to_min(timings.get("Maghrib"), default="18:00")
    now_min = now.hour * 60 + now.minute

    denom = maghrib_min - fajr_min
    if denom <= 0:
        denom = 1

    # Day progress (Fajr -> Maghrib)
    progress = (now_min - fajr_min) / denom
    progress = max(0.0, min(1.0, progress))

    is_day = fajr_min <= now_min <= maghrib_min

    # If after Maghrib, pin to Maghrib
    if now_min > maghrib_min:
        progress = 1.0

    # Arc geometry
    cx, cy, r = 160, 140, 130
    angle = 180 - (progress * 180)
    rad = math.radians(angle)
    orb_x = cx + r * math.cos(rad)
    orb_y = cy - r * math.sin(rad)

    # If night, moon sits at Maghrib endpoint
    if not is_day:
        angle_n = 0  # right end
        rad_n = math.radians(angle_n)
        orb_x = cx + r * math.cos(rad_n)
        orb_y = cy - r * math.sin(rad_n)

    # Styling
    track = "rgba(255, 200, 140, 0.20)"
    label = "rgba(255, 255, 255, 0.55)"
    glow = "rgba(255, 180, 90, 0.45)"

    svg = f"""
<div style="text-align:center; margin: 1.2rem 0 0.8rem 0; display:flex; justify-content:center;">
<svg width="100%" height="180" viewBox="0 0 320 180" style="max-width:420px; overflow:visible;">
  <defs>
    <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#d98a4f"/>
      <stop offset="55%" stop-color="#ffb36b"/>
      <stop offset="100%" stop-color="#d98a4f"/>
    </linearGradient>

    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="orbGlow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Track -->
  <path d="M 30 140 A 130 130 0 0 1 290 140"
        fill="none"
        stroke="{track}"
        stroke-width="2"
        stroke-linecap="round"/>

  <!-- Sexy arc -->
  <path d="M 30 140 A 130 130 0 0 1 290 140"
        fill="none"
        stroke="url(#arcGradient)"
        stroke-width="2.6"
        stroke-linecap="round"
        filter="url(#softGlow)"
        opacity="0.55"/>

  <!-- Orb -->
  {""
    if is_day else
    f'''
    <g filter="url(#orbGlow)">
      <circle cx="{orb_x:.2f}" cy="{orb_y:.2f}" r="9" fill="rgba(255,255,255,0.90)"/>
      <circle cx="{orb_x+3:.2f}" cy="{orb_y-1:.2f}" r="9" fill="rgba(0,0,0,0.55)"/>
    </g>
    '''
  }

  {""
    if not is_day else
    f'''
    <g filter="url(#orbGlow)">
      <circle cx="{orb_x:.2f}" cy="{orb_y:.2f}" r="10" fill="{glow}" opacity="0.35"/>
      <circle cx="{orb_x:.2f}" cy="{orb_y:.2f}" r="5.2" fill="#ffb36b"/>
    </g>
    '''
  }

  <text x="30" y="166" fill="{label}" font-size="12" font-family="Inconsolata, monospace">Fajr</text>
  <text x="290" y="166" fill="{label}" font-size="12" font-family="Inconsolata, monospace" text-anchor="end">Maghrib</text>
</svg>
</div>
"""
    return svg

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
# Inject weather particle overlay
st.markdown(_overlay_html, unsafe_allow_html=True)

try:
    _tz_display = pytz.timezone(_cached_tz)
    now_local = datetime.now(_tz_display)
except Exception:
    now_local = datetime.now()
    
col_title, col_clock, col_theme = st.columns([5, 3, 1])
with col_title:
    st.markdown('<p class="main-title">Salah</p>', unsafe_allow_html=True)
    st.markdown('<p class="arabic-sub">\u0623\u0648\u0642\u0627\u062a \u0627\u0644\u0635\u0644\u0627\u0629</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="date-line">{now_local.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)
with col_clock:
    _clock_city = st.session_state.get("cached_city", "")
    _tz_abbrev  = now_local.strftime("%Z")
    _loc_label  = f"{_clock_city.upper()} · {_tz_abbrev}" if _clock_city else _tz_abbrev
    st.markdown(
        f'<div class="clock-wrap">'
        f'<span class="clock-time">{now_local.strftime("%H:%M")}</span>'
        f'<span class="clock-loc">{_loc_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
with col_theme:
    st.write("")
    st.write("")
    if st.button("☀️" if is_dark else "🌙", help="Toggle light/dark mode"):
        st.session_state.dark_mode = not is_dark
        st.rerun()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Hadith of the Day ─────────────────────────────────────────────────────────
if "hadith_text" not in st.session_state:
    try:
        _ht, _hr = get_hadith()
        st.session_state["hadith_text"] = _ht
        st.session_state["hadith_ref"]  = _hr
    except Exception:
        st.session_state["hadith_text"] = (
            "The best of people are those who are most beneficial to people."
        )
        st.session_state["hadith_ref"] = "Sahih Bukhari"

_hadith_text = st.session_state["hadith_text"]
_hadith_ref  = st.session_state.get("hadith_ref", "Sahih Bukhari")

# Card — label inside, quote mark, text, reference
st.markdown(
    f'<div class="hadith-card">'
    f'<span class="hadith-label">Hadith of the Day</span>'
    f'<span class="hadith-quote-mark">\u201c</span>'
    f'<p class="hadith-text">{_hadith_text}</p>'
    f'<span class="hadith-ref">Sahih Bukhari &middot; {_hadith_ref}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🕌 Prayer", "📿 Tracker", "🤲 Duas", "📖 Quran", "☪️ Scholar"])

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
        except Exception:
            st.warning("Could not detect location. Please enter manually.")
            use_gps = False

    if not use_gps:
        _city_query = st.text_input(
            "Search city",
            placeholder="Type a city name…",
            label_visibility="collapsed",
            key="city_search_input",
        )
        if _city_query and len(_city_query.strip()) >= 2:
            try:
                _geo_results = search_cities(_city_query.strip())
            except Exception:
                _geo_results = []
            if _geo_results:
                _geo_labels = []
                for _gr in _geo_results:
                    _lbl = _gr["name"]
                    if _gr.get("admin1"):
                        _lbl += f", {_gr['admin1']}"
                    _lbl += f" — {_gr.get('country', '')}"
                    _geo_labels.append(_lbl)
                _geo_sel = st.selectbox(
                    "",
                    options=range(len(_geo_labels)),
                    format_func=lambda i: _geo_labels[i],
                    label_visibility="collapsed",
                    key="city_select_box",
                )
                _chosen = _geo_results[_geo_sel]
                lat          = float(_chosen["latitude"])
                lon          = float(_chosen["longitude"])
                timezone_str = _chosen.get("timezone") or "UTC"
                city         = _chosen["name"]
                country      = _chosen.get("country", "")
                st.markdown(
                    f'<p class="location-info">\u25cf  {city}, {country}</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No cities found — try a different spelling.")

    # Cache city for the header clock location label
    st.session_state["cached_city"] = city

    try:
        with st.spinner(""):
            data = get_data_by_coords(lat, lon)

            timings = data["data"]["timings"]
            hijri = data["data"]["date"]["hijri"]
            meta = data["data"]["meta"]

        # Timezone sync → triggers rerun so gradient updates immediately
        new_tz = meta.get("timezone") or timezone_str or "UTC"
        new_tz = str(new_tz).strip()

        old_tz = st.session_state.get("cached_timezone")
        if old_tz != new_tz:
            st.session_state["cached_timezone"] = new_tz
            st.rerun()

        timezone_str = new_tz

        # Weather refresh: re-fetch immediately on location change, else every 30 min
        _new_lat = float(lat)
        _new_lon = float(lon)
        _old_lat = st.session_state.get("cached_lat")
        _old_lon = st.session_state.get("cached_lon")
        st.session_state["cached_lat"] = _new_lat
        st.session_state["cached_lon"] = _new_lon

        _loc_changed = (
            _old_lat is None or _old_lon is None
            or abs(_new_lat - _old_lat) > 0.5
            or abs(_new_lon - _old_lon) > 0.5
        )
        _w_now = time.time()
        _throttle_ok = _w_now - st.session_state.get("_weather_fetched_at", 0) > 1800

        if _loc_changed or _throttle_ok:
            try:
                _wc_new, _wid_new = get_weather(_new_lat, _new_lon)
                _old_w = st.session_state.get("cached_weather", {})
                st.session_state["_weather_fetched_at"] = _w_now
                if (_old_w.get("weathercode") != _wc_new
                        or _old_w.get("is_day") != _wid_new):
                    st.session_state["cached_weather"] = {
                        "weathercode": _wc_new,
                        "is_day": _wid_new,
                    }
                    st.rerun()
            except Exception:
                pass

        def to_min(hhmm: str) -> int:
            # handles "5:44 PM" or "17:44" depending on your timings format
            hhmm = hhmm.strip()
            try:
                # 12-hr
                dt = datetime.strptime(hhmm, "%I:%M %p")
                return dt.hour * 60 + dt.minute
            except:
                # 24-hr
                dt = datetime.strptime(hhmm, "%H:%M")
                return dt.hour * 60 + dt.minute

        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        now_min = now.hour * 60 + now.minute

        fajr_min    = to_min(timings["Fajr"])
        sunrise_min = to_min(timings.get("Sunrise", timings["Fajr"]))  # fallback
        asr_min     = to_min(timings["Asr"])
        maghrib_min = to_min(timings["Maghrib"])
        isha_min    = to_min(timings["Isha"])   

        # Night is "after Maghrib until Fajr" (crosses midnight)
        after_maghrib = now_min >= maghrib_min
        before_fajr   = now_min < fajr_min

        if fajr_min <= now_min < sunrise_min:
            phase = "dawn"
        elif sunrise_min <= now_min < asr_min:
            phase = "day"
        elif asr_min <= now_min < maghrib_min:
            phase = "sunset"
        elif after_maghrib or before_fajr:
            phase = "night"
        else:
            phase = "night"            

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

        # ── Sun Arc Visualization ─────────────────────────────────────
        import streamlit.components.v1 as components

        sun_arc = get_sun_arc_svg(timings, timezone_str, is_ramadan)
        components.html(sun_arc, height=190)

        st.markdown('<p class="section-label">Prayer Times</p>', unsafe_allow_html=True)
        next_prayer = find_next_prayer(timings, timezone_str)

        # ── Countdown timer ───────────────────────────────────────────
        # ── Countdown timer ───────────────────────────────────────────
        try:
            _ctz   = pytz.timezone(timezone_str)
            _now_c = datetime.now(_ctz)
        except Exception:
            _now_c = datetime.now()

        _nts = timings.get(next_prayer, "00:00")
        _nh, _nm = int(_nts.split(":")[0]), int(_nts.split(":")[1])

        _ntgt = _now_c.replace(hour=_nh, minute=_nm, second=0, microsecond=0)
        if _ntgt <= _now_c:
            _ntgt += timedelta(days=1)

        _tms   = int(_ntgt.timestamp() * 1000)
        _sdiff = int((_ntgt - _now_c).total_seconds())
        _sh, _sr = divmod(_sdiff, 3600)
        _sm, _ss = divmod(_sr, 60)
        _static = f"{_sh:02d}:{_sm:02d}:{_ss:02d}"

        import streamlit.components.v1 as components
        _card_bg  = "#131210" if is_dark else "#fdf6ec"
        _border_c = "#1e1e1e" if is_dark else "#e0d8d0"
        _dim_c    = "#4a4540" if is_dark else "#aaa099"

        components.html(
            f"""<!DOCTYPE html>
<html>
<head>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background:{_card_bg};
  border:1px solid {_border_c};
  border-radius:8px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  height:100px;
  font-family:'Inconsolata', monospace;
}}
.lbl {{
  font-size:0.62rem;
  color:{_dim_c};
  letter-spacing:0.2em;
  text-transform:uppercase;
  margin-bottom:2px;
}}
.name {{
  font-size:1rem;
  color:#c8b89a;
  font-weight:400;
  letter-spacing:0.1em;
  text-transform:uppercase;
  margin-bottom:4px;
}}
.cd {{
  font-size:2.4rem;
  color:#c8a96e;
  font-weight:300;
  line-height:1;
  letter-spacing:0.06em;
}}
</style>
</head>
<body>
  <div class="lbl">next prayer in</div>
  <div class="name">{next_prayer}</div>
  <div class="cd" id="cd">{_static}</div>

<script>
var t = new Date({_tms});
function tick() {{
  var d = t - Date.now();
  if (d < 0) d = 0;
  var h = Math.floor(d / 3600000);
  var m = Math.floor((d % 3600000) / 60000);
  var s = Math.floor((d % 60000) / 1000);
  document.getElementById('cd').textContent =
    String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}}
tick();
setInterval(tick, 1000);
</script>
</body>
</html>""",
            height=108,
        )

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

    surah_options = [f"{n}. {name} \u2014 {meaning}" for n, name, meaning in SURAHS]

    col_search, col_reciter = st.columns([2, 1])
    with col_search:
        selected = st.selectbox(
            "Search surah...",
            options=surah_options,
            index=0,
            label_visibility="collapsed"
        )
    with col_reciter:
        reciter_name = st.selectbox(
            "Reciter",
            options=list(RECITERS.keys()),
            index=0,
            label_visibility="collapsed"
        )

    surah_number = int(selected.split(".")[0]) if selected else 1
    audio_edition_id = RECITERS[reciter_name]

    PLAY_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>'
    STOP_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12"></rect></svg>'

    try:
        with st.spinner("Loading surah..."):
            editions = get_surah(surah_number, audio_edition_id)
            arabic_edition = editions[0]
            translit_edition = editions[1]
            english_edition = editions[2]
            audio_edition = editions[3]

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

        # Show standard Bismillah header for all surahs except At-Tawbah (9)
        if surah_number != 9:
            st.markdown(
                '<div class="bismillah">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>',
                unsafe_allow_html=True
            )

        # --- Render ayahs wrapped in a surah-scoped root container ---
        import html as pyhtml

        root_id = f"surah-root-{surah_number}"

        html_blocks = f'<div id="{root_id}" class="surah-root" data-surah="{surah_number}">'

        ayahs = list(zip(
            arabic_edition["ayahs"],
            translit_edition["ayahs"],
            english_edition["ayahs"],
            audio_edition["ayahs"],
        ))

        for ar, tr, en, au in ayahs:
            num = ar["numberInSurah"]
            audio_url = au["audio"]
            audio_attr = pyhtml.escape(audio_url, quote=True)

            html_blocks += f"""
<div class="ayah-block" id="ayah-{surah_number}-{num}">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
    <div class="ayah-number">Ayah {num}</div>
    <button class="play-btn"
            id="play-btn-{surah_number}-{num}"
            data-audio="{audio_attr}"
            data-num="{num}"
            data-surah="{surah_number}">
      {PLAY_SVG}
    </button>
  </div>
  <div class="ayah-arabic">{ar["text"]}</div>
  <div class="ayah-translit">{tr["text"]}</div>
  <div class="ayah-english">{en["text"]}</div>
</div>
"""
        html_blocks += "</div>"

        st.markdown(html_blocks, unsafe_allow_html=True)

        # --- JS: event delegation + scoped root + cleanup (NO key=) ---
        import streamlit.components.v1 as components
        nonce = str(uuid.uuid4())

        js = f"""
<script>
(function() {{
  const parentDoc = window.parent.document;
  const SURAH_ID = {surah_number};
  const ROOT_ID = "surah-root-{surah_number}";
  const playIcon = `{PLAY_SVG}`;
  const stopIcon = `{STOP_SVG}`;
  const NONCE = "{nonce}";

  // Stop any previous audio
  try {{
    if (parentDoc.__quranAudio) {{
      parentDoc.__quranAudio.pause();
      parentDoc.__quranAudio.currentTime = 0;
    }}
  }} catch(e) {{}}

  // New audio instance for this run
  const audio = new Audio();
  parentDoc.__quranAudio = audio;

  // Global state
  parentDoc.__quranState = parentDoc.__quranState || {{}};
  parentDoc.__quranState.currentSurah = SURAH_ID;
  parentDoc.__quranState.currentAyah = null;

  // Remove old click handler if present
  if (parentDoc.__quranClickHandler) {{
    parentDoc.removeEventListener("click", parentDoc.__quranClickHandler, true);
    parentDoc.__quranClickHandler = null;
  }}

  function getRoot() {{
    return parentDoc.getElementById(ROOT_ID);
  }}

  function clearUI(root) {{
    root.querySelectorAll(".ayah-block").forEach(b => b.classList.remove("playing-ayah"));
    root.querySelectorAll(".play-btn").forEach(b => b.innerHTML = playIcon);
  }}

  function play(btn, root) {{
    const url = btn.dataset.audio;
    const num = parseInt(btn.dataset.num, 10);

    if (parentDoc.__quranState.currentAyah === num && !audio.paused) {{
      audio.pause();
      audio.currentTime = 0;
      clearUI(root);
      parentDoc.__quranState.currentAyah = null;
      return;
    }}

    clearUI(root);

    const block = parentDoc.getElementById(`ayah-${{SURAH_ID}}-${{num}}`);
    if (block) {{
      block.classList.add("playing-ayah");
      block.scrollIntoView({{ behavior: "smooth", block: "center" }});
    }}

    audio.src = url; // always pulled from clicked button's current dataset
    audio.play();
    parentDoc.__quranState.currentAyah = num;
    btn.innerHTML = stopIcon;
  }}

  // Event delegation (capture) — robust across Streamlit rerenders
  parentDoc.__quranClickHandler = function(e) {{
    const root = getRoot();
    if (!root) return;
    if (!root.contains(e.target)) return;

    const btn = e.target.closest(".play-btn");
    if (!btn) return;

    // Ensure the button matches current surah
    if (parseInt(btn.dataset.surah, 10) !== SURAH_ID) return;

    e.preventDefault();
    e.stopPropagation();
    play(btn, root);
  }};
  parentDoc.addEventListener("click", parentDoc.__quranClickHandler, true);

  audio.onended = () => {{
    const root = getRoot();
    if (!root) return;

    const currentAyah = parentDoc.__quranState.currentAyah;
    if (!currentAyah) return;

    const currentBtn = parentDoc.getElementById(`play-btn-${{SURAH_ID}}-${{currentAyah}}`);
    if (currentBtn) currentBtn.innerHTML = playIcon;

    const nextNum = currentAyah + 1;
    const nextBtn = parentDoc.getElementById(`play-btn-${{SURAH_ID}}-${{nextNum}}`);
    if (nextBtn) {{
      nextBtn.click();
    }} else {{
      clearUI(root);
      parentDoc.__quranState.currentAyah = null;
    }}
  }};
}})();
</script>
"""

        components.html(js, height=0, width=0)

    except Exception as e:
        st.error(f"Could not load surah: {e}")

# ════════════════════════════════════════════════════════════
# TAB 5 — ISLAMIC SCHOLAR AI  (premium chat redesign)
# ════════════════════════════════════════════════════════════
with tab5:
    import html    as _sc_html_mod
    import re     as _sc_re_mod
    import streamlit.components.v1 as _sc_comp

    _SCHOLAR_SYSTEM = (
        "You are a knowledgeable and compassionate Islamic scholar assistant. "
        "You have deep knowledge of the Quran, Sahih Bukhari, Sahih Muslim, and other major "
        "hadith collections, as well as Islamic jurisprudence and history. "
        "When answering questions: always cite specific Quranic verses (Surah:Ayah) or hadith "
        "references when relevant, be sensitive and compassionate when users share emotional "
        "struggles and respond with relevant Islamic guidance and duas, provide deep tafsir-style "
        "explanations when asked about specific verses, always clarify when something is a matter "
        "of scholarly difference of opinion, and keep responses warm, accessible and grounded in "
        "authentic sources. Never fabricate citations."
    )

    _SC_STARTERS = [
        "Explain Ayatul Kursi",
        "I'm feeling anxious",
        "What breaks a fast?",
        "Best dua for stress",
    ]

    # ── HTML helpers ──────────────────────────────────────────────────────────

    def _sc_md(text):
        """Convert basic markdown to safe HTML paragraphs."""
        s = _sc_html_mod.escape(text)
        s = _sc_re_mod.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s, flags=_sc_re_mod.DOTALL)
        s = _sc_re_mod.sub(r'\*(.+?)\*',     r'<em>\1</em>',         s)
        s = _sc_re_mod.sub(
            r'`([^`]+)`',
            r'<code style="font-family:Inconsolata,monospace;font-size:0.83em;'
            r'background:rgba(200,169,110,0.12);padding:0.1em 0.35em;border-radius:3px;">\1</code>',
            s,
        )
        paras = s.split('\n\n')
        return (
            ''.join(
                f'<p style="margin:0 0 0.5rem 0;">{p.replace(chr(10), "<br>")}</p>'
                for p in paras if p.strip()
            )
            or '<p style="margin:0;"></p>'
        )

    def _sc_user_card(content, ts=""):
        ts_html = f'<span class="sc-ts">{ts}</span>' if ts else ''
        return (
            f'<div class="sc-user-row">'
            f'<div class="sc-user-stack">'
            f'<div class="sc-user-bbl">{_sc_md(content)}</div>'
            f'{ts_html}'
            f'</div></div>'
        )

    def _sc_asst_card(content, ts="", streaming=False, thinking=False):
        if thinking:
            inner = (
                f'<span class="sc-asst-lbl">✦ Scholar is thinking</span>'
                f'<div class="sc-thinking-wrap">'
                f'<div class="sc-dot"></div>'
                f'<div class="sc-dot"></div>'
                f'<div class="sc-dot"></div>'
                f'</div>'
            )
        else:
            cursor = '<span class="sc-cursor">▌</span>' if streaming else ''
            inner  = f'<span class="sc-asst-lbl">✦ Scholar</span>{_sc_md(content)}{cursor}'
        ts_html = f'<span class="sc-ts">{ts}</span>' if ts else ''
        return (
            f'<div class="sc-asst-row">'
            f'<div class="sc-asst-stack">'
            f'<div class="sc-asst-bbl">{inner}</div>'
            f'{ts_html}'
            f'</div></div>'
        )

    def _sc_empty():
        return (
            '<div class="sc-empty">'
            '<div class="sc-empty-icon">☪</div>'
            '<p class="sc-empty-title">Islamic Scholar</p>'
            '<p class="sc-empty-sub">Powered by Claude · Grounded in authentic sources</p>'
            '</div>'
        )

    def _sc_render(msgs, streaming_content=None, is_thinking=False):
        """
        Build the full chat pane HTML.
        Uses CSS column-reverse: messages rendered newest-first in HTML so
        the visual bottom is always newest. scrollTop=0 = bottom. No JS scroll needed.
        """
        if not msgs and streaming_content is None and not is_thinking:
            return _sc_empty()

        parts = []
        # Visual bottom: live/thinking indicator goes first (HTML) = bottom (visual)
        if is_thinking:
            parts.append(_sc_asst_card("", thinking=True))
        elif streaming_content is not None:
            parts.append(_sc_asst_card(streaming_content, streaming=True))

        # Real messages, newest first (column-reverse shows them just above live area)
        for m in reversed(msgs):
            if m["role"] == "user":
                parts.append(_sc_user_card(m["content"], m.get("time", "")))
            else:
                parts.append(_sc_asst_card(m["content"], ts=m.get("time", "")))

        return f'<div class="sc-msgs">{"".join(parts)}</div>'

    def _sc_scroll_bottom():
        """
        Scroll the message pane to top (= visual bottom in column-reverse).
        Called once on send + once on complete to handle preserved scroll state.
        """
        _sc_comp.html(
            """<script>
            setTimeout(function () {
                var el = window.parent.document.querySelector('.sc-msgs');
                if (el) el.scrollTo({ top: 0, behavior: 'smooth' });
            }, 80);
            </script>""",
            height=0, width=0,
        )

    # ── state & initial render ────────────────────────────────────────────────

    if "scholar_messages" not in st.session_state:
        st.session_state["scholar_messages"] = []
    _sc_msgs = st.session_state["scholar_messages"]

    # Single st.empty() for the whole chat area — zero layout reflow on updates
    _sc_area = st.empty()
    _sc_area.markdown(_sc_render(_sc_msgs), unsafe_allow_html=True)

    # ── starter chips (only when conversation is empty) ───────────────────────

    if not _sc_msgs:
        st.markdown('<p class="sc-chips-lbl">Suggested questions</p>', unsafe_allow_html=True)
        st.markdown('<div class="sc-chips-marker"></div>', unsafe_allow_html=True)
        _sca, _scb = st.columns(2)
        _scc, _scd = st.columns(2)
        for _sci, (_sccol, _sctxt) in enumerate(
            zip([_sca, _scb, _scc, _scd], _SC_STARTERS)
        ):
            with _sccol:
                if st.button(_sctxt, key=f"sc_chip_{_sci}"):
                    st.session_state["scholar_pending"] = _sctxt
                    st.rerun()

    # ── input ─────────────────────────────────────────────────────────────────

    _sc_pending = st.session_state.pop("scholar_pending", None)

    # Rate limit: count user turns only
    _sc_user_turns = sum(1 for m in _sc_msgs if m["role"] == "user")
    _SC_MAX_TURNS  = 20
    if _sc_user_turns >= _SC_MAX_TURNS:
        st.markdown(
            f'<p style="font-family:Inconsolata,monospace;font-size:0.65rem;'
            f'color:{dim};letter-spacing:0.18em;text-transform:uppercase;'
            f'text-align:center;margin-top:0.75rem;opacity:0.65;">'
            f'Session limit reached ({_SC_MAX_TURNS} questions). Refresh to start a new session.</p>',
            unsafe_allow_html=True,
        )
    else:
        _sc_typed  = st.chat_input("Ask anything about Islam…", key="scholar_chat_input")
        _sc_prompt = _sc_typed or _sc_pending

        if _sc_prompt:
            _sc_t = datetime.now().strftime("%H:%M")
            _sc_msgs.append({"role": "user", "content": _sc_prompt, "time": _sc_t})

            # Show user message + thinking dots immediately
            _sc_area.markdown(_sc_render(_sc_msgs, is_thinking=True), unsafe_allow_html=True)
            _sc_scroll_bottom()

            _sc_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not _sc_api_key:
                st.error("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
            else:
                try:
                    import anthropic as _anthropic
                    _sc_client   = _anthropic.Anthropic(api_key=_sc_api_key)
                    _sc_api_msgs = [
                        {"role": m["role"], "content": m["content"]} for m in _sc_msgs
                    ]
                    _sc_full = ""
                    with _sc_client.messages.stream(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1500,
                        system=_SCHOLAR_SYSTEM,
                        messages=_sc_api_msgs,
                    ) as _sc_stream:
                        for _sc_chunk in _sc_stream.text_stream:
                            _sc_full += _sc_chunk
                            _sc_area.markdown(
                                _sc_render(_sc_msgs, streaming_content=_sc_full),
                                unsafe_allow_html=True,
                            )

                    # Finalize: save to history, remove streaming cursor
                    _sc_t2 = datetime.now().strftime("%H:%M")
                    _sc_msgs.append({"role": "assistant", "content": _sc_full, "time": _sc_t2})
                    _sc_area.markdown(_sc_render(_sc_msgs), unsafe_allow_html=True)
                    _sc_scroll_bottom()

                except Exception as _sc_err:
                    st.error(f"Could not reach the Scholar: {_sc_err}")