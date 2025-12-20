from pathlib import Path
from typing import List, Optional, Tuple, Union

from rdflib import Graph, URIRef, Namespace, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD

SH = Namespace("http://www.w3.org/ns/shacl#")


def _infer_sep_from_graph(g: Graph, base: str) -> str:
    """
    Try to infer whether terms under `base` most commonly use '#' or '/'.
    Defaults to '#'.
    """
    hash_count = 0
    slash_count = 0
    base_str = str(base)
    for s in set(g.subjects(RDF.type, OWL.DatatypeProperty)):
        s_str = str(s)
        if s_str.startswith(base_str):
            if "#" in s_str[len(base_str):]:
                hash_count += 1
            else:
                slash_count += 1
    return "#" if hash_count >= slash_count else "/"


def _expand_one_identifier(
    g: Graph,
    ident: str,
    iri_base: Optional[str],
    iri_sep: Optional[str]
) -> URIRef:
    """
    Resolve `ident` which can be a full IRI, CURIE, or bare local name.
    - Full IRI: used as-is
    - CURIE: expanded via graph prefixes
    - Bare name: requires iri_base; uses iri_sep or infers it
    """
    # Full IRI?
    if "://" in ident:
        return URIRef(ident)

    # CURIE?
    if ":" in ident:
        prefix, local = ident.split(":", 1)
        ns = dict(g.namespace_manager.namespaces()).get(prefix)
        if ns:
            return URIRef(str(ns) + local)
        # Not a known prefix; treat as bare name fall-through

    # Bare local name
    if not iri_base:
        raise ValueError(
            f"Identifier '{ident}' is a bare name but no iri_base was provided."
        )
    sep = iri_sep or _infer_sep_from_graph(g, iri_base)
    if not iri_base.endswith(("#", "/")):
        base_full = iri_base + sep
    else:
        # If base already ends with a separator, don't double it
        base_full = iri_base
    return URIRef(base_full + ident)


def _select_default_datatype_properties(g: Graph) -> List[Tuple[URIRef, URIRef]]:
    """
    Find all owl:DatatypeProperty with rdfs:range in {xsd:decimal, xsd:integer, xsd:dateTime}.
    Returns list of (property, expected_datatype).
    """
    allowed = {XSD.decimal, XSD.integer, XSD.dateTime}
    results = []
    for p in g.subjects(RDF.type, OWL.DatatypeProperty):
        for rng in g.objects(p, RDFS.range):
            if isinstance(rng, URIRef) and rng in allowed:
                results.append((p, rng))
    return results


def _localname(u: Union[str, URIRef]) -> str:
    s = str(u)
    if "#" in s:
        return s.split("#")[-1]
    return s.rstrip("/").split("/")[-1]


def _add_prefixes(dst: Graph, src: Graph):
    # copy common prefixes + whatever the source graph already has
    dst.namespace_manager.bind("rdf", RDF)
    dst.namespace_manager.bind("rdfs", RDFS)
    dst.namespace_manager.bind("owl", OWL)
    dst.namespace_manager.bind("xsd", XSD)
    dst.namespace_manager.bind("sh", SH)
    for prefix, ns in src.namespace_manager.namespaces():
        # don’t clobber SH, etc.; RDFLib handles collisions gracefully
        dst.namespace_manager.bind(prefix, ns, replace=False)


