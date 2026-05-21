from __future__ import annotations

from typing import List, Optional, Dict

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
    read rdfs:label@en for s and o when appropriate, and build:

        "<sLabel> <predLabelOrQName> <oLabel>."

    Unlike the earlier version, this function consolidates embedding notes by subject.
    For each subject, it combines:
      - existing dp:embedding_note values already in the graph
      - newly generated note lines from the selected predicates

    It then writes back a single multiline dp:embedding_note literal per updated subject.

    If test=True: print the consolidated note value that would be written for each subject.
    If test=False: replace that subject's existing dp:embedding_note triples with one
    consolidated dp:embedding_note literal.

    Returns: number of subjects whose consolidated note was written (0 if test=True).
    """

    # --- Helper: expand a QName like "dp:has_bounded_context" to a URIRef ---
    def expand_qname(qname: str) -> URIRef:
        if ":" not in qname:
            raise ValueError(f"Expected QName with prefix, got: {qname!r}")
        prefix, local = qname.split(":", 1)
        ns = g.namespace_manager.store.namespace(prefix)
        if ns is None:
            # rdflib sometimes keeps namespaces only in namespace_manager (not in store)
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
            if isinstance(lbl, Literal) and lbl.language == "en":
                return str(lbl)
        # Fallback: any label literal
        for lbl in g.objects(node, RDFS.label):
            if isinstance(lbl, Literal):
                return str(lbl)
        return None

    # Expand dp:embedding_note and dp:embedding_label
    embedding_note_pred = expand_qname(dp_embedding_note_qname)
    embedding_label_pred = expand_qname("dp:embedding_label")

    # --- Helper: get "best" predicate display label ---
    def predicate_display(pred_uri: URIRef, pred_qname: str) -> str:
        # 1) Prefer dp:embedding_label@en if present on the predicate
        for lbl in g.objects(pred_uri, embedding_label_pred):
            if isinstance(lbl, Literal) and lbl.language == "en":
                return str(lbl)
        # Fallback: any dp:embedding_label literal
        for lbl in g.objects(pred_uri, embedding_label_pred):
            if isinstance(lbl, Literal):
                return str(lbl)

        # 2) Otherwise, use rdfs:label
        pred_lbl = get_label_en(pred_uri)
        if pred_lbl:
            return pred_lbl

        # 3) Fallback to QName or full URI
        return pred_qname if predicate_label_fallback_to_qname else str(pred_uri)

    # --- Helper: readable subject display for test output ---
    def subject_display(subject: URIRef) -> str:
        subject_label = get_label_en(subject)
        try:
            subject_qname = g.namespace_manager.normalizeUri(subject)
        except Exception:
            subject_qname = str(subject)

        if subject_label:
            return f"{subject_label} ({subject_qname})"
        return subject_qname

    # --- Helper: split existing note literals into individual lines for dedup ---
    def normalize_existing_note_literal(note: Literal) -> List[str]:
        return [
            line.strip()
            for line in str(note).splitlines()
            if line.strip()
        ]

    # --- Helper: preserve order while removing duplicate note lines ---
    def unique_preserving_order(items: List[str]) -> List[str]:
        seen = set()
        result: List[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    # Queue newly generated notes by subject, then consolidate at the end.
    pending_notes: Dict[URIRef, List[str]] = {}

    def queue_note(subject: URIRef, note_text: str) -> None:
        if end_with_period and not note_text.endswith("."):
            note_text += "."
        pending_notes.setdefault(subject, []).append(note_text)

    for pred_qname in property_qnames:
        pred_uri = expand_qname(pred_qname)
        pred_disp = predicate_display(pred_uri, pred_qname)

        # Iterate matching triples
        for s, _, o in g.triples((None, pred_uri, None)):
            s_label = get_label_en(s)

            if isinstance(o, URIRef):
                o_label = get_label_en(o)
                if o_label is None:
                    o_label = str(o)  # fallback to the IRI itself
            elif isinstance(o, Literal):
                o_label = str(o)
            else:
                o_label = None

            if s_label is None or o_label is None:
                # Treat missing subject label as an error. For URIRef objects, the code falls
                # back to the IRI itself when no label exists, preserving the previous behavior.
                raise ValueError(
                    f"Missing rdfs:label@en (or any rdfs:label) for "
                    f"{'subject' if s_label is None else 'object'} in triple: "
                    f"({s}, {pred_uri}, {o})"
                )

            note_text = f"{s_label} {pred_disp} {o_label}"
            queue_note(s, note_text)

    def consolidated_lines_for(subject: URIRef) -> List[str]:
        existing_lines: List[str] = []

        for existing in g.objects(subject, embedding_note_pred):
            if isinstance(existing, Literal):
                existing_lines.extend(normalize_existing_note_literal(existing))
            else:
                existing_lines.append(str(existing).strip())

        return unique_preserving_order(existing_lines + pending_notes.get(subject, []))

    if test:
        for subject in sorted(pending_notes.keys(), key=lambda s: subject_display(s).lower()):
            generated_lines = unique_preserving_order(pending_notes[subject])
            consolidated_lines = consolidated_lines_for(subject)
            print(f"\nSubject: {subject_display(subject)}")
            print("-" * 72)
            print("Generated note lines:")
            for line in generated_lines:
                print(f"  - {line}")
            print("Consolidated dp:embedding_note value:")
            print('"""')
            print("\n".join(consolidated_lines))
            print('"""')
        return 0

    updated_subjects = 0

    for subject in pending_notes.keys():
        consolidated_lines = consolidated_lines_for(subject)
        consolidated_text = "\n".join(consolidated_lines)

        existing_literals = list(g.objects(subject, embedding_note_pred))
        existing_texts = [str(lit) for lit in existing_literals]

        # If the subject already has exactly one literal with exactly this consolidated text,
        # no update is needed.
        if existing_texts == [consolidated_text]:
            if verbose:
                pass
            continue

        for lit in existing_literals:
            g.remove((subject, embedding_note_pred, lit))

        g.add((subject, embedding_note_pred, Literal(consolidated_text, lang="en")))
        updated_subjects += 1

    return updated_subjects


