import streamlit as st
import feedparser
from datetime import datetime, timezone
import re
import pandas as pd

st.set_page_config(page_title="Institutional Deal Radar", layout="wide")

# -----------------------------
# RSS SOURCES
# -----------------------------

RSS_FEEDS = [

("Google Energy",
"https://news.google.com/rss/search?q=energy+investment+asia&hl=en-US&gl=US&ceid=US:en"),

("Google Infrastructure",
"https://news.google.com/rss/search?q=infrastructure+investment+asia&hl=en-US&gl=US&ceid=US:en"),

("Google Renewable",
"https://news.google.com/rss/search?q=renewable+energy+investment+asia&hl=en-US&gl=US&ceid=US:en"),

("Google Australia Energy",
"https://news.google.com/rss/search?q=energy+investment+australia&hl=en-US&gl=US&ceid=US:en")

]

# -----------------------------
# COUNTRY KEYWORDS
# -----------------------------

COUNTRY_MAP = {

"indonesia":"🇮🇩 Indonesia",
"vietnam":"🇻🇳 Vietnam",
"philippines":"🇵🇭 Philippines",
"thailand":"🇹🇭 Thailand",
"malaysia":"🇲🇾 Malaysia",
"singapore":"🇸🇬 Singapore",
"australia":"🇦🇺 Australia"

}

# -----------------------------
# SECTOR KEYWORDS
# -----------------------------

SECTOR_MAP = {

"solar":"☀️ Solar",
"wind":"🌬️ Wind",
"battery":"🔋 Storage",
"hydrogen":"🧪 Hydrogen",
"gas":"🔥 Gas / LNG",
"lng":"🔥 Gas / LNG",
"transmission":"⚡ Grid",
"power":"⚡ Power",
"infrastructure":"🏗️ Infrastructure",
"port":"🚢 Ports",
"rail":"🚆 Rail",
"airport":"✈️ Airport"

}

# -----------------------------
# DEAL KEYWORDS
# -----------------------------

DEAL_WORDS = [
"investment",
"financing",
"funding",
"deal",
"acquisition",
"project finance",
"loan",
"equity",
"stake",
"billion",
"million"
]

# -----------------------------
# HELPERS
# -----------------------------

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

    results = []

    for k,v in COUNTRY_MAP.items():

        if k in text:
            results.append(v)

    return results


def detect_sector(text):

    for k,v in SECTOR_MAP.items():

        if k in text:
            return v

    return "🔹 General"


def deal_score(text):

    score = 0

    for word in DEAL_WORDS:

        if word in text:
            score += 1

    return score


def extract_money(text):

    match = re.search(r'(\$?\d+\.?\d*\s?(billion|million|bn|m))', text)

    if match:

        value = match.group(1)

        if "b" in value.lower():
            size = 3
        elif "m" in value.lower():
            size = 2
        else:
            size = 1

        return value, size

    return None, 0


# -----------------------------
# FETCH FEEDS
# -----------------------------

def fetch_feed(source):

    name, url = source
    deals = []

    try:

        feed = feedparser.parse(url)

        for entry in feed.entries:

            title = clean(entry.get("title",""))
            summary = clean(entry.get("summary",""))

            text = (title + " " + summary).lower()

            if not is_recent(entry):
                continue

            countries = detect_country(text)
            sector = detect_sector(text)

            if not countries and sector == "🔹 General":
                continue

            money, size = extract_money(text)

            deals.append({

                "title": title,
                "summary": summary[:300],
                "link": entry.get("link","#"),
                "source": name,
                "countries": countries if countries else ["🌏 Regional"],
                "sector": sector,
                "money": money if money else "",
                "size": size,
                "score": deal_score(text)

            })

    except Exception as e:

        print("Feed error:", name)

    return deals


# -----------------------------
# LOAD ALL DEALS
# -----------------------------

def load_deals():

    all_deals = []

    for source in RSS_FEEDS:

        deals = fetch_feed(source)
        all_deals.extend(deals)

    all_deals.sort(key=lambda x:(x["score"],x["size"]),reverse=True)

    return all_deals


# -----------------------------
# UI
# -----------------------------

st.title("💰 Institutional Deal Radar")

st.caption("Infrastructure & Energy Deal Flow — Southeast Asia & Australia")

deals = load_deals()

# -----------------------------
# METRICS
# -----------------------------

col1,col2,col3 = st.columns(3)

total_deals = len(deals)

large_deals = len([d for d in deals if d["size"]>=2])

value_estimate = sum([500 if d["size"]==3 else 50 for d in deals])

col1.metric("Deals", total_deals)

col2.metric("Total Value", f"${value_estimate}M")

col3.metric("Large Deals", large_deals)

st.divider()

# -----------------------------
# DEAL TABLE
# -----------------------------

rows = []

for d in deals:

    rows.append({

    "Country": ", ".join(d["countries"]),
    "Sector": d["sector"],
    "Deal Size": d["money"],
    "Headline": d["title"],
    "Source": d["source"],
    "Link": d["link"]

    })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True
)

st.caption(
"Sources: Google News | Auto filtered for energy & infrastructure deals | Updated live"
)
