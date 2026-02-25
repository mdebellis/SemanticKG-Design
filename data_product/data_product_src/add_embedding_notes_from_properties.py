from __future__ import annotations

from typing import Iterable, List, Optional, Tuple, Dict, Set

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDFS


def add_embedding_notes_from_properties(
    g: Graph,
    property_qnames: List[str],
    *,
    dp_embedding_note_qname: str = "dp:embedding_note",
    test: bool = True,
    predicate_label_fallback_to_qname: bool = True,
    end_with_period: bool = True,
    verbose: bool = True,
) -> int:
    """
    Generate embedding-friendly natural-language notes for triples that use specific predicates.

    For each predicate in property_qnames, find triples (?s predicate ?o),
    read rdfs:label@en for s and o (assumed present), and build:

        "<sLabel> <predLabelOrQName> <oLabel>."

    If test=True: print (sLabel, predicate qname string, note).
    If test=False: add (?s dp:embedding_note "note"@en) unless an identical note already exists.

    Returns: number of notes inserted (0 if test=True).
    """

    # --- Helper: expand a QName like "dp:has_bounded_context" to a URIRef ---
    def expand_qname(qname: str) -> URIRef:
        if ":" not in qname:
            raise ValueError(f"Expected QName with prefix, got: {qname!r}")
        prefix, local = qname.split(":", 1)
        ns = g.namespace_manager.store.namespace(prefix)
        if ns is None:
            # rdflib sometimes keeps namespaces only in namespace_manager (not in store) depending on setup
            # try namespace_manager directly
            ns2 = dict(g.namespace_manager.namespaces()).get(prefix)
            if ns2 is None:
                raise ValueError(
                    f"Prefix {prefix!r} not bound in graph namespace_manager. "
                    f"Bind it first, e.g. g.bind('{prefix}', Namespace('...'))."
                )
            ns = ns2
        return URIRef(str(ns) + local)

    # --- Helper: prefer rdfs:label@en; otherwise any rdfs:label; else None ---
    def get_label_en(node: URIRef) -> Optional[str]:
        # Prefer @en
        for lbl in g.objects(node, RDFS.label):
            if isinstance(lbl, Literal) and (lbl.language == "en"):
                return str(lbl)
        # Fallback: any label literal
        for lbl in g.objects(node, RDFS.label):
            if isinstance(lbl, Literal):
                return str(lbl)
        return None

    # --- Helper: get "best" predicate display label ---
    def predicate_display(pred_uri: URIRef, pred_qname: str) -> str:
        # 1) Prefer dp:embedding_label@en if present on the predicate
        for lbl in g.objects(pred_uri, embedding_label_pred):
            if isinstance(lbl, Literal) and lbl.language == "en":
                return str(lbl)
        # fallback: any dp:embedding_label literal
        for lbl in g.objects(pred_uri, embedding_label_pred):
            if isinstance(lbl, Literal):
                return str(lbl)

        # 2) Otherwise, use rdfs:label (your existing behavior)
        pred_lbl = get_label_en(pred_uri)
        if pred_lbl:
            return pred_lbl

        # 3) Fallback to QName or full URI
        return pred_qname if predicate_label_fallback_to_qname else str(pred_uri)

    # Expand dp:embedding_note
    embedding_note_pred = expand_qname(dp_embedding_note_qname)
    embedding_label_pred = expand_qname("dp:embedding_label")

    # Preload existing embedding notes per subject (lexical form only) for dedup
    existing_notes: Dict[URIRef, Set[str]] = {}
    for s, _, note in g.triples((None, embedding_note_pred, None)):
        if isinstance(note, Literal):
            existing_notes.setdefault(s, set()).add(str(note))
        else:
            existing_notes.setdefault(s, set()).add(str(note))

    inserted = 0

    for pred_qname in property_qnames:
        pred_uri = expand_qname(pred_qname)
        pred_disp = predicate_display(pred_uri, pred_qname)

        # Iterate matching triples
        for s, _, o in g.triples((None, pred_uri, None)):
            # You said assume rdfs:label@en is always set for s and o:
            s_label = get_label_en(s)
            o_label = get_label_en(o) if isinstance(o, URIRef) else (str(o) if isinstance(o, Literal) else None)

            if s_label is None or o_label is None:
                # Since you said these are always present, treat missing as an error
                raise ValueError(
                    f"Missing rdfs:label@en (or any rdfs:label) for "
                    f"{'subject' if s_label is None else 'object'} in triple: "
                    f"({s}, {pred_uri}, {o})"
                )

            note_text = f"{s_label} {pred_disp} {o_label}"
            if end_with_period and not note_text.endswith("."):
                note_text += "."

            if test:
                print(note_text)
                continue

            # Dedup: don't insert if identical note already exists on that subject
            already = note_text in existing_notes.get(s, set())
            if already:
                if verbose:
                    # comment out if you want quieter runs
                    pass
                continue

            g.add((s, embedding_note_pred, Literal(note_text, lang="en")))
            existing_notes.setdefault(s, set()).add(note_text)
            inserted += 1
    return inserted

# How to run the program:
# Step 1: Create a text file listing QNames  of predicates to use: such as embedding_properties.txt
# Example contents. One per line. No commas. No quotes:
# dp:has_bounded_context
# prov:generated
# dp:has_platform_port
# Step2: From your repo directory at the terminal:
# 2.1: Test mode (safe — prints only) This is the default to make sure things are working. It is currently the default
# because the function doesn't do a lot of error checking so best to make sure all your properties can be found, etc.
# python add_embedding_notes_from_properties.py streamforge.ttl embedding_properties.txt
#
# 2.2: Insert mode
# python add_embedding_notes_from_properties.py streamforge.ttl embedding_properties.txt --insert
#
# That will write a new ontology file: output_with_embedding_notes.ttl You can change that filename later if needed.

if __name__ == "__main__":
    import sys
    from rdflib import Graph, Namespace

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python add_embedding_notes_from_properties.py <input.ttl> <properties.txt> [--insert]")
        sys.exit(1)

    input_file = sys.argv[1]
    properties_file = sys.argv[2]
    insert_mode = "--insert" in sys.argv

    # Load graph
    g = Graph()
    g.parse(input_file, format="turtle")

    # Bind prefixes (adjust if needed)
    g.bind("dp", Namespace("https://www.michaeldebellis.com/dp/"))
    g.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
    g.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))

    # Read predicate list
    with open(properties_file, "r", encoding="utf-8") as f:
        props = [line.strip() for line in f if line.strip()]

    print("Properties loaded:", props)

    if insert_mode:
        print("Running in INSERT mode...")
        n = add_embedding_notes_from_properties(g, props, test=False)
        print(f"Inserted {n} embedding notes.")
        g.serialize("output_with_embedding_notes.ttl", format="turtle")
    else:
        print("Running in TEST mode...")
        add_embedding_notes_from_properties(g, props, test=True)