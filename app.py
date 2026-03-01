import streamlit as st
import os
from datetime import datetime, timedelta
import requests
from openai import OpenAI

# Load keys from secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
BING_SEARCH_KEY = st.secrets["BING_SEARCH_KEY"]

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

# Search settings
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
HEADERS = {"Ocp-Apim-Subscription-Key": BING_SEARCH_KEY}

SEARCH_QUERIES = {
    "Renewable Energy": ["renewable energy", "solar wind capacity news", "clean energy technology"],
    "Energy Policy": ["energy policy government target", "energy regulation 2025", "government energy strategy"],
    "Project Finance": ["energy project finance deal", "renewable financing", "energy investment closing"],
    "Model Auditing": ["financial model audit methodology", "model audit standard energy", "project finance model review"]
}

def bing_search(query):
    params = {"q": query + " " + region, "mkt": "en-US", "count": 10}
    resp = requests.get(BING_ENDPOINT, headers=HEADERS, params=params)
    resp.raise_for_status()
    results = resp.json().get("webPages", {}).get("value", [])
    return results

def extract_text_from_result(res):
    title = res.get("name", "")
    snippet = res.get("snippet", "") or ""
    url = res.get("url", "")
    return {"title": title, "content": snippet, "url": url}

def ai_summarize(article, domain):
    prompt = f"""
You are a senior energy intelligence analyst.

Classify and summarize the following article.
Only include it if it was published in the last {days} days and is relevant to {domain}.

Output JSON exactly:
{{
"title": "...",
"domain": "...",
"headline": "...",
"what_happened": "...",
"why_it_matters": "...",
"url": "..."
}}

Article Title: {article['title']}
Snippet: {article['content']}
URL: {article['url']}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return response.choices[0].message.content
    except:
        return None

if run_button:
    st.spinner("🔎 Searching and summarizing...")
    all_summaries = []

    for dom in domains:
        st.subheader(f"📌 {dom}")

        for q in SEARCH_QUERIES[dom]:
            results = bing_search(q)
            for r in results:
                art = extract_text_from_result(r)
                summary = ai_summarize(art, dom)
                if summary:
                    with st.expander(art["title"]):
                        st.markdown(summary)
                        all_summaries.append(summary)

    # Global synthesis
    if all_summaries:
        synth_prompt = f"""
You are an expert analyst. Based on these summaries:
{all_summaries}

Write a one-paragraph cross-domain synthesis highlighting connecting themes.
"""
        synth = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": synth_prompt}]
        )
        st.subheader("🧠 Cross-Domain Synthesis")
        st.write(synth.choices[0].message.content)
