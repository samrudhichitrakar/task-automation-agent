import os
import time
import logging
from datetime import datetime

import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Task Automation Research Agent",
    page_icon="🔎",
    layout="centered"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# GROQ CONFIGURATION
# --------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)


def get_groq_client():
    """Create a Groq client using the OpenAI-compatible SDK."""

    if not GROQ_API_KEY:
        return None

    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


# --------------------------------------------------
# WEB SEARCH
# --------------------------------------------------

def search_web(topic, max_results=5):
    """
    Search DuckDuckGo and return relevant results.

    Returns a list of dictionaries containing titles,
    URLs, and snippets.
    """

    results = []

    try:
        with DDGS() as search:
            search_results = search.text(
                keywords=topic,
                max_results=max_results
            )

            for item in search_results or []:
                results.append({
                    "title": item.get("title", "Untitled"),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", "")
                })

        logger.info(
            "Web search completed: topic=%r, results=%d",
            topic,
            len(results)
        )

    except Exception:
        logger.exception(
            "Web search failed for topic=%r",
            topic
        )

    return results


# --------------------------------------------------
# AI RESEARCH SUMMARY
# --------------------------------------------------

def generate_research_brief(topic, search_results):
    """
    Generate a concise three-point research brief
    using Groq and the retrieved web results.
    """

    client = get_groq_client()

    if client is None:
        raise RuntimeError(
            "Groq API key is missing. Add GROQ_API_KEY "
            "to your Render environment variables."
        )

    if not search_results:
        raise RuntimeError(
            "No web search results were found. "
            "Try another topic or retry later."
        )

    research_context = "\n\n".join(
        [
            (
                f"Source {index}:\n"
                f"Title: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['snippet']}"
            )
            for index, result in enumerate(
                search_results,
                start=1
            )
        ]
    )

    prompt = f"""
Research topic: {topic}

Use the following web search results to prepare a concise
research brief.

WEB SEARCH RESULTS:
{research_context}

INSTRUCTIONS:
1. Produce exactly three numbered points.
2. Each point should contain a useful, specific finding.
3. Base factual claims on the supplied search results.
4. Do not invent statistics, quotations, or citations.
5. Mention uncertainty if the available evidence is limited.
6. Keep the language clear and suitable for a college report.
7. Do not claim that you independently verified the sources.

Return only the three-point research brief.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful research assistant. "
                    "Summarize supplied search evidence accurately "
                    "and never invent supporting facts."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=700
    )

    summary = response.choices[0].message.content

    if not summary or not summary.strip():
        raise RuntimeError(
            "The AI model returned an empty response. "
            "Please try again."
        )

    return summary.strip()


# --------------------------------------------------
# MAIN RESEARCH WORKFLOW
# --------------------------------------------------

def research_topic(topic):
    """Search the web and generate the research brief."""

    start_time = time.perf_counter()

    logger.info(
        "Research request received: topic=%r",
        topic
    )

    try:
        results = search_web(topic)

        if not results:
            raise RuntimeError(
                "The web search returned no results. "
                "Check your internet/search access and retry."
            )

        summary = generate_research_brief(
            topic,
            results
        )

        elapsed = time.perf_counter() - start_time

        logger.info(
            "Research request completed: topic=%r, "
            "results=%d, elapsed_seconds=%.2f",
            topic,
            len(results),
            elapsed
        )

        return {
            "summary": summary,
            "sources": results,
            "elapsed": elapsed
        }

    except Exception:
        elapsed = time.perf_counter() - start_time

        logger.exception(
            "Research request failed: topic=%r, "
            "elapsed_seconds=%.2f",
            topic,
            elapsed
        )

        raise


# --------------------------------------------------
# STREAMLIT USER INTERFACE
# --------------------------------------------------

st.title("🔎 Task Automation Research Agent")

st.write(
    "Enter a topic to search the web and generate "
    "a concise three-point research brief."
)

st.caption(
    "MLOps Experiment 10 · Streamlit · DuckDuckGo · Groq"
)

st.divider()

with st.form("research_form"):

    topic = st.text_input(
        "Research topic",
        placeholder=(
            "e.g. Applications of Artificial Intelligence "
            "in Healthcare"
        ),
        max_chars=300
    )

    submitted = st.form_submit_button(
        "Research topic",
        type="primary",
        use_container_width=True
    )


if submitted:

    topic = topic.strip()

    if not topic:
        st.warning("Please enter a research topic.")

    elif not GROQ_API_KEY:
        st.error(
            "Groq API key is not configured. "
            "Add GROQ_API_KEY in your Render "
            "service's Environment settings."
        )

    else:
        with st.spinner(
            "Searching the web and preparing your research brief..."
        ):

            try:
                result = research_topic(topic)

                st.success("Research brief generated successfully!")

                st.subheader("Research Brief")

                st.markdown(result["summary"])

                st.caption(
                    f"Elapsed time: {result['elapsed']:.2f} seconds"
                )

                st.subheader("Sources")

                for index, source in enumerate(
                    result["sources"],
                    start=1
                ):
                    title = source["title"]
                    url = source["url"]
                    snippet = source["snippet"]

                    st.markdown(
                        f"**{index}. [{title}]({url})**"
                    )

                    if snippet:
                        st.write(snippet)

                    st.divider()

            except Exception:
                st.error(
                    "The research request failed. "
                    "Check the Render application logs "
                    "for details, then try again."
                )