# How to run the program:
# Step 1: Create a text file listing QNames of predicates to use: such as embedding_properties.txt
# Example contents. One per line. No commas. No quotes:
# dp:has_bounded_context
# prov:generated
# dp:has_platform_port
#
# Step 2: From your repo directory at the terminal:
# 2.1: Test mode (safe — prints only). This is the default.
# python add_embedding_notes_from_properties.py streamforge_data_catalog_V1_w_class_embedding_notes.ttl embedding_properties.txt
#
# 2.2: Insert mode
# python add_embedding_notes_from_properties.py streamforge_data_catalog_V1_w_class_embedding_notes.ttl embedding_properties.txt --insert
#
# That will write a new ontology file based on the input filename:
# If the input file is streamforge_data_catalog_V1_w_class_embedding_notes.ttl the output file will be:
# streamforge_data_catalog_V1_w_class_embedding_notes_w_prop_embedding_notes.ttl

if __name__ == "__main__":
    import sys
    from pathlib import Path
    from rdflib import Graph, Namespace

    if len(sys.argv) < 3:
        print("Usage:")
        print(
            "  python add_embedding_notes_from_properties_consolidated.py "
            "<input.ttl> <properties.txt> [--insert]"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    properties_file = sys.argv[2]
    insert_mode = "--insert" in sys.argv

    def make_output_path(input_path: str, suffix: str) -> Path:
        path = Path(input_path)
        return path.with_name(f"{path.stem}{suffix}{path.suffix}")

    # Load graph
    g = Graph()
    g.parse(input_file, format="turtle")

    # Bind prefixes (adjust if needed)
    g.bind("dctm", Namespace("http://purl.org/dc/terms/"))
    g.bind("odrl", Namespace("http://www.w3.org/ns/odrl/2/"))
    g.bind("dp", Namespace("https://www.michaeldebellis.com/dp/"))
    g.bind("docs", Namespace("https://www.michaeldebellis.com/docs/"))
    g.bind("sf", Namespace("https://www.michaeldebellis.com/streamforge/"))
    g.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
    g.bind("dcat", Namespace("http://www.w3.org/ns/dcat#"))
    g.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))
    g.bind("skos", Namespace("http://www.w3.org/2004/02/skos/core#"))

    # Read predicate list
    with open(properties_file, "r", encoding="utf-8") as f:
        props = [line.strip() for line in f if line.strip()]

    print("Properties loaded:", props)

    if insert_mode:
        print("Running in INSERT mode...")
        n = add_embedding_notes_from_properties(g, props, test=False)
        print(f"Updated {n} subjects with consolidated embedding notes.")

        output_file = make_output_path(input_file, "_w_prop_embedding_notes")
        g.serialize(destination=str(output_file), format="turtle")
        print(f"Saved updated ontology to: {output_file}")
    else:
        print("Running in TEST mode...")
        add_embedding_notes_from_properties(g, props, test=True)
