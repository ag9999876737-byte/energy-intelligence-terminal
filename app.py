import streamlit as st
import feedparser
import re
import hashlib
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Institutional Deal Radar",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

.header-block {
    padding: 28px 0 10px 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 24px;
}

.header-title {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
}

.header-sub {
    font-size: 14px;
    color: #8b949e;
    margin-top: 4px;
}

.card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
}

.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 8px;
}

.tag-status-closed    { background:#0d4429; color:#3fb950; border:1px solid #238636; }
.tag-status-progress  { background:#341a00; color:#e3b341; border:1px solid #9e6a03; }
.tag-status-rumoured  { background:#2d1f00; color:#ffa657; border:1px solid #9b4c00; }
.tag-status-reported  { background:#1c2128; color:#8b949e; border:1px solid #30363d; }

.tag-type-ma          { background:#1a1f6e; color:#79c0ff; border:1px solid #388bfd; }
.tag-type-pf          { background:#1a3a1f; color:#56d364; border:1px solid #238636; }
.tag-type-pe          { background:#3d1a6e; color:#d2a8ff; border:1px solid #8957e5; }
.tag-type-ipo         { background:#3d2a00; color:#ffa657; border:1px solid #9b4c00; }
.tag-type-green       { background:#0d3320; color:#3fb950; border:1px solid #196c2e; }

.deal-title {
    font-size: 16px;
    font-weight: 700;
    margin: 10px 0 6px 0;
}

.deal-money {
    font-size: 22px;
    font-weight: 800;
    color: #3fb950;
}

.deal-meta {
    font-size: 12px;
    color: #8b949e;
    margin-bottom: 10px;
}

.read-more {
    font-size: 12px;
    color: #58a6ff;
    text-decoration: none;
}

.section-header {
    font-size: 18px;
    font-weight: 700;
    margin: 28px 0 12px 0;
    border-bottom: 1px solid #21262d;
}

.feed-error {
    background: #2d1515;
    border: 1px solid #6e1a1a;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #ffa198;
    margin: 4px 0;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RSS SOURCES
# ─────────────────────────────────────────────

RSS_FEEDS = [
    ("Nikkei Asia","https://asia.nikkei.com/rss/feed/nar"),
    ("RenewEconomy","https://reneweconomy.com.au/feed/"),
    ("Reuters Business","https://feeds.reuters.com/reuters/businessNews"),
    ("Bangkok Post Business","https://www.bangkokpost.com/rss/data/business.xml"),
    ("Vietnam Investment Review","https://vir.com.vn/rss/finance.rss"),
    ("Eco-Business","https://www.eco-business.com/rss/news/"),
    ("GlobeNewswire M&A","https://globenewswire.com/RssFeed/subjectcode/M109"),
    ("PR Newswire Finance","https://www.prnewswire.com/rss/financial-news.rss"),
    ("Business Wire M&A","https://feeds.businesswire.com/rss/home/?rss=G22"),
]

COUNTRIES = {
    "indonesia":"🇮🇩 Indonesia",
    "vietnam":"🇻🇳 Vietnam",
    "philippines":"🇵🇭 Philippines",
    "thailand":"🇹🇭 Thailand",
    "malaysia":"🇲🇾 Malaysia",
    "singapore":"🇸🇬 Singapore",
    "australia":"🇦🇺 Australia",
}

DEAL_KEYWORDS = [
    "financing","investment","acquisition","merger","raised","secured",
    "closed","deal","equity","debt","refinancing","buyout","fund",
    "capital","ipo","listing","bond","facility","infrastructure"
]

# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────

def clean(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_lower(text):
    return clean(text).lower()

def detect_countries(text):
    found=[]
    for key,label in COUNTRIES.items():
        if key in text:
            found.append(label)
    return found

def is_recent(entry,days=7):
    try:
        published=datetime(*entry.published_parsed[:6])
        return published >= datetime.utcnow()-timedelta(days=days)
    except:
        return True

def deduplicate(deals):
    seen=set()
    unique=[]
    for d in deals:
        key=hashlib.md5(re.sub(r'\W+','',d["title"].lower()).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique

# ─────────────────────────────────────────────
# FETCH DEALS
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_deals(days_back):

    deals=[]
    feed_status=[]

    for source,url in RSS_FEEDS:

        try:
            feed=feedparser.parse(url)

            if not feed.entries:
                feed_status.append(("error",source,"Feed unreachable"))
                continue

            for entry in feed.entries:

                title=clean_lower(entry.get("title",""))
                summary=clean_lower(entry.get("summary",""))
                combined=title+" "+summary

                if not any(k in combined for k in DEAL_KEYWORDS):
                    continue

                if not is_recent(entry,days_back):
                    continue

                countries=detect_countries(combined)

                if not countries:
                    continue

                deals.append({
                    "title":clean(entry.get("title","")),
                    "summary":clean(summary)[:300],
                    "link":entry.get("link","#"),
                    "source":source,
                    "countries":countries,
                    "date":entry.get("published","")
                })

            feed_status.append(("ok",source,"Loaded"))

        except Exception as e:

            feed_status.append(("error",source,str(e)))

    deals=deduplicate(deals)

    return deals,feed_status

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:

    st.markdown("### ⚙️ Filters")

    days_back=st.slider("Days back",1,30,7)

    country_filter=st.multiselect(
        "Countries",
        list(COUNTRIES.values()),
        default=list(COUNTRIES.values())
    )

    show_feed_health=st.checkbox("Show feed health")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="header-block">
<div class="header-title">💰 Institutional Deal Radar</div>
<div class="header-sub">
Infrastructure & Energy deals — Southeast Asia & Australia
</div>
</div>
""",unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

with st.spinner("Fetching deals..."):

    deals,feed_status=fetch_deals(days_back)

filtered=[
d for d in deals
if any(c in country_filter for c in d["countries"])
]

# ─────────────────────────────────────────────
# DEAL DISPLAY
# ─────────────────────────────────────────────

st.markdown(f'<div class="section-header">Deals ({len(filtered)})</div>',unsafe_allow_html=True)

for d in filtered:

    countries=" ".join(d["countries"])

    st.markdown(f"""
<div class="card">
<span class="tag">{countries}</span>
<div class="deal-title">{d["title"]}</div>
<div class="deal-meta">{d["date"]} | {d["source"]}</div>
<div>{d["summary"]}</div>
<a class="read-more" href="{d["link"]}" target="_blank">Read article →</a>
</div>
""",unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FEED HEALTH
# ─────────────────────────────────────────────

if show_feed_health:

    st.markdown('<div class="section-header">Feed Health</div>',unsafe_allow_html=True)

    for status,name,msg in feed_status:

        icon="✅" if status=="ok" else "❌"

        st.markdown(
            f'<div class="feed-error">{icon} <b>{name}</b> — {msg}</div>',
            unsafe_allow_html=True
        )
