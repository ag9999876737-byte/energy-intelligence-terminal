import streamlit as st
import feedparser
import re
from datetime import datetime, timedelta
from collections import defaultdict

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Capital & Automation Positioning Radar",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
body { background-color:#0e1117; color:white; }
.title { font-size:34px; font-weight:800; margin-bottom:20px; }
.metric-box { padding:15px; border-radius:10px; background:#161b22; margin-bottom:15px; }
.section { margin-top:30px; font-size:22px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ---------------- CURATED SOURCES ----------------

RSS_FEEDS = [
    "https://www.reuters.com/markets/deals/rss",
    "https://reneweconomy.com.au/feed/",
    "https://www.asiapower.com/rss.xml",
    "https://asia.nikkei.com/rss/feed/nar",
    "https://towardsdatascience.com/feed"
]

# ---------------- KEYWORDS ----------------

COUNTRIES = ["indonesia","vietnam","philippines","thailand","malaysia","australia"]
TECH = ["lng","solar","wind","battery","bess","hydrogen","grid","transmission"]
DEALS = ["deal","financing","investment","acquisition","equity","debt","refinancing"]
AI_TERMS = ["ai","automation","machine learning","copilot","model audit","financial model"]

# ---------------- FUNCTIONS ----------------

def is_recent(entry):
    try:
        published = datetime(*entry.published_parsed[:6])
        return published > (datetime.now() - timedelta(days=7))
    except:
        return False

def clean_text(text):
    return re.sub('<.*?>', '', text).lower()

# ---------------- DATA STRUCTURES ----------------

country_count = defaultdict(int)
tech_count = defaultdict(int)
deal_count = 0
ai_count = 0
total_articles = 0

# ---------------- FETCH & PROCESS ----------------

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:

        if not is_recent(entry):
            continue

        text = clean_text(entry.title + " " + entry.get("summary",""))
        total_articles += 1

        # Country detection
        for c in COUNTRIES:
            if c in text:
                country_count[c] += 1

        # Technology detection
        for t in TECH:
            if t in text:
                tech_count[t] += 1

        # Deal detection
        if any(d in text for d in DEALS):
            deal_count += 1

        # AI detection
        if any(a in text for a in AI_TERMS):
            ai_count += 1

# ---------------- SCORING ----------------

energy_momentum = sum(tech_count.values())
regional_intensity = sum(country_count.values())
ai_pressure = ai_count
deal_flow_intensity = deal_count

# ---------------- DASHBOARD ----------------

st.markdown("<div class='title'>📊 Capital & Automation Positioning Radar (7 Days)</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Energy Momentum Score", energy_momentum)
col2.metric("Regional Activity Signals", regional_intensity)
col3.metric("Project Finance Deal Signals", deal_flow_intensity)
col4.metric("AI Disruption Signals", ai_pressure)

# ---------------- SECTION: REGION HEAT ----------------

st.markdown("<div class='section'>🌏 Regional Heat Map</div>", unsafe_allow_html=True)

if country_count:
    for k, v in sorted(country_count.items(), key=lambda x: x[1], reverse=True):
        st.write(f"{k.title()} : {v} signals")
else:
    st.write("No regional signals detected.")

# ---------------- SECTION: TECHNOLOGY MOMENTUM ----------------

st.markdown("<div class='section'>⚡ Technology Momentum</div>", unsafe_allow_html=True)

if tech_count:
    for k, v in sorted(tech_count.items(), key=lambda x: x[1], reverse=True):
        st.write(f"{k.upper()} : {v} mentions")
else:
    st.write("No technology signals detected.")

# ---------------- SECTION: STRATEGIC INTERPRETATION ----------------

st.markdown("<div class='section'>🧠 Strategic Bias</div>", unsafe_allow_html=True)

if energy_momentum > 15:
    st.write("Energy investment momentum accelerating.")
elif energy_momentum > 7:
    st.write("Moderate energy activity.")
else:
    st.write("Energy activity muted.")

if deal_flow_intensity > 10:
    st.write("Project finance cycle active.")
else:
    st.write("Deal flow stable/low.")

if ai_pressure > 5:
    st.write("AI automation pressure rising in finance.")
else:
    st.write("AI disruption signals limited this week.")
