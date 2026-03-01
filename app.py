import streamlit as st
import feedparser
import pandas as pd

# ===============================
# REGION-WISE PREMIUM ENERGY SOURCES
# ===============================

RSS_SOURCES = {
    "India": [
        "https://mercomindia.com/feed/",
        "https://www.pv-tech.org/feed/",
        "https://news.google.com/rss/search?q=India+renewable+energy+LNG+oil"
    ],
    "Asia": [
        "https://asia.nikkei.com/rss/feed/nar",
        "https://news.google.com/rss/search?q=Asia+LNG+oil+energy"
    ],
    "Middle East": [
        "https://oilprice.com/rss/main",
        "https://news.google.com/rss/search?q=Middle+East+OPEC+oil"
    ],
    "Global": [
        "https://www.reuters.com/markets/energy/rss",
        "https://news.google.com/rss/search?q=global+energy+oil+gas+LNG"
    ]
}

ENERGY_KEYWORDS = {
    "oil": 3,
    "crude": 3,
    "gas": 3,
    "lng": 4,
    "opec": 5,
    "pipeline": 4,
    "refinery": 3,
    "sanctions": 4,
    "war": 5,
    "conflict": 4,
    "renewable": 2,
    "solar": 2,
    "wind": 2,
    "hydrogen": 3,
    "battery": 2
}

# ===============================
# FUNCTIONS
# ===============================

def fetch_multiple_feeds(feed_list):
    articles = []
    seen_titles = set()

    for url in feed_list:
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:
            title = entry.title

            if title not in seen_titles:
                seen_titles.add(title)
                articles.append({
                    "title": title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")
                })

    return articles


def compute_score(text):
    score = 0
    text = text.lower()

    for word, weight in ENERGY_KEYWORDS.items():
        if word in text:
            score += weight

    return score


def classify(score):
    if score >= 12:
        return "🔥 HIGH IMPACT"
    elif score >= 6:
        return "⚠️ MEDIUM IMPACT"
    elif score > 0:
        return "ℹ️ LOW IMPACT"
    else:
        return ""


def derive_bias(scored_articles):
    total = sum(a["score"] for a in scored_articles)

    if total > 60:
        return "🔴 HIGH ENERGY VOLATILITY"
    elif total > 30:
        return "🟡 MODERATE ENERGY MOVEMENT"
    else:
        return "⚪ STABLE CONDITIONS"


# ===============================
# STREAMLIT UI
# ===============================

st.set_page_config(layout="wide")
st.title("🌍 Premium Energy Intelligence Terminal")
st.markdown("High-Quality Publisher Feeds | Zero AI | Region-Wise")

region = st.selectbox("Select Region", list(RSS_SOURCES.keys()))

if st.button("Run Energy Scan"):

    with st.spinner("Scanning premium energy sources..."):

        raw_articles = fetch_multiple_feeds(RSS_SOURCES[region])

        if not raw_articles:
            st.warning("No articles retrieved.")
        else:
            scored_articles = []

            for article in raw_articles:
                text = article["title"] + " " + article["summary"]
                score = compute_score(text)

                scored_articles.append({
                    "title": article["title"],
                    "link": article["link"],
                    "score": score,
                    "impact": classify(score)
                })

            scored_articles = sorted(
                scored_articles,
                key=lambda x: x["score"],
                reverse=True
            )

            st.subheader(f"Top Energy Developments – {region}")

            for article in scored_articles:
                if article["score"] > 0:
                    st.markdown(f"""
### {article['impact']} | Score: {article['score']}
**{article['title']}**

[Read Full Article]({article['link']})
---
""")

            bias = derive_bias(scored_articles)

            st.subheader("Regional Energy Bias")
            st.markdown(f"### {bias}")

            if "HIGH" in bias:
                st.write("• Expect price volatility in crude/LNG")
                st.write("• Monitor OPEC & geopolitical triggers")
            elif "MODERATE" in bias:
                st.write("• Watch inventory reports & policy shifts")
            else:
                st.write("• No major structural catalyst detected")

    st.success("Scan Complete")
