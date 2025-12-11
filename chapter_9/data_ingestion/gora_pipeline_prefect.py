from datetime import datetime, timezone
from pathlib import Path

from prefect import flow, task
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD

# Namespaces
GORA = Namespace("https://www.michaeldebellis.com/gora/")
PROV = Namespace("http://www.w3.org/ns/prov#")


@task
def build_and_validate_graph() -> Graph:
    """
    Task 1: Build a small RDF graph of conjunction events using the GORA ontology,
    then perform minimal 'shape-like' validation before passing it downstream.

    In this revised version, a single ingestion run processes multiple events.
    """

    g = Graph()
    g.bind("gora", GORA)

    # --- Example event data (mocked here, could come from JSON, CSV, etc.) ---
    # One flow run, three different conjunction events.
    events = [
        {
            "event_id": "evt1001",
            "primary_id": "satA",
            "secondary_id": "satB",
            "closest_approach_time": "2025-01-01T12:00:00Z",
            "min_distance_m": "820.5",
            "risk_category": "Low",
        },
        {
            "event_id": "evt1002",
            "primary_id": "satC",
            "secondary_id": "satD",
            "closest_approach_time": "2025-01-02T03:15:00Z",
            "min_distance_m": "350.0",
            "risk_category": "Medium",
        },
        {
            "event_id": "evt1003",
            "primary_id": "satE",
            "secondary_id": "ISS",
            "closest_approach_time": "2025-01-03T18:42:00Z",
            "min_distance_m": "120.0",
            "risk_category": "High",
        },
    ]

    for ev in events:
        event_iri = GORA[ev["event_id"]]
        primary_iri = GORA[ev["primary_id"]]
        secondary_iri = GORA[ev["secondary_id"]]

        g.add((event_iri, RDF.type, GORA.Conjunction_Event))
        g.add((event_iri, GORA.has_primary_object, primary_iri))
        g.add((event_iri, GORA.has_secondary_object, secondary_iri))
        g.add(
            (
                event_iri,
                GORA.has_closest_approach_time,
                Literal(ev["closest_approach_time"], datatype=XSD.dateTime),
            )
        )
        g.add(
            (
                event_iri,
                GORA.has_min_distance_m,
                Literal(ev["min_distance_m"], datatype=XSD.decimal),
            )
        )
        g.add(
            (
                event_iri,
                GORA.has_risk_category,
                Literal(ev["risk_category"]),
            )
        )

    # --- Minimal validation: each Conjunction_Event must have required properties ---

    required_props = [
        GORA.has_primary_object,
        GORA.has_secondary_object,
        GORA.has_closest_approach_time,
        GORA.has_min_distance_m,
        GORA.has_risk_category,
    ]

    bad_events = []

    for ev in g.subjects(RDF.type, GORA.Conjunction_Event):
        missing = [p for p in required_props if not list(g.objects(ev, p))]
        if missing:
            bad_events.append((ev, missing))

    if bad_events:
        # In a real system you would log more detail; here we just fail fast.
        raise ValueError(f"Validation failed for events: {bad_events}")

    return g


@task
def write_outputs_and_prov(events_graph: Graph) -> None:
    """
    Task 2: Write the validated ABox as N-Triples, and record PROV-O metadata
    describing this ingestion run AND its relationship to the domain events.
    """

    # --- 1) Write ABox triples to gora_ingest_example.nt ---

    abox_path = Path("gora_ingest_example.nt").resolve()
    nt_data = events_graph.serialize(format="nt")
    abox_path.write_text(nt_data, encoding="utf-8")

    # --- 2) Build a PROV graph describing this ingestion run ---

    prov_graph = Graph()
    prov_graph.bind("prov", PROV)
    prov_graph.bind("gora", GORA)

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")

    run_iri = GORA[f"Ingestion_Run_{run_id}"]
    input_iri = GORA[f"Input_Batch_{run_id}"]
    output_iri = GORA[f"Output_File_{run_id}"]
    pipeline_iri = GORA["Ingestion_Pipeline"]

    # Activity: the ingestion run
    prov_graph.add((run_iri, RDF.type, PROV.Activity))
    prov_graph.add(
        (run_iri, PROV.startedAtTime, Literal(now.isoformat(), datatype=XSD.dateTime))
    )
    prov_graph.add(
        (run_iri, PROV.endedAtTime, Literal(now.isoformat(), datatype=XSD.dateTime))
    )
    prov_graph.add((run_iri, PROV.wasAssociatedWith, pipeline_iri))

    # Agent: the ingestion pipeline itself (very simple)
    prov_graph.add((pipeline_iri, RDF.type, PROV.SoftwareAgent))
    prov_graph.add(
        (pipeline_iri, PROV.label, Literal("GORA Ingestion Pipeline"))
    )

    # Entity: input batch (simplified)
    prov_graph.add((input_iri, RDF.type, PROV.Entity))
    prov_graph.add(
        (input_iri, PROV.atLocation, Literal("mock input batch for example"))
    )
    prov_graph.add((run_iri, PROV.used, input_iri))

    # Entity: output file
    prov_graph.add((output_iri, RDF.type, PROV.Entity))
    prov_graph.add((output_iri, PROV.atLocation, Literal(str(abox_path))))
    prov_graph.add((run_iri, PROV.generated, output_iri))

    # --- 3) Connect domain events to this PROV activity (A, B, C) ---

    for ev in events_graph.subjects(RDF.type, GORA.Conjunction_Event):
        # Treat each event as a PROV Entity as well
        prov_graph.add((ev, RDF.type, PROV.Entity))

        # A) Link event to the ingestion run that produced it
        prov_graph.add((ev, PROV.wasGeneratedBy, run_iri))

        # B) Attach generation timestamp
        prov_graph.add(
            (ev, PROV.generatedAtTime, Literal(now.isoformat(), datatype=XSD.dateTime))
        )

        # C) Record that the event is derived from this input batch
        prov_graph.add((ev, PROV.wasDerivedFrom, input_iri))

    # --- 4) Serialize PROV information to gora_ingest_prov.nt ---

    prov_path = Path("gora_ingest_prov.nt").resolve()
    prov_nt = prov_graph.serialize(format="nt")
    prov_path.write_text(prov_nt, encoding="utf-8")

    print(f"Wrote ABox N-Triples to: {abox_path}")
    print(f"Wrote PROV N-Triples to: {prov_path}")


@flow
def gora_ingestion_flow():
    """
    Prefect flow: build a small GORA ABox, validate it, and
    write both data and PROV metadata as N-Triples files.

    This version demonstrates a single ingestion run that processes
    multiple conjunction events.
    """
    g = build_and_validate_graph()
    write_outputs_and_prov(g)


if __name__ == "__main__":
    gora_ingestion_flow()
