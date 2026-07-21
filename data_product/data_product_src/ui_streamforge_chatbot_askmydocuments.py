import os
import re
from string import Template
from typing import Any, Dict, List, Tuple

import pyperclip
import streamlit as st
from franz.openrdf.query.query import QueryLanguage
from ag_api import *

# ------------------------------------------------------------
# StreamForge Data Catalog Graph RAG / askMyDocuments UI
#
# Assumptions:
#   1. ag_api.py creates/binds `conn` to the main triplestore repository:
#          streamforge_data_catalog
#   2. The vector database is now in the same repository:
#          streamforge_data_catalog
#      If your local AG setup uses the current repository's embedded vector store
#      shorthand instead, change the Vector repository field in the UI to: *
#   3. The only text predicates embedded as vectors are:
#          docs:chunk_text
#          dp:embedding_note
#   4. Your OpenAI key is in OPENAI_API_KEY, in keys.py as oaik, or saved as an
#      AllegroGraph query option for the repository.
#
# Run with, for example:
#   streamlit run C:\Users\mdebe\Documents\GitHub\SemanticKG-Design\data_product\data_product_src\ui_streamforge_chatbot_askmydocuments.py
# ------------------------------------------------------------

st.set_page_config(layout="wide")

APP_TITLE = "StreamForge Data Catalog"
GRUFF_URL = "http://localhost:10035"
HELP_URL = "https://github.com/mdebellis/SemanticKG-Design"

# The new StreamForge setup keeps vectors in streamforge_data_catalog.
VECTOR_REPO = "streamforge_data_catalog"

DEFAULT_NUM_VECTOR_RESULTS = 4
DEFAULT_VECTOR_THRESHOLD = 0.75
MAX_GRUFF_DOMAIN_OBJECTS = 10
STREAMFORGE_ASSISTANT_INSTRUCTIONS = """\
You are a helpful member of the StreamForge Data Catalog team.

Answer as if you are helping an internal StreamForge user understand the data catalog.
Use a practical, catalog-team voice rather than a generic RAG assistant voice.

Use only the retrieved catalog evidence when making factual claims about StreamForge.
If the retrieved evidence is incomplete, say what you can infer and what would need to be checked.
Mention relevant data products, annotations, policies, skills, teams, datasets, or interfaces when they appear in the retrieved evidence.
Keep the answer concise but useful.
"""

PREFIXES = """\
PREFIX llm: <http://franz.com/ns/allegrograph/8.0.0/llm/>
PREFIX vdb: <http://franz.com/vdb/gen/>
PREFIX vdbprop: <http://franz.com/vdb/prop/>
PREFIX dp: <https://www.michaeldebellis.com/dp/>
PREFIX docs: <https://www.michaeldebellis.com/docs/>
PREFIX sf: <https://www.michaeldebellis.com/streamforge/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

ASK_MY_DOCUMENTS_QUERY_TEMPLATE = Template("""\
${openai_prefix}${prefixes}
SELECT DISTINCT
  ?response
  ?score
  ?vdbId
  ?domainObject
  ?domainLabel
  ?domainType
  ?matchedPredicate
  ?citedText
  ?displayEmbeddedText
WHERE {
  BIND(${question} AS ?query)

  # RAG answer plus the vector citation rows that supported it.
  (?response ?score ?vdbId ?citedText)
    llm:askMyDocuments (?query ${vector_repo} ${num_vector_results} ${vector_threshold}) .

  # Trace the vector citation directly back to the RDF subject that was embedded.
  # Keep this mandatory so we do not accidentally range over unrelated VDB objects.
  ?vdbId vdbprop:id ?domainObject .

  # Vector metadata. The embedded text is stored at vdb:text,
  # i.e., http://franz.com/vdb/gen/text.
  OPTIONAL { ?vdbId vdbprop:pred ?matchedPredicate . }
  OPTIONAL { ?vdbId vdb:text ?embeddedText . }

  BIND(COALESCE(?embeddedText, ?citedText) AS ?displayEmbeddedText)

  # Useful labels and types for the trace table.
  OPTIONAL {
    ?domainObject (rdfs:label|skos:prefLabel|dcterms:title) ?domainLabel .
  }
  OPTIONAL {
    ?domainObject rdf:type ?domainType .
    FILTER(?domainType NOT IN (owl:NamedIndividual, vdb:Object))
  }
}
ORDER BY DESC(?score) ?domainLabel ?domainObject
""")


def clean_question(text: str) -> str:
    """Normalize whitespace in user input."""
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

def build_streamforge_prompt(user_question: str) -> str:
    """Wrap the user's question with StreamForge assistant instructions."""
    question = clean_question(user_question)

    return f"""\
{STREAMFORGE_ASSISTANT_INSTRUCTIONS}

User question:
{question}
"""

