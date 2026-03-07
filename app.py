import streamlit as st
import feedparser
import re
from datetime import datetime, timezone

st.set_page_config(page_title="Institutional Deal Radar", layout="wide")

# -------------------------
# RSS SOURCES
# -------------------------

RSS_FEEDS = [

("Energy",
"https://news.google.com/rss/search?q=energy+investment+asia&hl=en-US&gl=US&ceid=US:en"),

("Infrastructure",
"https://news.google.com/rss/search?q=infrastructure+investment+asia&hl=en-US&gl=US&ceid=US:en"),

("Renewables",
"https://news.google.com/rss/search?q=renewable+energy+investment+asia&hl=en-US&gl=US&ceid=US:en"),

("Australia Energy",
"https://news.google.com/rss/search?q=energy+investment+australia&hl=en-US&gl=US&ceid=US:en")

]

# -------------------------
# COUNTRY KEYWORDS
# -------------------------

COUNTRY_MAP = {

"indonesia":"🇮🇩 Indonesia",
"vietnam":"🇻🇳 Vietnam",
"philippines":"🇵🇭 Philippines",
"thailand":"🇹🇭 Thailand",
"malaysia":"🇲🇾 Malaysia",
"singapore":"🇸🇬 Singapore",
"australia":"🇦🇺 Australia"

}

# -------------------------
# SECTORS
# -------------------------

SECTOR_MAP = {

"solar":"☀️ Solar",
"wind":"🌬️ Wind",
"battery":"🔋 Storage",
"hydrogen":"🧪 Hydrogen",
"lng":"🔥 LNG",
"gas":"🔥 LNG",
"transmission":"⚡ Grid",
"power":"⚡ Power",
"port":"🚢 Ports",
"rail":"🚆 Rail",
"airport":"✈️ Airport",
"infrastructure":"🏗️ Infrastructure"

}

# -------------------------
# DEAL WORDS
# -------------------------

DEAL_WORDS = [
"investment",
"financing",
"funding",
"acquisition",
"deal",
"stake",
"project finance"
]

# -------------------------
# HELPERS
# -------------------------

def clean(text):

    text = re.sub("<.*?>","",text)
    return text.strip()


def is_recent(entry, days=10):

    try:

        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - published

        return diff.days <= days

    except:

        return True


def detect_country(text):

    for k,v in COUNTRY_MAP.items():

        if k in text:
            return v

    return "🌏 Regional"


def detect_sector(text):

    for k,v in SECTOR_MAP.items():

        if k in text:
            return v

    return "🔹 General"


def extract_money(text):

    match = re.search(r'(\$?\d+\.?\d*\s?(billion|million|bn|m))', text)

    if match:
        return match.group(1)

    return ""


# -------------------------
# FETCH NEWS
# -------------------------

def fetch_deals():

    deals = []

    for name,url in RSS_FEEDS:

        feed = feedparser.parse(url)

        for entry in feed.entries:

            title = clean(entry.title)
            summary = clean(entry.summary)

            text = (title + summary).lower()

            if not is_recent(entry):
                continue

            if not any(word in text for word in DEAL_WORDS):
                continue

            deals.append({

                "title":title,
                "summary":summary[:300],
                "link":entry.link,
                "country":detect_country(text),
                "sector":detect_sector(text),
                "money":extract_money(text),
                "source":name

            })

    return deals


# -------------------------
# LOAD DATA
# -------------------------

deals = fetch_deals()

# -------------------------
# HEADER
# -------------------------

st.title("💰 Institutional Deal Radar")

st.caption(
"Infrastructure & Energy Deal Flow — Southeast Asia & Australia"
)

# -------------------------
# METRICS
# -------------------------

col1,col2,col3 = st.columns(3)

col1.metric("Deals Detected", len(deals))

large = len([d for d in deals if "billion" in d["money"].lower()])
col2.metric("Large Deals", large)

countries = len(set([d["country"] for d in deals]))
col3.metric("Markets Active", countries)

st.divider()

# -------------------------
# FILTERS
# -------------------------

country_filter = st.selectbox(
"Filter by Country",
["All"] + sorted(list(set([d["country"] for d in deals])))
)

sector_filter = st.selectbox(
"Filter by Sector",
["All"] + sorted(list(set([d["sector"] for d in deals])))
)

# -------------------------
# APPLY FILTER
# -------------------------

filtered = []

for d in deals:

    if country_filter != "All" and d["country"] != country_filter:
        continue

    if sector_filter != "All" and d["sector"] != sector_filter:
        continue

    filtered.append(d)

# -------------------------
# DEAL CARDS
# -------------------------

for deal in filtered:

    with st.container():

        st.markdown(
        f"""
        ### {deal['title']}

        **{deal['country']} | {deal['sector']}**

        {deal['summary']}

        **Deal Size:** {deal['money'] if deal['money'] else "Undisclosed"}

        🔗 [Read article]({deal['link']})

        ---
        """
        )
