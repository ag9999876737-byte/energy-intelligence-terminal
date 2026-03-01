import streamlit as st
import feedparser
import re
from datetime import datetime, timedelta

# ------------------------
# PAGE CONFIG
# ------------------------

st.set_page_config(
    page_title="Energy & Finance Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body { background-color:#0e1117; color:white; }
.title { font-size:36px; font-weight:800; margin-bottom:10px; }
.card { padding:18px; border-radius:10px; background:#161b22; margin:12px 0; }
.tag-high { color:#ff4b4b;font-weight:700;}
.tag-med { color:#ffa500;font-weight:700;}
.tag-low { color:#00c853;font-weight:700;}
</style>
""", unsafe_allow_html=True)

# ------------------------
# CURATED RSS SOURCES
# ------------------------

RSS_SOURCES = {
    "SE Asia Energy": [
       "https://asia.nikkei.com/rss/feed/nar",
       "https://www.asiapower.com/rss.xml",
       "https://www.pv-tech.org/feed/",
       "https://www.mercomindia.com/feed/"
    ],
    "Australia Energy": [
       "https://reneweconomy.com.au/feed/",
       "https://www.energynewsbulletin.net/rss"
    ],
    "Project Finance Deals": [
       "https://www.reuters.com/markets/deals/rss",
       "https://www.ft.com/rss/world?edition=uk"
    ],
    "AI & Financial Modelling": [
       "https://towardsdatascience.com/feed"
       # Add additional Substack RSS here
    ]
}

DOMAIN_KEYWORDS = {
    "SE Asia Energy": ["renewable","capacity","oil","gas","lng","energy","power","pipeline"],
    "Australia Energy": ["renewable","solar","wind","energy","gas","au","australia","lng"],
    "Project Finance Deals": ["deal","investment","project finance","financing","acquisition","funding","equity","debt"],
    "AI & Financial Modelling": ["ai","automation","model audit","financial model","machine learning","copilot"]
}

# ------------------------
# UTILITY FUNCTIONS
# ------------------------

def filter_recent(entry):
    try:
        published = datetime(*entry.published_parsed[:6])
    except:
        return False
    return published > (datetime.now() - timedelta(hours=72))

def domain_relevant(title, summary, keywords):
    text = (title + " " + summary).lower()
    return any(k.lower() in text for k in keywords)

def extractive_summary(text, max_sentences=2):
    clean = re.sub('<.*?>','',text)
    parts = re.split(r'(?<=[.!?]) +', clean)
    return " ".join(parts[:max_sentences])

def classify_score(text):
    text = text.lower()
    if any(x in text for x in ["crisis","surge","shock","ban","collapse","deal"]):
        return "HIGH"
    elif any(x in text for x in ["growth","policy","agreement","investment","framework"]):
        return "MEDIUM"
    else:
        return "LOW"

# ------------------------
# UI - Sidebar
# ------------------------

st.sidebar.title("Select Focus Area")
category = st.sidebar.selectbox("Choose category", list(RSS_SOURCES.keys()))
run_button = st.sidebar.button("Scan Latest")

st.markdown(f"<div class='title'>⚡ {category} Updates (Last 72h)</div>", unsafe_allow_html=True)

# ------------------------
# MAIN SCAN
# ------------------------

if run_button:

    articles = []
    for url in RSS_SOURCES[category]:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if filter_recent(entry) and domain_relevant(entry.title, entry.get("summary",""), DOMAIN_KEYWORDS[category]):
                articles.append(entry)

    if not articles:
        st.warning("No high-quality recent articles found in this category.")
    else:

        for entry in articles:

            title = entry.title
            link = entry.link
            summary_raw = entry.get("summary","")
            summary = extractive_summary(summary_raw,2)
            impact = classify_score(summary_raw)

            tag_class = "tag-high" if impact=="HIGH" else "tag-med" if impact=="MEDIUM" else "tag-low"

            published = entry.get("published","N/A")

            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p><i>{published}</i></p>
                <p>{summary}</p>
                <span class="{tag_class}">{impact} IMPACT</span><br><br>
                <a href="{link}" target="_blank" style="color:#4ea1ff;">Read Full Article</a>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("Choose a category and click ‘Scan Latest’")
