import streamlit as st
import feedparser
from datetime import datetime

# ===================================
# REGION-SPECIFIC PREMIUM SOURCES
# ===================================

RSS_SOURCES = {
    "Southeast Asia": [
        "https://asia.nikkei.com/rss/feed/nar",
        "https://www.asiapower.com/rss.xml",
        "https://news.google.com/rss/search?q=Southeast+Asia+energy+LNG+renewable"
    ],
    "Australia": [
        "https://reneweconomy.com.au/feed/",
        "https://www.energyvoice.com/feed/",
        "https://news.google.com/rss/search?q=Australia+energy+LNG+gas+renewable"
    ],
    "AI in Financial Modelling": [
        "https://news.google.com/rss/search?q=AI+financial+modelling+automation",
        "https://news.google.com/rss/search?q=AI+model+auditing+financial+models",
        # Add specific Substack RSS here if known:
        # Example: "https://yournewsletter.substack.com/feed"
    ]
}

# ===================================
# KEYWORD WEIGHT ENGINE
# ===================================

ENERGY_KEYWORDS = {
    "oil": 3,
    "gas": 3,
    "lng": 4,
    "opec": 5,
    "pipeline": 4,
    "renewable": 3,
    "solar": 3,
    "wind": 3,
    "battery": 3,
    "hydrogen": 4,
    "sanctions": 4,
    "war": 5,
    "conflict": 4
}

AI_MODEL_KEYWORDS = {
    "ai": 4,
    "automation": 3,
    "financial model": 5,
    "model auditing": 5,
    "copilot": 3,
    "excel automation": 4,
    "llm": 4,
    "risk model": 3,
    "audit automation": 4
}

# ===================================
# FUNCTIONS
# ===================================

def fetch_feeds(feed_list):
    articles = []
    seen = set()

    for url in feed_list:
        feed = feedparser.parse(url)

        for entry in feed.entries[:12]:
            title = entry.title

            if title not in seen:
                seen.add(title)
                articles.append({
                    "title": title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")
                })

    return articles


def compute_score(text, region):
    text = text.lower()
    score = 0

    # Energy scoring
    for word, weight in ENERGY_KEYWORDS.items():
        if word in text:
            score += weight

    # AI/Model scoring
    if region == "AI in Financial Modelling":
        for word, weight in AI_MODEL_KEYWORDS.items():
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


def derive_bias(scored_articles, region):
    total = sum(a["score"] for a in scored_articles)

    if region == "AI in Financial Modelling":
        if total > 40:
            return "🚀 AI TRANSFORMATION ACCELERATING"
        elif total > 20:
            return "⚙️ Gradual AI Adoption"
        else:
            return "🧩 Limited AI Activity"

    else:
        if total > 60:
            return "🔴 STRONG ENERGY VOLATILITY"
        elif total > 30:
            return "🟡 MODERATE MOVEMENT"
        else:
            return "⚪ STABLE ENERGY CONDITIONS"


# ===================================
# STREAMLIT UI
# ===================================

st.set_page_config(layout="wide")
st.title("🌏 Southeast Asia & Australia Energy + AI Intelligence Terminal")
st.markdown("Premium Publisher Feeds | Region-Specific | Model Auditing AI Monitor")

region = st.selectbox("Select Focus Area", list(RSS_SOURCES.keys()))

if st.button("Run Intelligence Scan"):

    with st.spinner("Scanning premium intelligence sources..."):

        raw_articles = fetch_feeds(RSS_SOURCES[region])

        if not raw_articles:
            st.warning("No articles retrieved.")
        else:

            scored = []

            for article in raw_articles:
                text = article["title"] + " " + article["summary"]
                score = compute_score(text, region)

                scored.append({
                    "title": article["title"],
                    "link": article["link"],
                    "score": score,
                    "impact": classify(score)
                })

            scored = sorted(scored, key=lambda x: x["score"], reverse=True)

            st.subheader(f"Top Developments – {region}")

            for article in scored:
                if article["score"] > 0:
                    st.markdown(f"""
### {article['impact']} | Score: {article['score']}
**{article['title']}**

[Read Full Article]({article['link']})
---
""")

            bias = derive_bias(scored, region)

            st.subheader("Strategic Bias Indicator")
            st.markdown(f"### {bias}")

    st.success("Scan Complete")
