from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

# Namespaces
GORA = Namespace("https://www.michaeldebellis.com/gora/")
BASE = Namespace("https://www.michaeldebellis.com/gora/examples/")

# ---------------------------------------------------------------------
# Sample data: imagine this came from JSON, CSV, an API, etc.
# ---------------------------------------------------------------------
sample_events = [
    {
        "id": "evt1001",
        "primary_object": "satA",
        "secondary_object": "satB",
        "closest_approach_time": "2025-01-01T12:00:00Z",
        "min_distance_m": 820.5,
        "risk_category": "Low"
    }
]

# ---------------------------------------------------------------------
# RDF builder
# ---------------------------------------------------------------------
def build_graph():
    g = Graph()
    g.bind("gora", GORA)
    g.bind("ex", BASE)

    for ev in sample_events:
        event_uri = BASE[ev["id"]]
        primary_uri = BASE[ev["primary_object"]]
        secondary_uri = BASE[ev["secondary_object"]]

        # Type the event
        g.add((event_uri, RDF.type, GORA.Conjunction_Event))

        # Link objects
        g.add((event_uri, GORA.has_primary_object, primary_uri))
        g.add((event_uri, GORA.has_secondary_object, secondary_uri))

        # Time
        g.add((
            event_uri,
            GORA.has_closest_approach_time,
            Literal(ev["closest_approach_time"], datatype=XSD.dateTime)
        ))

        # Distance
        g.add((
            event_uri,
            GORA.has_min_distance_m,
            Literal(ev["min_distance_m"], datatype=XSD.decimal)
        ))

        # Risk
        g.add((
            event_uri,
            GORA.has_risk_category,
            Literal(ev["risk_category"], datatype=XSD.string)
        ))

    return g

# ---------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------
if __name__ == "__main__":
    graph = build_graph()
    output_file = "gora_ingest_example.nt"

    graph.serialize(destination=output_file, format="nt")
    print(f"\n✔ Wrote RDF triples to {output_file}\n")
