import streamlit as st
import requests
from openai import OpenAI

# Load keys
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
        "num": 5
    }
    resp = requests.get("https://serpapi.com/search", params=params)
    resp.raise_for_status()
    results = resp.json().get("organic_results", [])
    return results

def summarize_with_ai(title, snippet, url, domain):
    prompt = f"""
You are a senior energy intelligence analyst.

Only include if within last {days} days and highly credible.

Output format:

Headline — one sentence
What happened — 2-3 sentences
Why it matters — 1-2 sentences
Source — {url}

Article Title: {title}
Snippet: {snippet}
Domain Focus: {domain}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if run_button:
    st.spinner("🔎 Searching global intelligence...")
    
    all_summaries = []

    for dom in domains:
        st.subheader(f"📌 {dom}")
        results = serp_search(SEARCH_QUERIES[dom])

        for r in results:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            url = r.get("link", "")

            summary = summarize_with_ai(title, snippet, url, dom)

            with st.expander(title):
                st.write(summary)
                all_summaries.append(summary)

    if all_summaries:
        synthesis_prompt = f"""
Based on these insights:
{all_summaries}

Write a one-paragraph cross-domain synthesis highlighting key themes.
"""
        synth = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        st.subheader("🧠 Cross-Domain Synthesis")
        st.write(synth.choices[0].message.content)
