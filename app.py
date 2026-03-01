import streamlit as st
import feedparser
import nltk
from nltk.tokenize import sent_tokenize
from datetime import datetime

# Download tokenizer automatically (for Streamlit Cloud)
nltk.download("punkt", quiet=True)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Energy Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.big-title {
    font-size:38px !important;
    font-weight:700;
}
.card {
    padding:20px;
    border-radius:12px;
    background-color:#161b22;
    color:white;
    margin-bottom:20px;
}
.tag {
    padding:4px 10px;
    border-radius:20px;
    font-size:12px;
    font-weight:600;
}
.high { background-color:#ff4b4b; }
.medium { background-color:#ffa500; }
.low { background-color:#00c853; }
.sidebar .sidebar-content {
    background-color:#111;
}
</style>
""", unsafe_allow_html=True)

# ---------------- RSS SOURCES ----------------
RSS_SOURCES = {
    "Southeast Asia Energy": [
        "https://asian-power.com/rss.xml",
        "https://www.pv-tech.org/feed/",
    ],
    "Australia Energy": [
        "https://reneweconomy.com.au/feed/",
        "https://www.energynewsbulletin.net/rss",
    ],
    "AI in Financial Modelling": [
        "https://www.substack.com/feed",
        "https://towardsdatascience.com/feed",
    ]
}

# ---------------- FUNCTIONS ----------------

def summarize(text, sentences=3):
    sents = sent_tokenize(text)
    return " ".join(sents[:sentences])

def classify_impact(text):
    text = text.lower()
    if any(word in text for word in ["crisis", "surge", "ban", "war", "shock", "collapse"]):
        return "HIGH"
    elif any(word in text for word in ["growth", "increase", "policy", "investment"]):
        return "MEDIUM"
    else:
        return "LOW"

def fetch_articles(category):
    articles = []
    for url in RSS_SOURCES[category]:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.title,
                "summary": entry.summary if "summary" in entry else "",
                "link": entry.link,
                "published": entry.get("published", "N/A")
            })
    return articles

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Intelligence Filters")
category = st.sidebar.selectbox("Select Region / Theme", list(RSS_SOURCES.keys()))
run_scan = st.sidebar.button("Run Intelligence Scan")

# ---------------- HEADER ----------------
col1, col2, col3 = st.columns([4,1,1])

with col1:
    st.markdown('<p class="big-title">⚡ Energy Intelligence Terminal</p>', unsafe_allow_html=True)

with col2:
    st.metric("Region", category.split()[0])

with col3:
    st.metric("Updated", datetime.now().strftime("%H:%M"))

st.markdown("---")

# ---------------- MAIN LOGIC ----------------
if run_scan:

    articles = fetch_articles(category)

    if not articles:
        st.warning("No articles found. Try again later.")
    else:

        for article in articles:
            summary = summarize(article["summary"])
            impact = classify_impact(summary)

            if impact == "HIGH":
                tag_class = "tag high"
            elif impact == "MEDIUM":
                tag_class = "tag medium"
            else:
                tag_class = "tag low"

            st.markdown(f"""
            <div class="card">
                <h3>{article['title']}</h3>
                <p><i>{article['published']}</i></p>
                <p>{summary}</p>
                <span class="{tag_class}">{impact} IMPACT</span><br><br>
                <a href="{article['link']}" target="_blank" style="color:#4ea1ff;">Read Full Article</a>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("Select region and click 'Run Intelligence Scan' to begin.")
