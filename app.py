import streamlit as st
import requests
from datetime import datetime
import math

st.set_page_config(page_title="Salah", page_icon="🕌", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Inconsolata:wght@300;400&display=swap');
html, body, [class*="css"] { font-family: 'Cormorant Garamond', serif; background-color: #0a0a0a; color: #e8e2d9; }
.stApp { background-color: #0a0a0a; }
.main-title { font-size: 3.2rem; font-weight: 300; letter-spacing: 0.2em; text-transform: uppercase; color: #e8e2d9; margin-bottom: 0; line-height: 1; }
.arabic-sub { font-size: 1.6rem; color: #7a6f63; letter-spacing: 0.05em; margin-top: 0.2rem; font-weight: 300; }
.date-line { font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: #4a4540; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.5rem; }
.divider { border: none; border-top: 1px solid #1e1e1e; margin: 2rem 0; }
.prayer-card { background: #111111; border: 1px solid #1e1e1e; border-radius: 2px; padding: 1.4rem 1.8rem; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center; }
.prayer-card.next { border-color: #c8a96e; background: #131210; }
.prayer-name { font-size: 1.1rem; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; color: #c8b89a; }
.prayer-name-arabic { font-size: 0.85rem; color: #4a4540; margin-top: 0.1rem; }
.prayer-time { font-family: 'Inconsolata', monospace; font-size: 1.3rem; color: #e8e2d9; font-weight: 300; }
.next-badge { font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: #c8a96e; letter-spacing: 0.2em; text-transform: uppercase; margin-left: 0.8rem; }
.qibla-section { background: #111111; border: 1px solid #1e1e1e; border-radius: 2px; padding: 2rem; text-align: center; margin-top: 1rem; }
.qibla-degree { font-family: 'Inconsolata', monospace; font-size: 3rem; color: #c8a96e; font-weight: 300; line-height: 1; }
.qibla-label { font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: #4a4540; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.4rem; }
.section-label { font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: #4a4540; letter-spacing: 0.25em; text-transform: uppercase; margin-bottom: 1rem; margin-top: 2rem; }
.hijri-date { font-size: 1rem; color: #7a6f63; font-weight: 300; letter-spacing: 0.05em; }
.surah-header { background: #111111; border: 1px solid #1e1e1e; border-radius: 2px; padding: 1.8rem; text-align: center; margin-bottom: 1rem; }
.surah-name-ar { font-size: 2.2rem; color: #c8b89a; font-weight: 300; line-height: 1.2; }
.surah-name-en { font-family: 'Inconsolata', monospace; font-size: 0.75rem; color: #4a4540; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 0.4rem; }
.surah-meta { font-family: 'Inconsolata', monospace; font-size: 0.7rem; color: #2e2e2e; margin-top: 0.3rem; letter-spacing: 0.1em; }
.ayah-block { border-bottom: 1px solid #161616; padding: 1.4rem 0; }
.ayah-arabic { font-size: 1.6rem; color: #e8e2d9; text-align: right; line-height: 2.2; font-weight: 300; direction: rtl; }
.ayah-number { font-family: 'Inconsolata', monospace; font-size: 0.65rem; color: #c8a96e; letter-spacing: 0.15em; margin-bottom: 0.4rem; }
.ayah-english { font-size: 0.95rem; color: #7a6f63; line-height: 1.7; font-weight: 300; margin-top: 0.6rem; font-style: italic; }
.bismillah { font-size: 1.8rem; color: #c8a96e; text-align: center; padding: 1.5rem 0; direction: rtl; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 3rem; max-width: 680px; }
</style>
""", unsafe_allow_html=True)

ARABIC_NAMES = {
    "Fajr": "\u0627\u0644\u0641\u062c\u0631", "Sunrise": "\u0627\u0644\u0634\u0631\u0648\u0642", "Dhuhr": "\u0627\u0644\u0638\u0647\u0631",
    "Asr": "\u0627\u0644\u0639\u0635\u0631", "Maghrib": "\u0627\u0644\u0645\u063a\u0631\u0628", "Isha": "\u0627\u0644\u0639\u0634\u0627\u0621",
}
PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]

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

def get_data(city, country):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_qibla(lat, lon):
    url = f"https://api.aladhan.com/v1/qibla/{lat}/{lon}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()["data"]["direction"]

def get_surah(number):
    url = f"https://api.alquran.cloud/v1/surah/{number}/editions/quran-uthmani,en.sahih"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()["data"]

def to_12h(time_str):
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%-I:%M %p")
    except:
        return time_str

def find_next_prayer(timings):
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

now = datetime.now()
st.markdown('<p class="main-title">Salah</p>', unsafe_allow_html=True)
st.markdown('<p class="arabic-sub">\u0623\u0648\u0642\u0627\u062a \u0627\u0644\u0635\u0644\u0627\u0629</p>', unsafe_allow_html=True)
st.markdown(f'<p class="date-line">{now.strftime("%A, %B %d, %Y")}</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    city = st.text_input("City", value="New York", label_visibility="collapsed", placeholder="City")
with col2:
    country = st.text_input("Country", value="US", label_visibility="collapsed", placeholder="Country")

try:
    with st.spinner(""):
        data = get_data(city, country)
        timings = data["data"]["timings"]
        hijri = data["data"]["date"]["hijri"]
        meta = data["data"]["meta"]
        lat, lon = meta["latitude"], meta["longitude"]
        qibla_deg = get_qibla(lat, lon)

    hijri_str = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} AH"
    st.markdown(f'<p class="hijri-date">{hijri_str}</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Prayer Times</p>', unsafe_allow_html=True)

    next_prayer = find_next_prayer(timings)

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
        f'<div class="qibla-section">'
        f'{svg}'
        f'<div class="qibla-degree">{qibla_deg:.1f}\u00b0</div>'
        f'<div class="qibla-label">from North \u00b7 toward Makkah</div>'
        f'</div>',
        unsafe_allow_html=True
    )

except requests.exceptions.ConnectionError:
    st.error("Could not connect. Please check your internet connection.")
except Exception as e:
    st.error(f"Prayer times error: {e}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p class="section-label">Quran</p>', unsafe_allow_html=True)

surah_options = [f"{n}. {name} \u2014 {meaning}" for n, name, meaning in SURAHS]
selected = st.selectbox("Select a Surah", surah_options, index=0, label_visibility="collapsed")
surah_number = int(selected.split(".")[0])

try:
    with st.spinner("Loading surah..."):
        editions = get_surah(surah_number)
        arabic_edition = editions[0]
        english_edition = editions[1]

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

    arabic_ayahs = arabic_edition["ayahs"]
    english_ayahs = english_edition["ayahs"]

    for ar, en in zip(arabic_ayahs, english_ayahs):
        ayah_num = ar["numberInSurah"]
        st.markdown(
            f'<div class="ayah-block">'
            f'<div class="ayah-number">Ayah {ayah_num}</div>'
            f'<div class="ayah-arabic">{ar["text"]}</div>'
            f'<div class="ayah-english">{en["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

except Exception as e:
    st.error(f"Could not load surah: {e}")
