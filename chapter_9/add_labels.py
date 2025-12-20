from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Optional

from rdflib import Graph


# -----------------------------
# Parameters
# -----------------------------

@dataclass(frozen=True)
class LabelQueryParams:
    """
    Parameters used to specialize the SPARQL label-generator updates.

    namespace_segment:
        The string that identifies where the local name begins in the IRI.
        Example: 'people/' or 'pattern_examples/'.

    delimiter:
        The character used inside IRIs to separate words, to be converted to spaces.
        Example: '_' -> 'Some_Class' becomes 'Some Class'
    """
    namespace_segment: str
    delimiter: str = "_"
    lang: str = "en"


# -----------------------------
# SPARQL UPDATE templates
# -----------------------------

PREFIXES = """\
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
"""


CLASS_LABEL_INSERT_TEMPLATE = """\
{prefixes}
INSERT {{
  ?class rdfs:label ?label_lit .
}}
WHERE {{
  ?class rdf:type owl:Class .
  BIND(STRAFTER(STR(?class), '{namespace_segment}') AS ?name)
  BIND(REPLACE(?name, "{delimiter}", " ") AS ?lblname)
  BIND(STRLANG(?lblname, "{lang}") AS ?label_lit)
  OPTIONAL {{ ?class rdfs:label ?existing_label . }}
  FILTER(
    ?class != owl:Thing &&
    ?class != owl:Nothing &&
    "" != ?lblname &&
    !BOUND(?existing_label)
  )
}}

"""


OBJECT_PROPERTY_LABEL_INSERT_TEMPLATE = """\
{prefixes}
INSERT {{
  ?p rdfs:label ?label_lit .
}}
WHERE {{
  ?p rdf:type owl:ObjectProperty .
  BIND(STRAFTER(STR(?p), '{namespace_segment}') AS ?name)
  BIND(LCASE(REPLACE(?name, "{delimiter}", " ")) AS ?lblname)
  BIND(STRLANG(?lblname, "{lang}") AS ?label_lit)
  OPTIONAL {{ ?p rdfs:label ?existing_label . }}
  FILTER(
    ?p != owl:topObjectProperty &&
    ?p != owl:bottomObjectProperty &&
    "" != ?lblname &&
    !BOUND(?existing_label)
  )
}}

"""

INDIVIDUAL_LABEL_INSERT_TEMPLATE = """\
{prefixes}
INSERT {{
  ?individual rdfs:label ?label_lit .
}}
WHERE {{
  ?individual rdf:type owl:NamedIndividual .
  BIND(STRAFTER(STR(?individual), '{namespace_segment}') AS ?name)
  BIND(REPLACE(?name, "{delimiter}", " ") AS ?lblname)
  BIND(STRLANG(?lblname, "{lang}") AS ?label_lit)
  OPTIONAL {{ ?individual rdfs:label ?existing_label . }}
  FILTER("" != ?lblname && !BOUND(?existing_label))
}}

"""
DATATYPE_PROPERTY_LABEL_INSERT_TEMPLATE = """\
{prefixes}
INSERT {{
  ?p rdfs:label ?label_lit .
}}
WHERE {{
  ?p rdf:type owl:DatatypeProperty .
  BIND(STRAFTER(STR(?p), '{namespace_segment}') AS ?name)
  BIND(LCASE(REPLACE(?name, "{delimiter}", " ")) AS ?lblname)
  BIND(STRLANG(?lblname, "{lang}") AS ?label_lit)
  OPTIONAL {{ ?p rdfs:label ?existing_label . }}
  FILTER(
    ?p != owl:topDataProperty &&
    ?p != owl:bottomDataProperty &&
    "" != ?lblname &&
    !BOUND(?existing_label)
  )
}}

"""
ANNOTATION_PROPERTY_LABEL_INSERT_TEMPLATE = """\
{prefixes}
INSERT {{
  ?p rdfs:label ?label_lit .
}}
WHERE {{
  ?p rdf:type owl:AnnotationProperty .
  BIND(STRAFTER(STR(?p), '{namespace_segment}') AS ?name)
  BIND(LCASE(REPLACE(?name, "{delimiter}", " ")) AS ?lblname)
  BIND(STRLANG(?lblname, "{lang}") AS ?label_lit)
  OPTIONAL {{ ?p rdfs:label ?existing_label . }}
  FILTER("" != ?lblname && !BOUND(?existing_label))
}}

"""


# -----------------------------
# Query generation helpers
# -----------------------------

def render_update(template: str, params: LabelQueryParams) -> str:
    """
    Substitute parameters into a SPARQL UPDATE template.

    Intentionally simple and explicit: we want the example to be easy to understand,
    and easy to extend by copying patterns.
    """
    return template.format(
        prefixes=PREFIXES.strip(),
        namespace_segment=params.namespace_segment,
        delimiter=params.delimiter,
        lang=params.lang,
    )


