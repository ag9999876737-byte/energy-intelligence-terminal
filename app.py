import streamlit as st
import feedparser
import os
from datetime import datetime, timedelta
from openai import OpenAI

# Get API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Energy Intelligence Terminal", layout="wide")

st.title("⚡ Energy & Project Finance Intelligence Terminal")

st.sidebar.header("Filters")

region = st.sidebar.selectbox(
    "Select Region",
    ["Global", "Americas", "EMEA", "Southeast Asia", "Australia/NZ"]
)

days = st.sidebar.slider("Lookback Days", 1, 14, 7)

run_button = st.sidebar.button("Generate Intelligence")

RSS_FEEDS = [
    "https://www.reuters.com/markets/energy/rss",
    "https://www.iea.org/news/rss",
]

def fetch_articles():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, "published_parsed"):
                published = datetime(*entry.published_parsed[:6])
                if published > datetime.now() - timedelta(days=days):
                    articles.append({
                        "title": entry.title,
                        "summary": entry.summary if "summary" in entry else ""
                    })
    return articles

def analyze_article(article):
    prompt = f"""
Summarize the following news article in this format:

Headline — one sentence
What happened — 2-3 sentences
Why it matters — 1-2 sentences practical implication

Article:
Title: {article['title']}
Summary: {article['summary']}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

if run_button:
    with st.spinner("Scanning energy intelligence..."):
        articles = fetch_articles()

        if not articles:
            st.warning("No recent articles found.")
        else:
            for article in articles[:5]:
                summary = analyze_article(article)
                with st.expander(article["title"]):
                    st.write(summary)
