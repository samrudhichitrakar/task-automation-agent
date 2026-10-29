import logging
import os
import time
from datetime import datetime, timezone

import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI

APP_NAME = "Task Automation Research Agent"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("research_agent")

st.set_page_config(page_title=APP_NAME, page_icon="🔎", layout="centered")
st.title("🔎 Task Automation Research Agent")
st.write("Enter a topic to search the web and generate a concise three-point research brief.")
st.caption("MLOps Experiment 10 · Streamlit · DuckDuckGo · OpenAI")

topic = st.text_input("Research topic", placeholder="e.g., applications of AI in healthcare")
run = st.button("Research topic", type="primary", disabled=not bool(topic.strip()))

def search_web(query: str, max_results: int = 6) -> list[dict]:
    results = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            title = item.get("title", "").strip()
            body = item.get("body", "").strip()
            href = item.get("href", "").strip()
            if title and body:
                results.append({"title": title, "body": body, "url": href})
    return results

def make_brief(query: str, results: list[dict], api_key: str) -> str:
    if not results:
        return "No search results were returned. Try a more specific topic."
    if not api_key:
        # Helpful fallback for local UI testing; live AI summarization requires a key.
        return "\n".join(
            f"{i}. **{item['title']}** — {item['body']}"
            for i, item in enumerate(results[:3], start=1)
        )
    client = OpenAI(api_key=api_key)
    source_text = "\n\n".join(
        f"Source {i}: {item['title']}\n{item['body']}\nURL: {item['url']}"
        for i, item in enumerate(results, start=1)
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": (
                "You are a careful research assistant. Use only the supplied search snippets. "
                "Return exactly three concise bullet points. Avoid unsupported claims and "
                "include source URLs in the relevant bullets when possible."
            )},
            {"role": "user", "content": f"Topic: {query}\n\nSearch results:\n{source_text}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "The model returned an empty response."

if run:
    started = time.perf_counter()
    logger.info("Research request received: topic=%r", topic.strip())
    try:
        with st.spinner("Searching the web and preparing your brief..."):
            results = search_web(topic.strip())
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            brief = make_brief(topic.strip(), results, api_key)
        elapsed = time.perf_counter() - started
        logger.info("Research request completed: topic=%r elapsed_seconds=%.2f results=%d",
                    topic.strip(), elapsed, len(results))
        st.subheader("Three-point research brief")
        st.markdown(brief)
        if results:
            with st.expander("Sources found"):
                for i, item in enumerate(results, start=1):
                    st.markdown(f"{i}. [{item['title']}]({item['url']})")
        if not api_key:
            st.warning("OPENAI_API_KEY is not configured. Showing the top search snippets instead of an AI-generated summary.")
        st.caption(f"Completed in {elapsed:.2f} seconds · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    except Exception as exc:
        elapsed = time.perf_counter() - started
        logger.exception("Research request failed: topic=%r elapsed_seconds=%.2f",
                         topic.strip(), elapsed)
        st.error("The request failed. Check the app logs and API/search configuration, then try again.")
        st.caption(f"Elapsed time: {elapsed:.2f} seconds")