def sparql_string_literal(text: str) -> str:
    """Return a SPARQL-safe string literal."""
    escaped = (
        text
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'

REDACTED_OPENAI_PREFIX = """\
# OpenAI API key removed for security.
# To run this query manually, replace the masked value below with your actual key,
# or delete this PREFIX if your AllegroGraph repository already has the key configured.
PREFIX franzOption_openaiApiKey: <franz:REPLACE_WITH_OPENAI_API_KEY>
"""

def redact_openai_key(query_string: str) -> str:
    """Return a display-safe version of a SPARQL query with the OpenAI key removed."""
    pattern = r"(?m)^PREFIX\s+franzOption_openaiApiKey:\s+<franz:[^>\r\n]+>\s*$"
    return re.sub(pattern, REDACTED_OPENAI_PREFIX.rstrip(), query_string)

def franz_option_openai_key_prefix() -> str:
    """
    Build the AllegroGraph franzOption prefix for the OpenAI key.

    Preferred setup:
        Windows PowerShell:
            [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")

        Current session only:
            $env:OPENAI_API_KEY = "sk-..."

    If you still have the older keys.py file, this falls back to keys.oaik.
    If neither exists, the query can still work when the API key is saved as an
    AllegroGraph repository query option.
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
    franz_value = api_key if api_key.startswith("<franz:") else f"<franz:{api_key}>"
    return f"PREFIX franzOption_openaiApiKey: {franz_value}\n"


def build_query(
    user_question: str,
    vector_repo: str,
    num_vector_results: int,
    vector_threshold: float,
) -> str:
    """Build the SPARQL query sent to AllegroGraph."""
    question = clean_question(str(user_question))
    if not question:
        return ""

    prompt = build_streamforge_prompt(question)

    return ASK_MY_DOCUMENTS_QUERY_TEMPLATE.substitute(
        openai_prefix=franz_option_openai_key_prefix(),
        prefixes=PREFIXES,
        question=sparql_string_literal(prompt),
        vector_repo=sparql_string_literal(vector_repo),
        num_vector_results=int(num_vector_results),
        vector_threshold=float(vector_threshold),
    )


def remove_citation_ids(text: str) -> str:
    """Remove citation-id boilerplate sometimes emitted in LLM responses."""
    return re.sub(r"\(citation-id:<.*?>\)", "", text).strip()


def binding_to_string(value: Any) -> str:
    """Convert an AllegroGraph binding value to a clean display string."""
    if value is None:
        return ""

    # AllegroGraph literals often expose either toPython() or getLabel().
    # Prefer those over str(value), because str(value) includes datatype syntax
    # such as "5.538972E-1"^^<http://www.w3.org/2001/XMLSchema#float>.
    for attr in ("toPython", "getLabel"):
        method = getattr(value, attr, None)
        if callable(method):
            try:
                converted = method()
                if converted is not None:
                    return str(converted)
            except Exception:
                pass

    text = str(value)

    # Strip common typed-literal display syntax.
    typed_literal_match = re.match(r'^"(.*)"\^\^<[^>]+>$', text, flags=re.DOTALL)
    if typed_literal_match:
        return typed_literal_match.group(1)

    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text


def local_name(uri_or_literal: str) -> str:
    """Return a compact local name for URI-looking values, otherwise the original text."""
    text = str(uri_or_literal or "")
    if not text:
        return ""
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1]
    for separator in ("#", "/"):
        if separator in text:
            text = text.rstrip("/").split(separator)[-1]
    return text


def sparql_iri(value: str) -> str:
    """Return a full IRI in SPARQL syntax, or an empty string if it is not an IRI."""
    text = str(value or "").strip()
    if not text:
        return ""

    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1].strip()

    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", text):
        return ""

    # The values originate in AllegroGraph query bindings. Reject characters
    # that cannot safely appear here rather than generating malformed SPARQL.
    if any(character in text for character in '<>"{}|^`\\'):
        return ""

    return f"<{text}>"


def build_gruff_exploration_query(trace_rows: List[Dict[str, str]]) -> str:
    """Build a deterministic CONSTRUCT query for the selected domain objects."""
    domain_objects: List[str] = []
    seen_objects = set()

    for row in trace_rows:
        vdb_id = sparql_iri(row.get("Vector ID", ""))
        domain_object = sparql_iri(row.get("Domain Object", ""))

        # Safety check: do not expose vector objects in the user-facing Gruff graph.
        if not domain_object or domain_object == vdb_id:
            continue

        if domain_object not in seen_objects:
            domain_objects.append(domain_object)
            seen_objects.add(domain_object)

        if len(domain_objects) >= MAX_GRUFF_DOMAIN_OBJECTS:
            break

    if not domain_objects:
        return ""

    values_block = "\n".join(f"    {domain_object}" for domain_object in domain_objects)

    return f"""\
PREFIX dp: <https://www.michaeldebellis.com/dp/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

# This query makes no OpenAI call. The vector search has already selected the
# domain objects; only those objects and a small deterministic neighborhood are
# returned to Gruff.
CONSTRUCT {{
  # Labels and types of the selected domain objects.
  ?selectedObject ?selectedLabelPredicate ?selectedLabel .
  ?selectedObject rdf:type ?selectedType .

  # Any direct RDF relationship between two objects selected by the vector search.
  # This preserves relationships such as is_downstream_of or applies_to_activity.
  ?selectedObject ?connectingPredicate ?connectedSelectedObject .

  # One-hop downstream neighborhood.
  ?selectedObject dp:is_downstream_of ?downstreamObject .
  ?downstreamObject ?downstreamLabelPredicate ?downstreamLabel .
  ?downstreamObject rdf:type ?downstreamType .

  # One-hop upstream neighborhood.
  ?upstreamObject dp:is_downstream_of ?selectedObject .
  ?upstreamObject ?upstreamLabelPredicate ?upstreamLabel .
  ?upstreamObject rdf:type ?upstreamType .
}}
WHERE {{
  VALUES ?selectedObject {{
{values_block}
  }}

  OPTIONAL {{
    VALUES ?selectedLabelPredicate {{ rdfs:label skos:prefLabel dcterms:title }}
    ?selectedObject ?selectedLabelPredicate ?selectedLabel .
  }}

  OPTIONAL {{
    ?selectedObject rdf:type ?selectedType .
    FILTER(?selectedType NOT IN (owl:NamedIndividual))
  }}

  # Explicitly include links among the objects returned by the vector search.
  # A CONSTRUCT query guarantees that Gruff receives these relationship triples.
  OPTIONAL {{
    VALUES ?connectedSelectedObject {{
{values_block}
    }}
    ?selectedObject ?connectingPredicate ?connectedSelectedObject .
    FILTER(?connectingPredicate NOT IN (
      rdf:type,
      rdfs:label,
      skos:prefLabel,
      dcterms:title
    ))
  }}

  OPTIONAL {{
    ?selectedObject dp:is_downstream_of ?downstreamObject .

    OPTIONAL {{
      VALUES ?downstreamLabelPredicate {{ rdfs:label skos:prefLabel dcterms:title }}
      ?downstreamObject ?downstreamLabelPredicate ?downstreamLabel .
    }}

    OPTIONAL {{
      ?downstreamObject rdf:type ?downstreamType .
      FILTER(?downstreamType NOT IN (owl:NamedIndividual))
    }}
  }}

  OPTIONAL {{
    ?upstreamObject dp:is_downstream_of ?selectedObject .

    OPTIONAL {{
      VALUES ?upstreamLabelPredicate {{ rdfs:label skos:prefLabel dcterms:title }}
      ?upstreamObject ?upstreamLabelPredicate ?upstreamLabel .
    }}

    OPTIONAL {{
      ?upstreamObject rdf:type ?upstreamType .
      FILTER(?upstreamType NOT IN (owl:NamedIndividual))
    }}
  }}
}}
"""


def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard when pyperclip is available."""
    try:
        pyperclip.copy(text)
    except Exception:
        # Some environments do not expose a system clipboard. The query is still
        # displayed in the UI for manual copying.
        pass

def do_query(query_string: str, clipboard_text: str = "") -> Tuple[str, List[Dict[str, str]]]:
    """Run the SPARQL query and return the answer plus trace rows."""
    if not query_string:
        return "", []

    copy_to_clipboard(clipboard_text or redact_openai_key(query_string))

    tuple_query = conn.prepareTupleQuery(QueryLanguage.SPARQL, query_string)
    result = tuple_query.evaluate()

    answers: List[str] = []
    trace_rows: List[Dict[str, str]] = []
    seen_answers = set()
    seen_trace_rows = set()

    with result:
        for binding_set in result:
            response = remove_citation_ids(binding_to_string(binding_set.getValue("response")))
            if response and response not in seen_answers:
                answers.append(response)
                seen_answers.add(response)

            row = {
                "Score": binding_to_string(binding_set.getValue("score")),
                "Vector ID": binding_to_string(binding_set.getValue("vdbId")),
                "Domain Object": binding_to_string(binding_set.getValue("domainObject")),
                "Object Label": binding_to_string(binding_set.getValue("domainLabel")),
                "Object Type": local_name(binding_to_string(binding_set.getValue("domainType"))),
                "Vector Predicate": local_name(binding_to_string(binding_set.getValue("matchedPredicate"))),
                "Cited Text": binding_to_string(binding_set.getValue("citedText")),
                "Embedded Text": binding_to_string(binding_set.getValue("displayEmbeddedText")),
            }
            row_key = tuple(row.items())
            if row_key not in seen_trace_rows:
                trace_rows.append(row)
                seen_trace_rows.add(row_key)

    if not answers:
        return "No response was returned.", trace_rows

    return "\n\n---\n\n".join(answers), trace_rows


def init_state() -> None:
    defaults = {
        "last_query": "",
        "gruff_query": "",
        "answer": "",
        "trace_rows": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

st.title(APP_TITLE)
st.caption("Graph RAG with one-time LLM retrieval plus deterministic Gruff exploration")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ask the Data Catalog")

    vector_repo = st.text_input(
        "Vector repository",
        value=VECTOR_REPO,
        help="Use streamforge_data_catalog for the new combined graph/vector setup. Use * only if your AG vector store is embedded in the currently selected repository and configured that way.",
    )

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
        )
        safe_query_string = redact_openai_key(query_string)

        st.session_state.last_query = safe_query_string
        st.session_state.gruff_query = ""
        answer, trace_rows = do_query(query_string, clipboard_text=safe_query_string)
        st.session_state.answer = answer
        st.session_state.trace_rows = trace_rows

    st.subheader("Answer")
    if st.session_state.answer:
        st.markdown(st.session_state.answer)
    else:
        st.info("Answer will be displayed here.")

    st.subheader("Citation Trace")
    if st.session_state.trace_rows:
        st.dataframe(
            st.session_state.trace_rows,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Citation rows will appear here after a query.")

with col2:
    st.subheader("SPARQL Sent to AllegroGraph")
    st.caption("The OpenAI key is used only for execution. The displayed query redacts the key for safe copy/paste.")

    st.text_area(
        label="The redacted LLM/vector query is copied to the clipboard after each Ask:",
        value=st.session_state.last_query,
        height=330,
        placeholder="The generated llm:askMyDocuments query will appear here.",
    )

    if st.button("Copy LLM SPARQL Again"):
        if st.session_state.last_query:
            copy_to_clipboard(st.session_state.last_query)

    st.subheader("Gruff Graph Query")
    st.caption("Generated from the resolved domain objects; vector nodes are omitted and no second OpenAI call is made.")

    if st.button(
        "Generate and Copy Gruff Graph Query",
        disabled=not bool(st.session_state.trace_rows),
    ):
        gruff_query = build_gruff_exploration_query(st.session_state.trace_rows)
        st.session_state.gruff_query = gruff_query
        if gruff_query:
            copy_to_clipboard(gruff_query)

    st.text_area(
        "Paste this deterministic CONSTRUCT query into Gruff:",
        value=st.session_state.gruff_query,
        height=390,
        placeholder="Ask a question, then select Generate and Copy Gruff Query.",
    )

    if st.button("Copy Gruff Query Again"):
        if st.session_state.gruff_query:
            copy_to_clipboard(st.session_state.gruff_query)

st.page_link(GRUFF_URL, label="Open Gruff", icon=None)
st.page_link(HELP_URL, label="Project Repository", icon=None)
