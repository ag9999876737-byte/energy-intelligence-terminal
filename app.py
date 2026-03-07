import streamlit as st
import feedparser
import re
import hashlib
import html
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

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
    padding: 18px;
    margin: 12px 0;
}

.deal-title{
    font-size:16px;
    font-weight:700;
}

.deal-money{
    font-size:20px;
    font-weight:800;
    color:#3fb950;
}

.tag{
    display:inline-block;
    padding:3px 8px;
    border-radius:20px;
    font-size:11px;
    margin-right:6px;
    background:#21262d;
}

.stat{
    background:#161b22;
    padding:12px;
    border-radius:8px;
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# CONFIG
# ------------------------------------------------

GN = "https://news.google.com/rss/search?hl=en&gl=SG&ceid=SG:en&q="

RSS_FEEDS = [

("Indonesia Deals", GN + "Indonesia+(investment OR acquisition OR financing OR project finance)"),
("Vietnam Deals", GN + "Vietnam+(investment OR acquisition OR financing OR project finance)"),
("Philippines Deals", GN + "Philippines+(investment OR acquisition OR financing)"),
("Thailand Deals", GN + "Thailand+(investment OR acquisition OR financing)"),
("Malaysia Deals", GN + "Malaysia+(investment OR acquisition OR financing)"),
("Singapore Deals", GN + "Singapore+(investment OR acquisition OR financing)"),

("SEA Infrastructure", GN + "Southeast Asia infrastructure investment"),
("SEA Renewable", GN + "Southeast Asia renewable energy investment"),

("Nikkei Asia","https://asia.nikkei.com/rss/feed/nar"),
("RenewEconomy","https://reneweconomy.com.au/feed/"),
("Bangkok Post","https://www.bangkokpost.com/rss/data/business.xml")

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

SECTORS = {
"⚡ Energy":["energy","solar","wind","battery","lng","renewable"],
"🏗 Infrastructure":["toll","road","rail","airport","port"],
"💻 Technology":["tech","ai","data","software"],
"🏢 Real Estate":["property","reit","data centre","warehouse"]
}

# ------------------------------------------------
# REGEX
# ------------------------------------------------

MONEY_PATTERN = re.compile(
r"""
(\$|US\$)?\s?
(\d+(?:,\d+)*(?:\.\d+)?)\s?
(trillion|billion|million|bn|mn|m|b)?
""",
re.IGNORECASE | re.VERBOSE
)

MULTIPLIER = {
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

    text=re.sub("<[^>]*>"," ",text)
    text=re.sub("\s+"," ",text)

    return text.strip()

def detect_country(text):

    text=text.lower()
    found=[]

    for k,v in COUNTRIES.items():
        if k in text:
            found.append(v)

    return found

def detect_sector(text):

    text=text.lower()

    for sector,keywords in SECTORS.items():

        if any(k in text for k in keywords):
            return sector

    return "🔹 General"

def extract_money(text):

    best=0
    raw=""

    for m in MONEY_PATTERN.finditer(text):

        num=m.group(2)
        unit=(m.group(3) or "").lower()

        try:
            value=float(num.replace(",",""))
        except:
            continue

        size=value*MULTIPLIER.get(unit,0)

        if size>best:

            best=size
            raw=m.group(0)

    return raw,best

def deal_score(text):

    score=0

    signals=[
    ("$",4),
    ("billion",4),
    ("acquisition",3),
    ("financing",3),
    ("project finance",4),
    ("investment",2)
    ]

    for word,val in signals:

        if word in text:
            score+=val

    return score

def is_recent(entry,days=7):

    try:

        if entry.published_parsed:

            dt=datetime(*entry.published_parsed[:6])

            return dt>=datetime.utcnow()-timedelta(days=days)

    except:
        pass

    return True

# ------------------------------------------------
# FETCH SINGLE FEED
# ------------------------------------------------

def fetch_feed(source):

    name,url=source

    deals=[]

    try:

        feed=feedparser.parse(url,request_headers={'User-Agent': 'Mozilla'})

        for entry in feed.entries:

            title=clean(entry.get("title",""))
            summary=clean(entry.get("summary",""))

            text=(title+" "+summary).lower()

            if not is_recent(entry,7):
                continue

            if deal_score(text)<3:
                continue

            countries=detect_country(text)

            if not countries:
                continue

            money,size=extract_money(text)

            deals.append({

            "title":title,
            "summary":summary[:300],
            "link":entry.get("link","#"),
            "source":name,
            "countries":countries,
            "sector":detect_sector(text),
            "money":money,
            "size":size,
            "score":deal_score(text)

            })

    except:

        pass

    return deals

# ------------------------------------------------
# FETCH ALL FEEDS (PARALLEL)
# ------------------------------------------------

@st.cache_data(ttl=3600)

def fetch_all():

    deals=[]

    with ThreadPoolExecutor(max_workers=6) as executor:

        results=executor.map(fetch_feed,RSS_FEEDS)

    for r in results:
        deals.extend(r)

    # deduplicate

    unique={}
    for d in deals:

        key=hashlib.md5((d["title"]+d["source"]).encode()).hexdigest()

        unique[key]=d

    deals=list(unique.values())

    deals.sort(key=lambda x:(x["size"],x["score"]),reverse=True)

    return deals

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.title("💰 Institutional Deal Radar")
st.caption("Infrastructure & Energy Deal Flow — Southeast Asia & Australia")

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

with st.spinner("Scanning global deal feeds..."):

    deals=fetch_all()

# ------------------------------------------------
# TOP DEALS
# ------------------------------------------------

top=[d for d in deals if d["size"]>500]

if top:

    st.subheader("🔥 Top Deals")

    for d in top[:5]:

        st.markdown(f"• **{d['title']}** ({d['money']})")

# ------------------------------------------------
# STATS
# ------------------------------------------------

total=len(deals)

value=sum(d["size"] for d in deals)

c1,c2,c3=st.columns(3)

with c1:
    st.markdown(f"<div class='stat'><b>{total}</b><br>Deals</div>",unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='stat'><b>${value:.0f}M</b><br>Total Value</div>",unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='stat'><b>{len(top)}</b><br>Large Deals</div>",unsafe_allow_html=True)

# ------------------------------------------------
# DISPLAY DEALS
# ------------------------------------------------

for d in deals:

    title=html.escape(d["title"])
    summary=html.escape(d["summary"])

    money_html=f"<div class='deal-money'>{d['money']}</div>" if d["money"] else ""

    tags="".join([f"<span class='tag'>{c}</span>" for c in d["countries"]])

    tags+=f"<span class='tag'>{d['sector']}</span>"

    html_block=f"""
    <div class="card">

    {tags}

    <div class="deal-title">{title}</div>

    {money_html}

    <div style="font-size:13px;margin-top:6px">{summary}</div>

    <div style="margin-top:8px">
    <a href="{d["link"]}" target="_blank">Read article</a>
    </div>

    </div>
    """

    st.markdown(html_block,unsafe_allow_html=True)

# ------------------------------------------------
# FOOTER
# ------------------------------------------------

st.markdown("---")

st.caption(
"Sources: Google News · Nikkei Asia · RenewEconomy · Bangkok Post | "
"Auto filtered for deal intelligence | Cached 1 hour"
)
