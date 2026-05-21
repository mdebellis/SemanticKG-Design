from __future__ import annotations

from typing import Dict, List, Optional, Set

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
    and asserted instance typing, consolidating all notes for each subject into a
    single dp:embedding_note value.

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

    Consolidation behavior:
      - generated note strings are first collected in memory by subject
      - existing dp:embedding_note values for that subject are also preserved
      - if an existing dp:embedding_note contains multiple lines, each non-empty line
        is treated as a distinct note for deduplication
      - all notes for each subject are deduplicated while preserving order
      - in insert mode, old dp:embedding_note triples for that subject are removed
        and replaced by one consolidated lang="en" literal
      - in test mode, the consolidated note preview is printed but the graph is not changed

    Returns:
      - if test=True: 0
      - if test=False: number of subjects whose consolidated embedding note changed
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

    # --- Helper: display subject in test output ---
    def subject_display(subject: URIRef) -> str:
        subject_lbl = get_label_en(subject)
        if subject_lbl:
            try:
                return f"{subject_lbl} ({g.namespace_manager.normalizeUri(subject)})"
            except Exception:
                return f"{subject_lbl} ({subject})"
        try:
            return g.namespace_manager.normalizeUri(subject)
        except Exception:
            return str(subject)

    # Expand dp:embedding_note
    embedding_note_pred = expand_qname(dp_embedding_note_qname)

    # Collected note strings to be added, grouped by subject.
    pending_notes: Dict[URIRef, List[str]] = {}

    # --- Helper: normalize note ending ---
    def normalize_note_text(note_text: str) -> str:
        note_text = note_text.strip()
        if end_with_period and note_text and not note_text.endswith("."):
            note_text = note_text + "."
        return note_text

    # --- Helper: queue one generated note for later consolidation ---
    def queue_note(subject: URIRef, note_text: str) -> None:
        note_text = normalize_note_text(note_text)
        if not note_text:
            return
        pending_notes.setdefault(subject, []).append(note_text)

    # --- Helper: split existing literals into individual note lines ---
    def note_lines_from_existing_value(value: object) -> List[str]:
        text = str(value)
        return [line.strip() for line in text.splitlines() if line.strip()]

    # --- Helper: preserve insertion order while deduplicating ---
    def unique_preserving_order(items: List[str]) -> List[str]:
        seen: Set[str] = set()
        result: List[str] = []

        for item in items:
            item = normalize_note_text(item)
            if not item or item in seen:
                continue
            seen.add(item)
            result.append(item)

        return result

    # --- Helper: get existing note lines for a subject ---
    def existing_note_lines(subject: URIRef) -> List[str]:
        lines: List[str] = []

        for existing in g.objects(subject, embedding_note_pred):
            lines.extend(note_lines_from_existing_value(existing))

        return unique_preserving_order(lines)

    # --- Helper: preview consolidated output without changing the graph ---
    def print_consolidation_preview() -> None:
        if not pending_notes:
            print("No embedding notes generated.")
            return

        for subject in sorted(pending_notes.keys(), key=lambda s: subject_display(s)):
            existing_lines = existing_note_lines(subject)
            generated_lines = unique_preserving_order(pending_notes[subject])
            consolidated_lines = unique_preserving_order(existing_lines + generated_lines)

            print()
            print(f"Subject: {subject_display(subject)}")
            print("-" * 72)

            if existing_lines:
                print("Existing note lines preserved:")
                for line in existing_lines:
                    print(f"  - {line}")

            print("Generated note lines:")
            for line in generated_lines:
                print(f"  - {line}")

            print("Consolidated dp:embedding_note value:")
            print('"""')
            print("\n".join(consolidated_lines))
            print('"""')

    # --- Helper: replace old note triples with one consolidated note per subject ---
    def consolidate_embedding_notes() -> int:
        changed_subjects = 0

        for subject, generated_notes in pending_notes.items():
            existing_literals = list(g.objects(subject, embedding_note_pred))
            existing_lines = existing_note_lines(subject)
            generated_lines = unique_preserving_order(generated_notes)
            consolidated_lines = unique_preserving_order(existing_lines + generated_lines)

            if not consolidated_lines:
                continue

            consolidated_text = "\n".join(consolidated_lines)
            current_texts = [str(lit) for lit in existing_literals]

            # If there is already exactly one literal with the consolidated text,
            # leave the graph unchanged.
            if len(current_texts) == 1 and current_texts[0] == consolidated_text:
                continue

            for lit in existing_literals:
                g.remove((subject, embedding_note_pred, lit))

            g.add((subject, embedding_note_pred, Literal(consolidated_text, lang="en")))
            changed_subjects += 1

            if verbose:
                try:
                    display = subject_display(subject)
                except Exception:
                    display = str(subject)
                print(f"Consolidated embedding note for: {display}")

        return changed_subjects

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
                queue_note(c, note_text)

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
                queue_note(c, note_text)

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
                queue_note(inst, note_text)

    # Default to owl:Thing if no classes provided
    if not class_qnames:
        class_uris = [OWL.Thing]
    else:
        class_uris = [expand_qname(cq) for cq in class_qnames]

    for class_uri in class_uris:
        process_class_subtree(class_uri)

    if test:
        print_consolidation_preview()
        return 0

    return consolidate_embedding_notes()


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
# Step 2: From your repo directory at the terminal:
# 2.1: Test mode (safe — prints only). This is the default.
# python add_embedding_notes_from_classes.py streamforge_data_catalog_V1.ttl embedding_classes.txt
#
# 2.2: Insert mode
# python add_embedding_notes_from_classes.py streamforge_data_catalog_V1.ttl embedding_classes.txt --insert
#
# That will write a new ontology file based on the input filename:
# If the input file is streamforge_data_catalog_V1.ttl the output file will be:
# streamforge_data_catalog_V1_w_class_embedding_notes.ttl
#
# Important:
# This version keeps the same dp:embedding_note property but consolidates all notes
# for each subject into one multi-line literal.

if __name__ == "__main__":
    import sys
    from pathlib import Path
    from rdflib import Graph, Namespace

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python add_embedding_notes_from_classes_consolidated.py <input.ttl> <classes.txt> [--insert]")
        sys.exit(1)

    input_file = sys.argv[1]
    classes_file = sys.argv[2]
    insert_mode = "--insert" in sys.argv

    def make_output_path(input_path: str, suffix: str) -> Path:
        path = Path(input_path)
        return path.with_name(f"{path.stem}{suffix}{path.suffix}")

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
        print(f"Consolidated embedding notes for {n} subjects.")

        output_file = make_output_path(input_file, "_w_class_embedding_notes")
        g.serialize(destination=str(output_file), format="turtle")
        print(f"Saved updated ontology to: {output_file}")
    else:
        print("Running in TEST mode...")
        add_embedding_notes_from_classes(g, classes, test=True)
