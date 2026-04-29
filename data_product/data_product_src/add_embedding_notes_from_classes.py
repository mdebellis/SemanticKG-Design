from __future__ import annotations

from typing import List, Optional, Dict, Set

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL


def add_embedding_notes_from_classes(
    g: Graph,
    class_qnames: List[str],
    *,
    dp_embedding_note_qname: str = "dp:embedding_note",
    test: bool = True,
    class_label_fallback_to_qname: bool = True,
    end_with_period: bool = True,
    verbose: bool = True,
) -> int:
    """
    Generate embedding-friendly natural-language notes from asserted class hierarchies
    and asserted instance typing.

    For each class in class_qnames:
      1) Generate notes on the class itself:
           "<Class> is a kind of <Superclass>."
           "<Subclass> is a kind of <Class>."
      2) Recursively do the same for all explicitly asserted subclasses.
      3) For each resource explicitly typed as that exact class, generate:
           "<Instance> is an instance of <Class>."

    If class_qnames is empty, default to owl:Thing.

    This version is intentionally simple:
      - it uses only asserted rdfs:subClassOf triples
      - it uses only asserted rdf:type triples
      - it does not depend on a reasoner
      - it assumes asserted instance types are already the intended leaf types

    If test=True: print the notes that would be added.
    If test=False: add (?s dp:embedding_note "note"@en) unless an identical note already exists.

    Returns: number of notes inserted (0 if test=True).
    """

    # --- Helper: expand a QName like "prov:Agent" to a URIRef ---
    def expand_qname(qname: str) -> URIRef:
        if ":" not in qname:
            raise ValueError(f"Expected QName with prefix, got: {qname!r}")
        prefix, local = qname.split(":", 1)
        ns = g.namespace_manager.store.namespace(prefix)
        if ns is None:
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
        for lbl in g.objects(node, RDFS.label):
            if isinstance(lbl, Literal) and lbl.language == "en":
                return str(lbl)
        for lbl in g.objects(node, RDFS.label):
            if isinstance(lbl, Literal):
                return str(lbl)
        return None

    # --- Helper: qname/uri fallback display for classes ---
    def class_display(class_uri: URIRef) -> str:
        class_lbl = get_label_en(class_uri)
        if class_lbl:
            return class_lbl
        if class_label_fallback_to_qname:
            try:
                return g.namespace_manager.normalizeUri(class_uri)
            except Exception:
                return str(class_uri)
        return str(class_uri)

    # Expand dp:embedding_note
    embedding_note_pred = expand_qname(dp_embedding_note_qname)

    # Preload existing embedding notes per subject (lexical form only) for dedup
    existing_notes: Dict[URIRef, Set[str]] = {}
    for s, _, note in g.triples((None, embedding_note_pred, None)):
        if isinstance(note, Literal):
            existing_notes.setdefault(s, set()).add(str(note))
        else:
            existing_notes.setdefault(s, set()).add(str(note))

    inserted = 0

    # --- Helper: add one note if not already present ---
    def maybe_add_note(subject: URIRef, note_text: str) -> None:
        nonlocal inserted

        if end_with_period and not note_text.endswith("."):
            note_text = note_text + "."

        if test:
            print(note_text)
            return

        already = note_text in existing_notes.get(subject, set())
        if already:
            if verbose:
                pass
            return

        g.add((subject, embedding_note_pred, Literal(note_text, lang="en")))
        existing_notes.setdefault(subject, set()).add(note_text)
        inserted += 1

    # --- Helper: get direct named superclasses ---
    def direct_named_superclasses(c: URIRef) -> List[URIRef]:
        supers = []
        for sup in g.objects(c, RDFS.subClassOf):
            if isinstance(sup, URIRef) and sup != OWL.Thing:
                supers.append(sup)
        return supers

    # --- Helper: get direct named subclasses ---
    def direct_named_subclasses(c: URIRef) -> List[URIRef]:
        subs = []
        for sub in g.subjects(RDFS.subClassOf, c):
            if isinstance(sub, URIRef):
                subs.append(sub)
        return subs

    # --- Helper: recurse downward through explicitly asserted named subclasses ---
    def all_named_descendants(root: URIRef) -> Set[URIRef]:
        visited: Set[URIRef] = set()
        stack = [root]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            for sub in direct_named_subclasses(current):
                if sub not in visited:
                    stack.append(sub)

        return visited

    # --- Helper: process one class subtree ---
    def process_class_subtree(root_class: URIRef) -> None:
        scoped_classes = all_named_descendants(root_class)

        # 1) Add class hierarchy notes for every class in the subtree
        for c in scoped_classes:
            c_label = get_label_en(c)
            if c_label is None:
                if class_label_fallback_to_qname:
                    c_label = class_display(c)
                else:
                    raise ValueError(f"Missing rdfs:label@en (or any rdfs:label) for class: {c}")

            # direct superclasses
            for sup in direct_named_superclasses(c):
                sup_label = get_label_en(sup)
                if sup_label is None:
                    if class_label_fallback_to_qname:
                        sup_label = class_display(sup)
                    else:
                        raise ValueError(
                            f"Missing rdfs:label@en (or any rdfs:label) for superclass: {sup}"
                        )

                note_text = f"{c_label} is a kind of {sup_label}"
                maybe_add_note(c, note_text)

            # direct subclasses
            for sub in direct_named_subclasses(c):
                sub_label = get_label_en(sub)
                if sub_label is None:
                    if class_label_fallback_to_qname:
                        sub_label = class_display(sub)
                    else:
                        raise ValueError(
                            f"Missing rdfs:label@en (or any rdfs:label) for subclass: {sub}"
                        )

                note_text = f"{sub_label} is a kind of {c_label}"
                maybe_add_note(c, note_text)

        # 2) Add instance typing notes only for directly asserted rdf:type values
        for c in scoped_classes:
            c_label = get_label_en(c)
            if c_label is None:
                if class_label_fallback_to_qname:
                    c_label = class_display(c)
                else:
                    raise ValueError(f"Missing rdfs:label@en (or any rdfs:label) for class: {c}")

            for inst in g.subjects(RDF.type, c):
                if not isinstance(inst, URIRef):
                    continue

                inst_label = get_label_en(inst)
                if inst_label is None:
                    raise ValueError(
                        f"Missing rdfs:label@en (or any rdfs:label) for instance: {inst}"
                    )

                note_text = f"{inst_label} is an instance of {c_label}"
                maybe_add_note(inst, note_text)

    # Default to owl:Thing if no classes provided
    if not class_qnames:
        class_uris = [OWL.Thing]
    else:
        class_uris = [expand_qname(cq) for cq in class_qnames]

    for class_uri in class_uris:
        process_class_subtree(class_uri)

    return inserted


