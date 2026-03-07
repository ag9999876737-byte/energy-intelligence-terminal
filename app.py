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

.stat-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.stat-num {
    font-size: 28px;
    font-weight: 800;
    color: #58a6ff;
}
.stat-label {
    font-size: 12px;
    color: #8b949e;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
    transition: border-color 0.2s;
}
.card:hover { border-color: #388bfd; }

.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 8px;
    letter-spacing: 0.3px;
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
.tag-type-general     { background:#1c2128; color:#8b949e; border:1px solid #30363d; }

.tag-sector           { background:#1c2128; color:#a5d6ff; border:1px solid #30363d; }
.tag-country          { background:#1c2128; color:#ffa198; border:1px solid #30363d; }

.deal-title {
    font-size: 16px;
    font-weight: 700;
    color: #e6edf3;
    margin: 10px 0 6px 0;
    line-height: 1.4;
}
.deal-money {
    font-size: 22px;
    font-weight: 800;
    color: #3fb950;
    margin: 4px 0 10px 0;
}
.deal-meta {
    font-size: 12px;
    color: #8b949e;
    margin-bottom: 10px;
}
.deal-summary {
    font-size: 13px;
    color: #c9d1d9;
    line-height: 1.6;
    border-left: 3px solid #21262d;
    padding-left: 12px;
    margin: 10px 0;
}
.read-more {
    font-size: 12px;
    color: #58a6ff;
    text-decoration: none;
    font-weight: 600;
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
.section-header {
    font-size: 18px;
    font-weight: 700;
    color: #e6edf3;
    margin: 28px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
}
.no-deals {
    background: #161b22;
    border: 1px dashed #30363d;
    border-radius: 10px;
    padding: 40px;
    text-align: center;
    color: #8b949e;
}
</style>

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# CONFIGURATION

# ─────────────────────────────────────────────

# Google News RSS – always reachable from Streamlit Cloud, aggregates Reuters/Bloomberg/FT etc.

# Each query is scoped to a country + deal keyword for high precision

_GN = “https://news.google.com/rss/search?hl=en&gl=SG&ceid=SG:en&q=”

RSS_FEEDS = [
# – Country-specific deal queries via Google News –
(“GNews: Indonesia deals”,      _GN + “Indonesia+investment+OR+acquisition+OR+financing”),
(“GNews: Vietnam deals”,        _GN + “Vietnam+investment+OR+acquisition+OR+financing”),
(“GNews: Philippines deals”,    _GN + “Philippines+investment+OR+acquisition+OR+financing”),
(“GNews: Thailand deals”,       _GN + “Thailand+investment+OR+acquisition+OR+financing”),
(“GNews: Malaysia deals”,       _GN + “Malaysia+investment+OR+acquisition+OR+financing”),
(“GNews: Singapore deals”,      _GN + “Singapore+investment+OR+acquisition+OR+financing”),
(“GNews: Australia deals”,      _GN + “Australia+infrastructure+OR+acquisition+OR+financing”),
# – Sector-specific queries –
(“GNews: SEA renewables”,       _GN + “Southeast+Asia+renewable+energy+investment+OR+solar+OR+wind”),
(“GNews: SEA infrastructure”,   _GN + “Southeast+Asia+infrastructure+investment+OR+financing”),
(“GNews: AUS energy”,           _GN + “Australia+energy+investment+OR+financing+OR+acquisition”),
# – Direct sources still reachable from Streamlit Cloud –
(“Nikkei Asia”,                 “https://asia.nikkei.com/rss/feed/nar”),
(“RenewEconomy”,                “https://reneweconomy.com.au/feed/”),
(“Bangkok Post Business”,       “https://www.bangkokpost.com/rss/data/business.xml”),
]

COUNTRIES = {
“indonesia”:   “🇮🇩 Indonesia”,
“vietnam”:     “🇻🇳 Vietnam”,
“philippines”: “🇵🇭 Philippines”,
“thailand”:    “🇹🇭 Thailand”,
“malaysia”:    “🇲🇾 Malaysia”,
“singapore”:   “🇸🇬 Singapore”,
“australia”:   “🇦🇺 Australia”,
}

DEAL_KEYWORDS = [
“financing”, “investment”, “acquisition”, “merger”,
“raised”, “secured”, “closed”, “deal”, “equity”,
“debt”, “refinancing”, “buyout”, “fund”, “capital”,
“ipo”, “listing”, “bond”, “facility”, “infrastructure”
]

DEAL_TYPES = {
“M&A”:             [“acquisition”, “merger”, “takeover”, “buys”, “acquires”, “buyout”, “stake”],
“Project Finance”: [“financing”, “project finance”, “refinancing”, “debt facility”, “loan”, “bond”],
“Private Equity”:  [“private equity”, “pe firm”, “fund”, “portfolio”, “growth capital”],
“IPO / Equity”:    [“ipo”, “listing”, “public offering”, “equity raise”, “raised equity”],
“Green Finance”:   [“green bond”, “sustainability”, “esg”, “renewable”, “solar”, “wind”, “battery”],
}

SECTORS = {
“⚡ Energy & Renewables”: [“solar”, “wind”, “hydro”, “energy”, “power”, “battery”, “grid”, “renewable”, “lng”, “gas”],
“🏗 Infrastructure”:      [“toll”, “port”, “airport”, “road”, “rail”, “water”, “telecom”, “tower”, “fibre”],
“🏢 Real Estate”:         [“property”, “reit”, “real estate”, “data centre”, “logistics”, “warehouse”],
“💻 Technology”:          [“tech”, “fintech”, “software”, “data”, “cloud”, “ai”, “digital”, “saas”],
“⛏ Resources”:           [“mining”, “oil”, “coal”, “metals”, “copper”, “nickel”, “gold”, “commodity”],
“🏦 Financial Services”:  [“bank”, “insurance”, “asset management”, “financial services”, “wealth”],
}

STATUS_SIGNALS = {
“🟢 Closed”:       [“closed”, “completed”, “finalised”, “finalized”, “signs”, “signed”],
“🟠 In Progress”:  [“agreed”, “announced”, “plans to”, “entered into”, “set to”],
“🟡 Rumoured”:     [“could”, “may”, “considering”, “exploring”, “in talks”, “eyeing”, “weighing”],
}

MONEY_PATTERN = re.compile(
r”””
(?:US$|A$|S$|HK$|$|USD|AUD|SGD|IDR|THB|PHP|MYR|€|£|¥)\s?
(\d{1,3}(?:[.,]\d{3})*(?:.\d+)?)\s?
(trillion|billion|million|bn|mn|m|b|t)?
|
(\d{1,3}(?:[.,]\d{3})*(?:.\d+)?)\s?
(trillion|billion|million|bn|mn|m|b|t)\s?
(?:dollars?|USD|AUD|SGD|ringgit|baht|peso)?
“””,
re.IGNORECASE | re.VERBOSE
)

SIZE_MULTIPLIERS = {
“trillion”: 1_000_000, “billion”: 1_000, “bn”: 1_000,
“million”: 1, “mn”: 1, “m”: 1,
“b”: 1_000, “t”: 1_000_000,
}

MIN_DEAL_SIZE_M = 50   # Filter deals below $50M equivalent

# ─────────────────────────────────────────────

# CORE FUNCTIONS

# ─────────────────────────────────────────────

def is_recent(entry, days=7):
try:
published = datetime(*entry.published_parsed[:6])
return published >= (datetime.utcnow() - timedelta(days=days))
except Exception:
# Fall back to checking ‘updated_parsed’
try:
updated = datetime(*entry.updated_parsed[:6])
return updated >= (datetime.utcnow() - timedelta(days=days))
except Exception:
return True   # Include if date unparseable – better than silent drop

def clean(text):
text = re.sub(r’<[^>]+>’, ’ ‘, text)
text = re.sub(r’\s+’, ’ ’, text)
return text.strip()

def clean_lower(text):
return clean(text).lower()

def detect_countries(text):
found = []
for key, label in COUNTRIES.items():
if key in text:
found.append(label)
return found

def classify_deal_type(text):
for deal_type, keywords in DEAL_TYPES.items():
if any(kw in text for kw in keywords):
return deal_type
return “General”

def classify_sector(text):
for sector, keywords in SECTORS.items():
if any(kw in text for kw in keywords):
return sector
return “🔹 General”

def get_deal_status(text):
for status, signals in STATUS_SIGNALS.items():
if any(s in text for s in signals):
return status
return “📋 Reported”

def extract_money(text):
“”“Returns (display_string, size_in_millions) for the largest amount found.”””
best_raw = “”
best_size = 0.0

```
for m in MONEY_PATTERN.finditer(text):
    # Group 1+2 or Group 3+4
    num_str = m.group(1) or m.group(3)
    unit    = (m.group(2) or m.group(4) or "").lower().strip()
    if not num_str:
        continue
    try:
        num = float(num_str.replace(",", ""))
    except ValueError:
        continue

    multiplier = SIZE_MULTIPLIERS.get(unit, 1)
    size_m = num * multiplier

    if size_m > best_size:
        best_size = size_m
        # Pretty display
        full_match = m.group(0).strip()
        best_raw = full_match

return best_raw, best_size
```

def deduplicate(deals):
seen = set()
unique = []
for d in deals:
# Hash on normalised title
key = hashlib.md5(
re.sub(r’\W+’, ‘’, d[“title”].lower()).encode()
).hexdigest()
if key not in seen:
seen.add(key)
unique.append(d)
return unique

def format_date(entry):
for attr in (“published_parsed”, “updated_parsed”):
try:
t = getattr(entry, attr, None)
if t:
return datetime(*t[:6]).strftime(”%d %b %Y”)
except Exception:
pass
return entry.get(“published”, “Unknown date”)

# ─────────────────────────────────────────────

# FEED FETCHER  (cached 1 hour)

# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_deals(days_back: int, min_size: int):
deals = []
feed_status = []

```
for source_name, url in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            feed_status.append(("error", source_name, "Feed unreachable or malformed"))
            continue

        count_before = len(deals)

        for entry in feed.entries:
            title   = clean_lower(entry.get("title", ""))
            summary = clean_lower(entry.get("summary", entry.get("description", "")))
            combined = title + " " + summary

            # ── Filters ──────────────────────────────────
            if not is_recent(entry, days=days_back):
                continue
            if not any(kw in combined for kw in DEAL_KEYWORDS):
                continue

            countries_found = detect_countries(combined)
            if not countries_found:
                continue

            money_str, size_m = extract_money(combined)
            if money_str and size_m < min_size:
                continue

            # ── Classifiers ──────────────────────────────
            deal_type   = classify_deal_type(combined)
            sector      = classify_sector(combined)
            status      = get_deal_status(combined)

            deals.append({
                "title":     clean(entry.get("title", "No title")),
                "summary":   clean(entry.get("summary", entry.get("description", "")))[:400],
                "link":      entry.get("link", "#"),
                "date":      format_date(entry),
                "source":    source_name,
                "countries": countries_found,
                "money":     money_str,
                "size_m":    size_m,
                "type":      deal_type,
                "sector":    sector,
                "status":    status,
            })

        added = len(deals) - count_before
        feed_status.append(("ok", source_name, f"{added} deal(s) matched"))

    except Exception as e:
        feed_status.append(("error", source_name, str(e)[:80]))

deals = deduplicate(deals)
deals.sort(key=lambda x: x["size_m"], reverse=True)
return deals, feed_status
```

# ─────────────────────────────────────────────

# UI HELPERS

# ─────────────────────────────────────────────

TYPE_TAG_CLASS = {
“M&A”:             “tag-type-ma”,
“Project Finance”: “tag-type-pf”,
“Private Equity”:  “tag-type-pe”,
“IPO / Equity”:    “tag-type-ipo”,
“Green Finance”:   “tag-type-green”,
“General”:         “tag-type-general”,
}

STATUS_TAG_CLASS = {
“🟢 Closed”:      “tag-status-closed”,
“🟠 In Progress”: “tag-status-progress”,
“🟡 Rumoured”:    “tag-status-rumoured”,
“📋 Reported”:    “tag-status-reported”,
}

def render_card(d):
status_cls = STATUS_TAG_CLASS.get(d[“status”], “tag-status-reported”)
type_cls   = TYPE_TAG_CLASS.get(d[“type”], “tag-type-general”)

```
country_tags = "".join(
    f'<span class="tag tag-country">{c}</span>' for c in d["countries"]
)
money_block = (
    f'<div class="deal-money">💵 {d["money"]}</div>'
    if d["money"] else ""
)
summary_block = (
    f'<div class="deal-summary">{d["summary"]}…</div>'
    if d["summary"] else ""
)

# NOTE: No blank lines inside the HTML string -- blank lines cause Streamlit's
# markdown parser to break out of unsafe_allow_html mode, leaking raw tags.
html = (
    f'<div class="card">'
    f'<span class="tag {status_cls}">{d["status"]}</span>'
    f'<span class="tag {type_cls}">{d["type"]}</span>'
    f'<span class="tag tag-sector">{d["sector"]}</span>'
    f'{country_tags}'
    f'<div class="deal-title">{d["title"]}</div>'
    f'{money_block}'
    f'<div class="deal-meta">📅 {d["date"]} &nbsp;|&nbsp; 🗞 {d["source"]}</div>'
    f'{summary_block}'
    f'<a class="read-more" href="{d["link"]}" target="_blank">🔗 Read full article →</a>'
    f'</div>'
)
st.markdown(html, unsafe_allow_html=True)
```

# ─────────────────────────────────────────────

# SIDEBAR FILTERS

# ─────────────────────────────────────────────

with st.sidebar:
st.markdown(”### ⚙️ Filters”)
st.markdown(”—”)

```
days_back = st.slider("Days back", 1, 30, 7)
min_size  = st.slider("Min deal size ($M equivalent)", 0, 500, 50, step=25)

st.markdown("**Deal Type**")
all_types   = list(DEAL_TYPES.keys()) + ["General"]
type_filter = st.multiselect("", all_types, default=all_types, label_visibility="collapsed")

st.markdown("**Sector**")
all_sectors    = list(SECTORS.keys()) + ["🔹 General"]
sector_filter  = st.multiselect("", all_sectors, default=all_sectors, label_visibility="collapsed")

st.markdown("**Country**")
country_labels = list(COUNTRIES.values())
country_filter = st.multiselect("", country_labels, default=country_labels, label_visibility="collapsed")

st.markdown("**Status**")
all_statuses   = list(STATUS_SIGNALS.keys()) + ["📋 Reported"]
status_filter  = st.multiselect("", all_statuses, default=all_statuses, label_visibility="collapsed")

st.markdown("---")
show_feed_health = st.checkbox("Show feed health", value=False)

if st.button("🔄 Refresh now", use_container_width=True):
    st.cache_data.clear()
```

# ─────────────────────────────────────────────

# HEADER

# ─────────────────────────────────────────────

st.markdown(”””

<div class="header-block">
    <div class="header-title">💰 Institutional Deal Radar</div>
    <div class="header-sub">
        Infrastructure &amp; Energy deal flow -- Southeast Asia &amp; Australia
        &nbsp;·&nbsp; Live from institutional RSS sources &nbsp;·&nbsp; Cached 1 hr
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────

# FETCH + APPLY FILTERS

# ─────────────────────────────────────────────

with st.spinner(“Fetching deals from institutional sources…”):
all_deals, feed_status = fetch_deals(days_back, min_size)

# Apply sidebar filters

filtered = [
d for d in all_deals
if d[“type”]   in type_filter
and d[“sector”] in sector_filter
and d[“status”] in status_filter
and any(c in country_filter for c in d[“countries”])
]

# ─────────────────────────────────────────────

# STATS ROW

# ─────────────────────────────────────────────

total_value = sum(d[“size_m”] for d in filtered if d[“size_m”] > 0)
value_str   = f”${total_value/1000:.1f}B” if total_value >= 1000 else f”${total_value:.0f}M”

closed_count   = sum(1 for d in filtered if “Closed”   in d[“status”])
inprog_count   = sum(1 for d in filtered if “Progress” in d[“status”])
rumoured_count = sum(1 for d in filtered if “Rumoured” in d[“status”])

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
st.markdown(f’<div class="stat-box"><div class="stat-num">{len(filtered)}</div><div class="stat-label">Total Deals</div></div>’, unsafe_allow_html=True)
with col2:
st.markdown(f’<div class="stat-box"><div class="stat-num">{value_str}</div><div class="stat-label">Identified Value</div></div>’, unsafe_allow_html=True)
with col3:
st.markdown(f’<div class="stat-box"><div class="stat-num">{closed_count}</div><div class="stat-label">Closed</div></div>’, unsafe_allow_html=True)
with col4:
st.markdown(f’<div class="stat-box"><div class="stat-num">{inprog_count}</div><div class="stat-label">In Progress</div></div>’, unsafe_allow_html=True)
with col5:
st.markdown(f’<div class="stat-box"><div class="stat-num">{rumoured_count}</div><div class="stat-label">Rumoured</div></div>’, unsafe_allow_html=True)

st.markdown(”<br>”, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# FEED HEALTH (optional)

# ─────────────────────────────────────────────

if show_feed_health:
st.markdown(’<div class="section-header">📡 Feed Health</div>’, unsafe_allow_html=True)
for status, name, msg in feed_status:
icon  = “✅” if status == “ok” else “❌”
color = “#3fb950” if status == “ok” else “#ffa198”
st.markdown(
f’<div class="feed-error" style="color:{color};border-color:{color}30;">’
f’{icon} <b>{name}</b> – {msg}</div>’,
unsafe_allow_html=True
)
st.markdown(”<br>”, unsafe_allow_html=True)

# ─────────────────────────────────────────────

# DEAL CARDS – grouped by type

# ─────────────────────────────────────────────

if not filtered:
st.markdown(”””
<div class="no-deals">
<div style="font-size:36px">🔍</div>
<div style="font-size:16px;font-weight:600;margin-top:10px">No deals match your filters</div>
<div style="font-size:13px;margin-top:6px;color:#8b949e">
Try expanding the date range, lowering the minimum size, or adjusting filters in the sidebar.
</div>
</div>
“””, unsafe_allow_html=True)
else:
# Group deals by type for scannability
groups = {}
for d in filtered:
groups.setdefault(d[“type”], []).append(d)

```
# Preferred display order
ORDER = ["M&A", "Project Finance", "Private Equity", "IPO / Equity", "Green Finance", "General"]
for group_name in ORDER:
    group_deals = groups.get(group_name, [])
    if not group_deals:
        continue
    st.markdown(
        f'<div class="section-header">{group_name} &nbsp;<span style="font-size:14px;color:#8b949e;font-weight:400">({len(group_deals)} deal{"s" if len(group_deals)!=1 else ""})</span></div>',
        unsafe_allow_html=True
    )
    for d in group_deals:
        render_card(d)
```

# ─────────────────────────────────────────────

# FOOTER

# ─────────────────────────────────────────────

st.markdown(”—”)
st.caption(
“Sources: Google News (Reuters/Bloomberg/FT aggregated) · Nikkei Asia · RenewEconomy · Bangkok Post  ·  “
“”
f”Filters: last {days_back}d, min ${min_size}M  ·  Cached 1 hr  ·  “
f”Last loaded: {datetime.utcnow().strftime(’%d %b %Y %H:%M’)} UTC”
)
