import streamlit as st
import feedparser
import re
import hashlib
from datetime import datetime, timedelta

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="Institutional Deal Radar",
    page_icon="💰",
    layout="wide"
)

# ------------------------------------------------
# STYLES
# ------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

.card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
}

.deal-title{
    font-size:16px;
    font-weight:700;
}

.deal-money{
    font-size:22px;
    font-weight:800;
    color:#3fb950;
}

.tag{
    display:inline-block;
    padding:3px 10px;
    border-radius:20px;
    font-size:11px;
    margin-right:6px;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# CONFIG
# ------------------------------------------------

GN = "https://news.google.com/rss/search?hl=en&gl=SG&ceid=SG:en&q="

RSS_FEEDS = [

("Indonesia Deals", GN + "Indonesia+(investment OR acquisition OR financing)"),
("Vietnam Deals", GN + "Vietnam+(investment OR acquisition OR financing)"),
("Philippines Deals", GN + "Philippines+(investment OR acquisition OR financing)"),
("Thailand Deals", GN + "Thailand+(investment OR acquisition OR financing)"),
("Malaysia Deals", GN + "Malaysia+(investment OR acquisition OR financing)"),
("Singapore Deals", GN + "Singapore+(investment OR acquisition OR financing)"),

("SEA Infrastructure", GN + "Southeast Asia infrastructure investment"),
("SEA Renewable", GN + "Southeast Asia renewable energy investment"),

("Nikkei Asia","https://asia.nikkei.com/rss/feed/nar"),
("RenewEconomy","https://reneweconomy.com.au/feed/"),

]

COUNTRIES = {
"indonesia":"🇮🇩 Indonesia",
"vietnam":"🇻🇳 Vietnam",
"philippines":"🇵🇭 Philippines",
"thailand":"🇹🇭 Thailand",
"malaysia":"🇲🇾 Malaysia",
"singapore":"🇸🇬 Singapore",
"australia":"🇦🇺 Australia"
}

# ------------------------------------------------
# REGEX
# ------------------------------------------------

MONEY_PATTERN = re.compile(
r"""
(?:\$|US\$|USD|A\$|S\$)?\s?
(\d+(?:,\d+)*(?:\.\d+)?)\s?
(trillion|billion|million|bn|mn|m|b)?
""",
re.IGNORECASE | re.VERBOSE
)

SIZE_MULTIPLIER = {
"trillion":1000000,
"billion":1000,
"bn":1000,
"million":1,
"mn":1,
"m":1,
"b":1000
}

# ------------------------------------------------
# HELPERS
# ------------------------------------------------

def clean(text):

    if not text:
        return ""

    text = re.sub("<[^>]*>"," ",text)
    text = re.sub("\s+"," ",text)

    return text.strip()

def is_recent(entry, days=7):

    try:

        if entry.published_parsed:
            published=datetime(*entry.published_parsed[:6])
            return published >= datetime.utcnow() - timedelta(days=days)

    except:
        pass

    return True

def detect_country(text):

    text=text.lower()

    result=[]

    for k,v in COUNTRIES.items():
        if k in text:
            result.append(v)

    return result

def extract_money(text):

    best_value=0
    best_raw=""

    for m in MONEY_PATTERN.finditer(text):

        num=m.group(1)
        unit=(m.group(2) or "").lower()

        try:
            value=float(num.replace(",",""))
        except:
            continue

        multiplier=SIZE_MULTIPLIER.get(unit,0)

        size=value*multiplier

        if size>best_value:
            best_value=size
            best_raw=m.group(0)

    return best_raw,best_value

# ------------------------------------------------
# FETCH DEALS
# ------------------------------------------------

@st.cache_data(ttl=3600)

def fetch_deals():

    deals=[]

    for source,url in RSS_FEEDS:

        try:

            feed=feedparser.parse(url)

            for entry in feed.entries:

                title=clean(entry.get("title",""))
                summary=clean(entry.get("summary",""))

                text=(title+" "+summary).lower()

                if not is_recent(entry,7):
                    continue

                countries=detect_country(text)

                if not countries:
                    continue

                money,size=extract_money(text)

                deals.append({

                "title":title,
                "summary":summary[:300],
                "link":entry.get("link","#"),
                "source":source,
                "money":money,
                "size":size,
                "countries":countries

                })

        except:
            continue

    return deals

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.title("💰 Institutional Deal Radar")
st.caption("Infrastructure & Energy deal flow — Southeast Asia & Australia")

# ------------------------------------------------
# LOAD DEALS
# ------------------------------------------------

with st.spinner("Fetching deals..."):

    deals=fetch_deals()

# ------------------------------------------------
# DISPLAY
# ------------------------------------------------

for d in deals:

    money_html=f"<div class='deal-money'>{d['money']}</div>" if d["money"] else ""

    country_tags="".join([f"<span class='tag'>{c}</span>" for c in d["countries"]])

    html=f"""
    <div class="card">
    {country_tags}
    <div class="deal-title">{d["title"]}</div>
    {money_html}
    <div>{d["summary"]}</div>
    <a href="{d["link"]}" target="_blank">Read article</a>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
