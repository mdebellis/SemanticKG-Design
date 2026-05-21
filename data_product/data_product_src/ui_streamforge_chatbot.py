import os
import re
import html
import streamlit as st
import pyperclip
from string import Template
from franz.openrdf.query.query import QueryLanguage
from ag_api import *

# ------------------------------------------------------------
# StreamForge Data Catalog Graph RAG / ChatState UI
#
# Assumptions:
#   1. ag_api.py creates/binds `conn` to the main triplestore repository:
#          streamforge_data_catalog
#   2. AllegroGraph can see the vector repository by name:
#          streamforge_vdb
#   3. Your OpenAI key is in the standard environment variable:
#          OPENAI_API_KEY
#
# Run with, for example:
#   streamlit run C:\Users\mdebe\Documents\GitHub\SemanticKG-Design\data_product\data_product_src\ui_streamforge_chatbot.py
# ------------------------------------------------------------

st.set_page_config(layout="wide")

APP_TITLE = "StreamForge Data Catalog"
GRUFF_URL = "http://localhost:10035"
HELP_URL = "https://github.com/mdebellis/SemanticKG-Design"

# AllegroGraph repository names
VECTOR_REPO = "streamforge_vdb"
HISTORY_REPO = "streamforge_history"

# Defaults for the chatState call
DEFAULT_NUM_VECTOR_RESULTS = 4
DEFAULT_VECTOR_THRESHOLD = 0.75
DEFAULT_NUM_HISTORY_RESULTS = 4
DEFAULT_HISTORY_THRESHOLD = 0.0

PREFIXES = """\
PREFIX llm: <http://franz.com/ns/allegrograph/8.0.0/llm/>
PREFIX dp: <https://www.michaeldebellis.com/dp/>
PREFIX sf: <https://www.michaeldebellis.com/streamforge/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

CHATSTATE_QUERY_TEMPLATE = Template("""\
${openai_prefix}${prefixes}
SELECT ?response WHERE {
  ?response llm:chatState (
    ${question}
    ${vector_repo}
    ${num_vector_results}
    ${vector_threshold}
    ${history_repo}
    ${num_history_results}
    ${history_threshold}
  )
}
""")


def clean_question(text: str) -> str:
    """Normalize whitespace in user input."""
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()


def sparql_string_literal(text: str) -> str:
    """
    Return a SPARQL-safe string literal.

    json.dumps would also work, but this keeps the escaping rules explicit.
    """
    escaped = (
        text
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def franz_option_openai_key_prefix() -> str:
    """
    Build the AllegroGraph franzOption prefix for the OpenAI key.

    Preferred setup:
        Windows PowerShell:
            [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")

        Current session only:
            $env:OPENAI_API_KEY = "sk-..."

    If you still have the older keys.py file, this falls back to keys.oaik.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        try:
            from keys import oaik  # type: ignore
            api_key = str(oaik).strip()
        except Exception:
            api_key = ""

    if not api_key:
        return ""

    # Your old keys.py may already have stored the full <franz:...> value.
    if api_key.startswith("<franz:"):
        franz_value = api_key
    else:
        franz_value = f"<franz:{api_key}>"

    return f"PREFIX franzOption_openaiApiKey: {franz_value}\n"


def build_query(
    user_question: str,
    vector_repo: str,
    num_vector_results: int,
    vector_threshold: float,
    history_repo: str,
    num_history_results: int,
    history_threshold: float,
) -> str:
    """Build the SPARQL query sent to AllegroGraph."""
    question = clean_question(str(user_question))
    if not question:
        return ""

    return CHATSTATE_QUERY_TEMPLATE.substitute(
        openai_prefix=franz_option_openai_key_prefix(),
        prefixes=PREFIXES,
        question=sparql_string_literal(question),
        vector_repo=sparql_string_literal(vector_repo),
        num_vector_results=int(num_vector_results),
        vector_threshold=float(vector_threshold),
        history_repo=sparql_string_literal(history_repo),
        num_history_results=int(num_history_results),
        history_threshold=float(history_threshold),
    )


def remove_citation_ids(text: str) -> str:
    """Remove citation-id boilerplate sometimes emitted in LLM responses."""
    return re.sub(r"\(citation-id:<.*?>\)", "", text).strip()


def do_query(query_string: str) -> str:
    """Run the SPARQL query and return a Markdown response."""
    if not query_string:
        return ""

    pyperclip.copy(query_string)

    tuple_query = conn.prepareTupleQuery(QueryLanguage.SPARQL, query_string)
    result = tuple_query.evaluate()

    responses = []
    with result:
        for i, binding_set in enumerate(result, start=1):
            response_value = binding_set.getValue("response")
            response = "" if response_value is None else str(response_value)
            response = remove_citation_ids(response)
            responses.append(f"**Result {i}:**\n\n{response}")

    if not responses:
        return "No response was returned."

    return "\n\n---\n\n".join(responses)


def init_state() -> None:
    defaults = {
        "last_query": "",
        "answer": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

st.title(APP_TITLE)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ask the Data Catalog")

    vector_repo = st.text_input("Vector repository", value=VECTOR_REPO)
    history_repo = st.text_input("History repository", value=HISTORY_REPO)

    num_vector_results = st.number_input(
        "Number of Vector Results",
        min_value=1,
        max_value=20,
        value=DEFAULT_NUM_VECTOR_RESULTS,
        step=1,
    )

    vector_threshold = st.number_input(
        "Vector Relevance Threshold",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_VECTOR_THRESHOLD,
        step=0.05,
    )

    num_history_results = st.number_input(
        "Number of History Results",
        min_value=0,
        max_value=20,
        value=DEFAULT_NUM_HISTORY_RESULTS,
        step=1,
    )

    history_threshold = st.number_input(
        "History Threshold",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_HISTORY_THRESHOLD,
        step=0.05,
    )

    question = st.text_area(
        "Enter question here:",
        value="",
        placeholder="Type question here. Press Ctrl-Enter when done.",
        height=100,
    )

    if st.button("Ask"):
        query_string = build_query(
            question,
            vector_repo,
            num_vector_results,
            vector_threshold,
            history_repo,
            num_history_results,
            history_threshold,
        )
        st.session_state.last_query = query_string
        st.session_state.answer = do_query(query_string)

    st.text_area(
        "Answer:",
        value=st.session_state.answer,
        height=300,
        placeholder="Answer will be displayed here.",
    )

with col2:
    st.subheader("SPARQL Sent to AllegroGraph")

    st.text_area(
        "Copied to clipboard after each query:",
        value=st.session_state.last_query,
        height=520,
        placeholder="The generated SPARQL query will appear here and will also be copied to the clipboard.",
    )

    if st.button("Copy SPARQL Again"):
        if st.session_state.last_query:
            pyperclip.copy(st.session_state.last_query)

st.page_link(GRUFF_URL, label="Open Gruff", icon=None)
st.page_link(HELP_URL, label="Project Repository", icon=None)