# How to run the program:
# Step 1: Create a text file listing QNames of classes to use: such as embedding_classes.txt
# Example contents. One per line. No commas. No quotes:
# prov:Person
# dp:User
# dp:Creator
# prov:Organization
# dp:Data_Product_Team
#
# If the file is empty, the program defaults to owl:Thing
#
# Step2: From your repo directory at the terminal:
# 2.1: Test mode (safe — prints only) This is the default
# python add_embedding_notes_from_classes.py streamforge_data_catalog_V1.ttl embedding_classes.txt
#
# 2.2: Insert mode
# python add_embedding_notes_from_classes.py streamforge_data_catalog_V1.ttl embedding_classes.txt --insert
#
# That will write a new ontology file: output_with_embedding_notes.ttl

if __name__ == "__main__":
    import sys
    from rdflib import Graph, Namespace

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python add_embedding_notes_from_classes.py <input.ttl> <classes.txt> [--insert]")
        sys.exit(1)

    input_file = sys.argv[1]
    classes_file = sys.argv[2]
    insert_mode = "--insert" in sys.argv

    # Load graph
    g = Graph()
    g.parse(input_file, format="turtle")

    # Bind prefixes (adjust if needed)
    g.bind("odrl", Namespace("http://www.w3.org/ns/odrl/2/"))
    g.bind("dctm", Namespace("http://purl.org/dc/terms/"))
    g.bind("dp", Namespace("https://www.michaeldebellis.com/dp/"))
    g.bind("docs", Namespace("https://www.michaeldebellis.com/docs/"))
    g.bind("sf", Namespace("https://www.michaeldebellis.com/streamforge/"))
    g.bind("prov", Namespace("http://www.w3.org/ns/prov#"))
    g.bind("dcat", Namespace("http://www.w3.org/ns/dcat#"))
    g.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))
    g.bind("rdf", Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
    g.bind("owl", Namespace("http://www.w3.org/2002/07/owl#"))

    # Read class list
    with open(classes_file, "r", encoding="utf-8") as f:
        classes = [line.strip() for line in f if line.strip()]

    if classes:
        print("Classes loaded:", classes)
    else:
        print("No classes loaded from file; defaulting to owl:Thing")

    if insert_mode:
        print("Running in INSERT mode...")
        n = add_embedding_notes_from_classes(g, classes, test=False)
        print(f"Inserted {n} embedding notes.")
        g.serialize("output_with_embedding_notes.ttl", format="turtle")
    else:
        print("Running in TEST mode...")
        add_embedding_notes_from_classes(g, classes, test=True)