def generate_label_updates(params: LabelQueryParams) -> Dict[str, str]:
    """
    Generate the SPARQL UPDATE statements we will execute.

    This example includes:
      - owl:Class
      - owl:ObjectProperty
      - owl:NamedIndividual
    """
    updates: Dict[str, str] = {}

    updates["add_missing_class_labels"] = render_update(CLASS_LABEL_INSERT_TEMPLATE, params)
    updates["add_missing_object_property_labels"] = render_update(OBJECT_PROPERTY_LABEL_INSERT_TEMPLATE, params)
    updates["add_missing_individual_labels"] = render_update(INDIVIDUAL_LABEL_INSERT_TEMPLATE, params)
    updates["add_missing_datatype_property_labels"] = render_update(DATATYPE_PROPERTY_LABEL_INSERT_TEMPLATE, params)

    updates["add_missing_annotation_property_labels"] = render_update(
        ANNOTATION_PROPERTY_LABEL_INSERT_TEMPLATE,
        params
    )

    return updates


def write_updates_to_file(updates: Dict[str, str], output_path: Path) -> None:
    """
    Write all generated updates to a single .rq file for inspection/debugging.
    """
    parts = []
    for name, update_text in updates.items():
        parts.append(f"# --- {name} ---\n")
        parts.append(update_text.strip())
        parts.append("\n\n")
    output_path.write_text("".join(parts), encoding="utf-8")


# -----------------------------
# Apply updates to a Turtle file
# -----------------------------

def output_ttl_path_with_labels(input_ttl_path: Path) -> Path:
    """
    Create an output file path by appending '_with_labels' before the file extension.
    Example:
      Pattern_Examples_No_Labels.ttl -> Pattern_Examples_No_Labels_with_labels.ttl
    """
    suffix = input_ttl_path.suffix  # likely ".ttl"
    stem = input_ttl_path.stem
    return input_ttl_path.with_name(f"{stem}_with_labels{suffix}")


def apply_updates_to_ttl(
    input_ttl_path: Path,
    output_ttl_path: Path,
    updates: Dict[str, str],
) -> Tuple[int, int]:
    """
    Load a TTL file, apply each SPARQL UPDATE using RDFLib, then write a new TTL file.

    Returns:
      (number_of_updates_applied, total_triples_after)
    """
    g = Graph()
    g.parse(str(input_ttl_path), format="turtle")

    for _name, update_text in updates.items():
        g.update(update_text)

    g.serialize(destination=str(output_ttl_path), format="turtle")
    return len(updates), len(g)


# -----------------------------
# CLI
# -----------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Add missing rdfs:label values to classes, object properties, and individuals in a Turtle ontology."
    )
    p.add_argument(
        "input_ttl",
        help="Input Turtle file path (e.g., Pattern_Examples_No_Labels.ttl)",
    )
    p.add_argument(
        "--ns",
        required=True,
        help="Namespace segment to strip from IRIs (e.g., 'pattern_examples/')",
    )
    p.add_argument(
        "--delimiter",
        default="_",
        help="Delimiter in local names to convert to spaces (default: '_')",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="If set, also write the generated SPARQL updates to a .rq file.",
    )
    p.add_argument(
        "--lang",
        default="en",
        help="Language tag for generated rdfs:label values (default: 'en')",
    )

    return p.parse_args()


def main() -> None:
    args = parse_args()

    input_ttl_path = Path(args.input_ttl)
    if not input_ttl_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_ttl_path}")

    params = LabelQueryParams(namespace_segment=args.ns, delimiter=args.delimiter,lang=args.lang)

    updates = generate_label_updates(params)

    output_ttl_path = output_ttl_path_with_labels(input_ttl_path)

    if args.debug:
        rq_path = output_ttl_path.with_suffix(".rq")
        write_updates_to_file(updates, rq_path)
        print(f"Wrote generated SPARQL updates to: {rq_path}")

    num_updates, triple_count = apply_updates_to_ttl(input_ttl_path, output_ttl_path, updates)
    print(f"Applied {num_updates} SPARQL updates.")
    print(f"Wrote labeled ontology to: {output_ttl_path} (triples: {triple_count})")

# Example: python add_labels.py Pattern_Examples_No_Labels.ttl --ns "pattern_examples/"
# With no debugging only outputs new ontology file
# Example with debugging: python add_labels.py Pattern_Examples_No_Labels.ttl --ns "pattern_examples/" --debug
# With debugging outputs new ontology file and also save generated queries to ontology_file_name_queries.rq

if __name__ == "__main__":
    main()
