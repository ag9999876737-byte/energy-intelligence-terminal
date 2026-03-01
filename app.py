import streamlit as st
import feedparser
import re
from datetime import datetime, timedelta

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Free Institutional Deal Radar",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
<style>
body { background-color:#0e1117; color:white; }
.title { font-size:34px; font-weight:800; margin-bottom:20px; }
.card { padding:18px; border-radius:10px; background:#161b22; margin:15px 0; }
.money { color:#00c853; font-weight:700; }
.section { margin-top:30px; font-size:22px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ---------------- HIGH-QUALITY FREE SOURCES ----------------

RSS_FEEDS = [
    "https://www.reuters.com/markets/deals/rss",
    "https://asia.nikkei.com/rss/feed/nar",
    "https://reneweconomy.com.au/feed/",
    "https://www.asiapower.com/rss.xml"
]

# ---------------- STRICT FILTERING RULES ----------------

COUNTRIES = [
    "indonesia","vietnam","philippines",
    "thailand","malaysia","singapore",
    "australia"
]

DEAL_KEYWORDS = [
    "financing","investment","acquisition",
    "raised","secured","closed","deal",
    "equity","debt","refinancing"
]

# Regex for money detection
MONEY_PATTERN = r"(\$|usd|a\$|aud|sgd)\s?\d+[.,]?\d*\s?(billion|million|bn|m)?"

# ---------------- FUNCTIONS ----------------

def is_recent(entry):
    try:
        published = datetime(*entry.published_parsed[:6])
        return published > (datetime.now() - timedelta(days=7))
    except:
        return False

def clean_text(text):
    return re.sub('<.*?>', '', text).lower()

def extract_money(text):
    matches = re.findall(MONEY_PATTERN, text, re.IGNORECASE)
    return matches

def contains_country(text):
    return any(c in text for c in COUNTRIES)

def contains_deal_keyword(text):
    return any(k in text for k in DEAL_KEYWORDS)

# ---------------- SCAN ----------------

st.markdown("<div class='title'>💰 Institutional Deal Radar (Last 7 Days)</div>", unsafe_allow_html=True)

events = []

for url in RSS_FEEDS:
    feed = feedparser.parse(url)

    for entry in feed.entries:

        if not is_recent(entry):
            continue

        text = clean_text(entry.title + " " + entry.get("summary",""))

        if not contains_country(text):
            continue

        if not contains_deal_keyword(text):
            continue

        money = re.findall(MONEY_PATTERN, text, re.IGNORECASE)

        if not money:
            continue

        events.append({
            "title": entry.title,
            "link": entry.link,
            "summary": re.sub('<.*?>', '', entry.get("summary","")),
            "published": entry.get("published","N/A")
        })

# ---------------- DISPLAY ----------------

if not events:
    st.warning("No high-quality capital events detected in last 7 days.")
else:

    # Limit to strongest 5 events
    events = events[:5]

    for e in events:

        st.markdown(f"""
        <div class="card">
            <h3>{e['title']}</h3>
            <p><i>{e['published']}</i></p>
            <p>{e['summary'][:500]}...</p>
            <br>
            <a href="{e['link']}" target="_blank" style="color:#4ea1ff;">Read Full Article</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section'>🧠 Positioning Bias</div>", unsafe_allow_html=True)

    if len(events) >= 4:
        st.write("Capital deployment active in region. Monitor sector overweight positioning.")
    elif len(events) >= 2:
        st.write("Moderate deal activity. Selective opportunities emerging.")
    else:
        st.write("Low visible capital flow. Defensive stance advisable.")
