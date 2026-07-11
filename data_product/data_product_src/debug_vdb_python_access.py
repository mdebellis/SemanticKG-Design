r"""
Diagnostic script for StreamForge / AllegroGraph VDB metadata visibility.

Run from the same environment and project directory you use for Streamlit, e.g.:

    cd C:\Users\mdebe\Documents\GitHub\SemanticKG-Design\data_product\data_product_src
    python C:\Users\mdebe\Downloads\debug_vdb_python_access.py

Or copy this file into data_product_src and run:

    python debug_vdb_python_access.py

It assumes ag_api.py creates/binds `conn` to the streamforge_data_catalog repository.
"""

from __future__ import annotations

from typing import Any, Iterable

from franz.openrdf.query.query import QueryLanguage
from ag_api import conn  # type: ignore

VDB_219 = "http://franz.com/vdb/id/219"
VDB_326 = "http://franz.com/vdb/id/326"
VDB_PROP_ID = "http://franz.com/vdb/prop/id"
VDB_PROP_PRED = "http://franz.com/vdb/prop/pred"
VDB_GEN_TEXT = "http://franz.com/vdb/gen/text"


def value_debug(v: Any) -> str:
    """Return a detailed string describing an AllegroGraph binding value."""
    if v is None:
        return "None"

    parts = [f"str={str(v)!r}", f"repr={repr(v)}", f"class={v.__class__.__module__}.{v.__class__.__name__}"]

    for method_name in ["getURI", "getNamespace", "getLocalName", "getLabel", "toPython", "ntriplesString"]:
        method = getattr(v, method_name, None)
        if callable(method):
            try:
                parts.append(f"{method_name}={method()!r}")
            except Exception as exc:
                parts.append(f"{method_name}=ERROR({exc!r})")

    return " | ".join(parts)


def run_query(title: str, query: str, binding_names: Iterable[str]) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    print(query.strip())
    print("-" * 100)

    try:
        tuple_query = conn.prepareTupleQuery(QueryLanguage.SPARQL, query)
        result = tuple_query.evaluate()
        count = 0
        with result:
            for count, binding_set in enumerate(result, start=1):
                print(f"\nROW {count}")
                for name in binding_names:
                    try:
                        value = binding_set.getValue(name)
                    except Exception as exc:
                        print(f"  {name}: ERROR getting value: {exc!r}")
                        continue
                    print(f"  {name}: {value_debug(value)}")
        if count == 0:
            print("NO ROWS")
    except Exception as exc:
        print(f"QUERY ERROR: {exc!r}")


def run_get_statements(title: str, subject_iri: str, predicate_iri: str | None = None) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    try:
        subject = conn.createURI(subject_iri)
        predicate = conn.createURI(predicate_iri) if predicate_iri else None
        statements = conn.getStatements(subject, predicate, None)
        count = 0
        with statements:
            for count, st in enumerate(statements, start=1):
                print(f"\nSTMT {count}")
                print(f"  subject:   {value_debug(st.getSubject())}")
                print(f"  predicate: {value_debug(st.getPredicate())}")
                print(f"  object:    {value_debug(st.getObject())}")
        if count == 0:
            print("NO STATEMENTS")
    except Exception as exc:
        print(f"GET STATEMENTS ERROR: {exc!r}")


def main() -> None:
    run_query(
        "A. Explicit outgoing triples for vdbid:219 using absolute IRI",
        f"""
        SELECT ?p ?o
        WHERE {{
          <{VDB_219}> ?p ?o .
        }}
        ORDER BY ?p ?o
        """,
        ["p", "o"],
    )

    run_query(
        "B. Explicit outgoing triples for vdbid:326 using absolute IRI",
        f"""
        SELECT ?p ?o
        WHERE {{
          <{VDB_326}> ?p ?o .
        }}
        ORDER BY ?p ?o
        """,
        ["p", "o"],
    )

    run_query(
        "C. Direct vdbprop:id dereference for 219 and 326",
        f"""
        SELECT ?vdbId ?domainObject ?domainObjectString
        WHERE {{
          VALUES ?vdbId {{ <{VDB_219}> <{VDB_326}> }}
          ?vdbId <{VDB_PROP_ID}> ?domainObject .
          BIND(STR(?domainObject) AS ?domainObjectString)
        }}
        ORDER BY ?vdbId
        """,
        ["vdbId", "domainObject", "domainObjectString"],
    )

    run_query(
        "D. All VDB metadata with STR property filters",
        f"""
        SELECT ?vdbId ?p ?o
        WHERE {{
          VALUES ?vdbId {{ <{VDB_219}> <{VDB_326}> }}
          ?vdbId ?p ?o .
          FILTER(
            STR(?p) = "{VDB_PROP_ID}" ||
            STR(?p) = "{VDB_PROP_PRED}" ||
            STR(?p) = "{VDB_GEN_TEXT}"
          )
        }}
        ORDER BY ?vdbId ?p ?o
        """,
        ["vdbId", "p", "o"],
    )

    run_get_statements("E. getStatements for all outgoing triples from vdbid:219", VDB_219)
    run_get_statements("F. getStatements for vdbid:219 vdbprop:id ?o", VDB_219, VDB_PROP_ID)
    run_get_statements("G. getStatements for all outgoing triples from vdbid:326", VDB_326)
    run_get_statements("H. getStatements for vdbid:326 vdbprop:id ?o", VDB_326, VDB_PROP_ID)


if __name__ == "__main__":
    main()
