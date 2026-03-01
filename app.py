import streamlit as st
import requests
from openai import OpenAI
import json

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="Energy Intelligence Terminal", layout="wide")
st.title("📊 Energy & Project Finance Intelligence Terminal")

# Sidebar
st.sidebar.header("Filters")

region = st.sidebar.selectbox(
    "Select Region",
    ["Global", "Americas", "EMEA", "Southeast Asia", "Australia/NZ"]
)

domains = st.sidebar.multiselect(
    "Select Domains",
    ["Renewable Energy", "Energy Policy", "Project Finance", "Model Auditing"],
    default=["Renewable Energy", "Energy Policy", "Project Finance", "Model Auditing"]
)

days = st.sidebar.slider("Last Days to Search", 7, 90, 30)
run_button = st.sidebar.button("Generate Intelligence")

SEARCH_QUERIES = {
    "Renewable Energy": "renewable energy capacity technology project",
    "Energy Policy": "energy policy regulation government target",
    "Project Finance": "energy project finance deal funding debt equity",
    "Model Auditing": "financial model audit project finance standard"
}

def serp_search(query):
    params = {
        "engine": "google",
        "q": f"{query} {region} last {days} days",
        "api_key": SERPAPI_KEY,
        "num": 3
    }
    resp = requests.get("https://serpapi.com/search", params=params)
    resp.raise_for_status()
    return resp.json().get("organic_results", [])

if run_button:
    st.spinner("🔎 Searching global intelligence...")

    collected_articles = []

    for dom in domains:
        results = serp_search(SEARCH_QUERIES[dom])
        for r in results:
            collected_articles.append({
                "domain": dom,
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "url": r.get("link", "")
            })

    if not collected_articles:
        st.warning("No articles found.")
    else:

        prompt = f"""
You are a senior energy intelligence analyst.

From the following articles (last {days} days, region: {region}):

1) Keep only credible, recent sources.
2) Summarize 3–5 highlights per domain.
3) Use format:

Domain:
Headline — one sentence
What happened — 2–3 sentences
Why it matters — 1–2 sentences
Source — URL

Then write a cross-domain synthesis paragraph.

Articles:
{json.dumps(collected_articles)}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        output = response.choices[0].message.content
        st.markdown(output)