def owl_to_shacl(
    path: str,
    datatype_properties: Optional[List[str]] = None,
    remove_ranges: bool = False,
    shacl_path: Optional[str] = None,
    iri_base: Optional[str] = None,
    iri_sep: Optional[str] = None,
    strict_ident_check: bool = True,
) -> Tuple[Path, Optional[Path]]:
    """
    Generate SHACL constraints for datatype properties from an OWL ontology.

    Parameters
    ----------
    path : str
        Path to the ontology file (any RDF format readable by RDFLib).
    datatype_properties : Optional[List[str]]
        Identifiers of properties to generate shapes for. Each item may be:
          - full IRI (e.g., 'http://ex.org/has_birthdate')
          - CURIE (e.g., 'ex:has_birthdate' – must be declared in the graph)
          - bare local name (e.g., 'has_birthdate' – requires `iri_base`)
        If None, auto-discovers all owl:DatatypeProperty with rdfs:range in
        {xsd:decimal, xsd:integer, xsd:dateTime}.
    remove_ranges : bool
        If True, removes rdfs:range triples for the targeted properties from the ontology
        and writes a new '*_refactored.ttl' file. Default False.
    shacl_path : Optional[str]
        Output path for SHACL; default is '<basename>_constraints.shacl.ttl' next to `path`.
    iri_base : Optional[str]
        Base IRI used ONLY for resolving bare local names in `datatype_properties`.
    iri_sep : Optional[str]
        Separator to use with `iri_base` for bare names ('#' or '/'). If not provided,
        attempts to infer from existing terms; defaults to '#'.
    strict_ident_check : bool
        If True, error when a provided property cannot be found as owl:DatatypeProperty.
        If False, skip unknowns with a warning.

    Returns
    -------
    (shacl_file_path, refactored_file_path_or_None)
    """
    # ---------- Load the ontology ----------
    src_path = Path(path)
    if not src_path.exists():
        raise FileNotFoundError(f"Ontology file not found: {path}")

    g = Graph()
    g.parse(src_path.as_posix())  # format auto-detected

    # ---------- Determine target properties ----------
    targets: List[Tuple[URIRef, URIRef]] = []

    if datatype_properties:
        # Resolve each identifier and look up its declared range
        for ident in datatype_properties:
            prop = _expand_one_identifier(g, ident, iri_base, iri_sep)
            # ensure it's declared (or at least used) as a datatype property
            is_dataprop = (prop, RDF.type, OWL.DatatypeProperty) in g
            if not is_dataprop:
                # Sometimes ontologies omit explicit type; still allow if it is used with literal objects
                sample_literal_use = next(g.objects(prop, RDFS.range), None)
                if not sample_literal_use:
                    msg = f"Identifier '{ident}' resolved to <{prop}>, which is not an owl:DatatypeProperty."
                    if strict_ident_check:
                        raise ValueError(msg)
                    else:
                        print(f"[warn] {msg} Skipping.")
                        continue

            # Determine expected datatype (use explicit rdfs:range if any)
            rngs = list(g.objects(prop, RDFS.range))
            if rngs:
                # choose first XSD datatype if multiple; (first attempt keeps it simple)
                xsd_rngs = [r for r in rngs if isinstance(r, URIRef) and str(r).startswith(str(XSD))]
                if xsd_rngs:
                    targets.append((prop, xsd_rngs[0]))
                else:
                    print(f"[warn] Property <{prop}> has non-XSD/complex range(s); skipping in this first pass.")
            else:
                print(f"[warn] Property <{prop}> has no explicit rdfs:range; skipping in this first pass.")
    else:
        targets = _select_default_datatype_properties(g)

    if not targets:
        raise RuntimeError("No datatype properties selected for SHACL generation.")

    # ---------- Build SHACL shapes ----------
    shapes_g = Graph()
    _add_prefixes(shapes_g, g)

    # simple shapes graph node (optional)
    # shapes_graph_uri = URIRef(str(src_path.resolve().as_uri()) + "#Shapes")  # optional; not strictly needed

    for prop, expected_dt in targets:
        # NodeShape per property
        shape_uri = URIRef(str(prop) + "_Shape")
        shapes_g.add((shape_uri, RDF.type, SH.NodeShape))
        # Validate wherever the property appears
        shapes_g.add((shape_uri, SH.targetSubjectsOf, prop))

        # PropertyShape
        pshape = BNode()
        shapes_g.add((shape_uri, SH.property, pshape))
        shapes_g.add((pshape, SH.path, prop))
        shapes_g.add((pshape, SH.datatype, expected_dt))
        # Provide a helpful message
        msg = f"Value of {str(prop)} must have datatype {str(expected_dt)}."
        shapes_g.add((pshape, SH.message, Literal(msg)))

        # By default, SHACL violations are severity=Violation; can be made explicit:
        # shapes_g.add((pshape, SH.severity, SH.Violation))

    # ---------- Write SHACL file ----------
    if shacl_path:
        shacl_out = Path(shacl_path)
        if not shacl_out.suffix:
            shacl_out = shacl_out.with_suffix(".ttl")
    else:
        shacl_out = src_path.with_name(src_path.stem + "_constraints.shacl.ttl")

    shapes_g.serialize(destination=shacl_out.as_posix(), format="turtle")

    # ---------- Optionally remove ranges and write refactored ontology ----------
    refactored_out: Optional[Path] = None
    if remove_ranges:
        to_remove = []
        for prop, expected_dt in targets:
            for rng in g.objects(prop, RDFS.range):
                to_remove.append((prop, RDFS.range, rng))
        for triple in to_remove:
            g.remove(triple)

        refactored_out = src_path.with_name(src_path.stem + "_refactored.ttl")
        g.serialize(destination=refactored_out.as_posix(), format="turtle")

    return shacl_out, refactored_out
