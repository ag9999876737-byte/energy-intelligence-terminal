import streamlit as st
import requests
from datetime import datetime

# ==============================
# CONFIG
# ==============================

SERPAPI_KEY = "YOUR_SERPAPI_KEY"  # <-- Put your key here

SEARCH_QUERIES = {
    "Geopolitics": "latest geopolitics news war conflict sanctions energy impact",
    "Energy": "oil gas LNG OPEC renewable energy supply disruption",
    "India Macro": "India economy RBI rupee inflation infrastructure policy"
}

# ==============================
# KEYWORD WEIGHTS
# ==============================

RISK_KEYWORDS = {
    "war": 5,
    "conflict": 4,
    "sanctions": 4,
    "crisis": 3,
    "attack": 5,
    "embargo": 4,
    "strike": 3
}

ENERGY_KEYWORDS = {
    "oil": 3,
    "gas": 3,
    "lng": 4,
    "refinery": 3,
    "pipeline": 4,
    "opec": 5,
    "renewable": 2,
    "solar": 2
}

INDIA_KEYWORDS = {
    "india": 5,
    "rupee": 3,
    "rbi": 4,
    "sensex": 3,
    "nifty": 3,
    "inflation": 3,
    "infrastructure": 2
}

# ==============================
# FUNCTIONS
# ==============================

def serp_search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("news_results", [])


def compute_score(text, keyword_dict):
    score = 0
    for word, weight in keyword_dict.items():
        if word in text:
            score += weight
    return score


def evaluate_article(article):
    text = (article["title"] + " " + article.get("snippet", "")).lower()

    geo_score = compute_score(text, RISK_KEYWORDS)
    energy_score = compute_score(text, ENERGY_KEYWORDS)
    india_score = compute_score(text, INDIA_KEYWORDS)

    total_score = geo_score + energy_score + india_score

    return {
        "title": article["title"],
        "link": article["link"],
        "geo_score": geo_score,
        "energy_score": energy_score,
        "india_score": india_score,
        "total_score": total_score
    }


def derive_market_bias(articles):
    total_geo = sum(a["geo_score"] for a in articles)
    total_energy = sum(a["energy_score"] for a in articles)
    total_india = sum(a["india_score"] for a in articles)

    if total_geo > 20:
        return "🔴 RISK-OFF (Global Tension High)"
    elif total_energy > 20:
        return "🟢 ENERGY BULLISH"
    elif total_india > 20:
        return "🟡 INDIA MACRO ACTIVE"
    else:
        return "⚪ NEUTRAL"


# ==============================
# STREAMLIT UI
# ==============================

st.set_page_config(page_title="Energy Intelligence Terminal", layout="wide")

st.title("🌍 Energy & Geopolitical Intelligence Terminal")
st.markdown("Zero-AI | Deterministic Macro Scoring Engine")

run_button = st.button("Run Intelligence Scan")

if run_button:

    with st.spinner("Scanning global macro environment..."):

        collected_articles = []

        for domain, query in SEARCH_QUERIES.items():
            results = serp_search(query)

            for r in results:
                collected_articles.append({
                    "title": r.get("title", ""),
                    "link": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                    "domain": domain
                })

        if not collected_articles:
            st.warning("No recent articles found.")
        else:

            scored_articles = [
                evaluate_article(a) for a in collected_articles
            ]

            top_articles = sorted(
                scored_articles,
                key=lambda x: x["total_score"],
                reverse=True
            )[:10]

            st.subheader("🔥 High Impact News")

            for article in top_articles:
                if article["total_score"] > 0:
                    st.markdown(f"""
### {article['title']}
Score: **{article['total_score']}**
- Geopolitical: {article['geo_score']}
- Energy: {article['energy_score']}
- India: {article['india_score']}
[Read More]({article['link']})
---
""")

            bias = derive_market_bias(top_articles)

            st.subheader("📈 Market Bias Engine")
            st.markdown(f"### {bias}")

            st.subheader("🎯 Trading Interpretation")

            if "RISK-OFF" in bias:
                st.write("• Consider Gold ETF")
                st.write("• Reduce high-beta exposure")
            elif "ENERGY BULLISH" in bias:
                st.write("• Look at ONGC / Oil India")
                st.write("• Monitor crude-sensitive stocks")
            elif "INDIA MACRO" in bias:
                st.write("• Infra / PSU themes")
                st.write("• Nifty momentum watch")
            else:
                st.write("• No strong macro signal today")

    st.success("Scan Complete")
