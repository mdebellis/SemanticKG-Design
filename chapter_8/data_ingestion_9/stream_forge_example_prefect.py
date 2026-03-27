from datetime import datetime, timezone
from pathlib import Path
import os
import csv
import shutil
import hashlib
from typing import Tuple, Dict

from prefect import flow, task
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD

# Namespaces
SFE = Namespace("https://www.michaeldebellis.com/stream_forge_example/")
PROV = Namespace("http://www.w3.org/ns/prov#")

# Runtime directories (outside GitHub)
BASE_DIR = Path(os.environ["INGEST_BASE_DIR"])
INPUT_DIR = BASE_DIR / "input_data"
PROCESSED_DIR = BASE_DIR / "processed_data"
DATA_FOR_GRAPH_DIR = BASE_DIR / "data_for_graph"
LOGS_DIR = BASE_DIR / "logs"

# Ensure dirs exist (safe if they already exist)
for d in (INPUT_DIR, PROCESSED_DIR, DATA_FOR_GRAPH_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# CSV columns (Stream_Forge_Example Trending Snapshot)
COL_SNAPSHOT_TIME = "snapshot_time"
COL_REGION = "region"
COL_CATEGORY = "category"
COL_RANK = "rank"
COL_VIDEO_ID = "video_id"
COL_VIDEO_TITLE = "video_title"
COL_CHANNEL_ID = "channel_id"
COL_CHANNEL_NAME = "channel_name"
COL_VIEWS_24H = "views_24h"
COL_LIKES_24H = "likes_24h"
COL_COMMENTS_24H = "comments_24h"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pick_newest_input_csv() -> Path:
    csv_files = sorted(INPUT_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csv_files:
        raise FileNotFoundError(f"No .csv files found in input_data: {INPUT_DIR}")
    return csv_files[0]


def parse_int(row: Dict[str, str], col: str, default: int = 0) -> int:
    raw = (row.get(col) or "").strip()
    if raw == "":
        return default
    return int(raw)


def parse_str(row: Dict[str, str], col: str, default: str = "") -> str:
    return (row.get(col) or default).strip()


@task
def build_and_validate_graph() -> Tuple[Graph, Path, str]:
    """
    Task 1: Read a CSV from input_data, build a Stream_Forge_Example ABox,
    and perform minimal validation.

    Returns:
      (graph, input_csv_path, input_sha256)
    """
    input_csv = pick_newest_input_csv()
    input_hash = sha256_file(input_csv)

    g = Graph()
    g.bind("sfe", SFE)

    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"CSV had no data rows: {input_csv}")

    # Keep demo compact: ingest up to first 50 rows (adjust if you like)
    rows = rows[:50]

    for row in rows:
        video_id = parse_str(row, COL_VIDEO_ID)
        channel_id = parse_str(row, COL_CHANNEL_ID)
        snapshot_time = parse_str(row, COL_SNAPSHOT_TIME)

        # Skip incomplete rows
        if not (video_id and channel_id and snapshot_time):
            continue

        region = parse_str(row, "region_code", default="Unknown")
        category = parse_str(row, COL_CATEGORY, default="Unknown")
        rank = parse_int(row, COL_RANK, default=0)

        video_title = parse_str(row, COL_VIDEO_TITLE, default="")
        channel_name = parse_str(row, COL_CHANNEL_NAME, default="")

        views_24h = parse_int(row, COL_VIEWS_24H, default=0)
        likes_24h = parse_int(row, COL_LIKES_24H, default=0)
        comments_24h = parse_int(row, COL_COMMENTS_24H, default=0)

        # Create stable IRIs
        video_iri = SFE[f"Video/{video_id}"]
        channel_iri = SFE[f"Channel/{channel_id}"]

        # Snapshot record is per (snapshot_time, region, category, rank, video)
        safe_time = snapshot_time.replace(":", "").replace("-", "")
        record_id = f"{safe_time}_{region}_{category}_{rank}_{video_id}".replace(" ", "_")
        record_iri = SFE[f"Trending_Snapshot_Record/{record_id}"]

        # Types
        g.add((record_iri, RDF.type, SFE.Trending_Snapshot_Record))
        g.add((video_iri, RDF.type, SFE.Video))
        g.add((channel_iri, RDF.type, SFE.Channel))

        # Core relationships
        g.add((record_iri, SFE.has_video, video_iri))
        g.add((record_iri, SFE.has_channel, channel_iri))

        # Snapshot metadata
        g.add((record_iri, SFE.has_snapshot_time, Literal(snapshot_time, datatype=XSD.dateTime)))
        g.add((record_iri, SFE.has_region, Literal(region)))
        g.add((record_iri, SFE.has_category, Literal(category)))
        g.add((record_iri, SFE.has_rank, Literal(rank, datatype=XSD.integer)))

        # Engagement metrics (24h window)
        g.add((record_iri, SFE.has_views_24h, Literal(views_24h, datatype=XSD.integer)))
        g.add((record_iri, SFE.has_likes_24h, Literal(likes_24h, datatype=XSD.integer)))
        g.add((record_iri, SFE.has_comments_24h, Literal(comments_24h, datatype=XSD.integer)))

        # Optional labels (helpful in Gruff)
        if video_title:
            g.add((video_iri, SFE.has_title, Literal(video_title)))
        if channel_name:
            g.add((channel_iri, SFE.has_name, Literal(channel_name)))

    # --- Minimal validation: each Trending_Snapshot_Record must have required properties ---
    required_props = [
        SFE.has_video,
        SFE.has_channel,
        SFE.has_snapshot_time,
        SFE.has_region,
        SFE.has_category,
        SFE.has_rank,
    ]

    bad_records = []
    for rec in g.subjects(RDF.type, SFE.Trending_Snapshot_Record):
        missing = [p for p in required_props if not list(g.objects(rec, p))]
        if missing:
            bad_records.append((rec, missing))

    if bad_records:
        raise ValueError(f"Validation failed for records: {bad_records}")

    return g, input_csv, input_hash


@task
def write_outputs_and_prov(abox_graph: Graph, input_csv: Path, input_hash: str) -> None:
    """
    Task 2: Write the validated ABox as N-Triples, and record PROV-O metadata
    describing this ingestion run and its relationship to the ingested records.
    Then move the input CSV into processed_data.
    """
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")

    run_out_dir = DATA_FOR_GRAPH_DIR / run_id
    run_out_dir.mkdir(parents=True, exist_ok=True)

    # --- 1) Write ABox triples ---
    abox_path = (run_out_dir / "stream_forge_example_abox.nt").resolve()
    abox_nt = abox_graph.serialize(format="nt")
    abox_path.write_text(abox_nt, encoding="utf-8")

    # --- 2) Build PROV graph ---
    prov_graph = Graph()
    prov_graph.bind("prov", PROV)
    prov_graph.bind("sfe", SFE)

    run_iri = SFE[f"Ingestion_Run/{run_id}"]
    input_iri = SFE[f"Input_Batch/{run_id}"]
    output_iri = SFE[f"Output_File/{run_id}"]
    pipeline_iri = SFE["Ingestion_Pipeline"]

    # Harmless Data Product hook (for later DDD/Data Product discussion)
    data_product_iri = SFE["Data_Product/Trending_Videos_Snapshot_Data_Product"]

    # Activity: the ingestion run
    prov_graph.add((run_iri, RDF.type, PROV.Activity))
    prov_graph.add((run_iri, PROV.startedAtTime, Literal(now.isoformat(), datatype=XSD.dateTime)))
    prov_graph.add((run_iri, PROV.endedAtTime, Literal(now.isoformat(), datatype=XSD.dateTime)))
    prov_graph.add((run_iri, PROV.wasAssociatedWith, pipeline_iri))
    prov_graph.add((run_iri, PROV.wasAssociatedWith, data_product_iri))

    # Agent: the ingestion pipeline (SoftwareAgent)
    prov_graph.add((pipeline_iri, RDF.type, PROV.SoftwareAgent))
    prov_graph.add((pipeline_iri, RDFS.label, Literal("Stream_Forge_Example Ingestion Pipeline")))

    # Agent-ish: the Data Product (modeled as Entity)
    prov_graph.add((data_product_iri, RDF.type, PROV.Entity))
    prov_graph.add((data_product_iri, RDFS.label, Literal("Trending Videos Snapshot Data Product")))

    # Entity: input batch (real file path + hash)
    prov_graph.add((input_iri, RDF.type, PROV.Entity))
    prov_graph.add((input_iri, PROV.atLocation, Literal(str(input_csv.resolve()))))
    prov_graph.add((input_iri, PROV.value, Literal(input_hash)))
    prov_graph.add((input_iri, PROV.wasAttributedTo, data_product_iri))
    prov_graph.add((run_iri, PROV.used, input_iri))

    # Entity: output file
    prov_graph.add((output_iri, RDF.type, PROV.Entity))
    prov_graph.add((output_iri, PROV.atLocation, Literal(str(abox_path))))
    prov_graph.add((run_iri, PROV.generated, output_iri))

    # --- 3) Connect ingested records to the ingestion run ---
    for rec in abox_graph.subjects(RDF.type, SFE.Trending_Snapshot_Record):
        prov_graph.add((rec, RDF.type, PROV.Entity))
        prov_graph.add((rec, PROV.wasGeneratedBy, run_iri))
        prov_graph.add((rec, PROV.generatedAtTime, Literal(now.isoformat(), datatype=XSD.dateTime)))
        prov_graph.add((rec, PROV.wasDerivedFrom, input_iri))

    # --- 4) Serialize PROV graph ---
    prov_path = (run_out_dir / "stream_forge_example_meta.nt").resolve()
    prov_nt = prov_graph.serialize(format="nt")
    prov_path.write_text(prov_nt, encoding="utf-8")

    # Move the input file to processed_data (rename with run_id to avoid collisions)
    dest = (PROCESSED_DIR / input_csv.name).with_name(f"{input_csv.stem}_{run_id}{input_csv.suffix}")
    shutil.move(str(input_csv), str(dest))

    print(f"Wrote ABox N-Triples to: {abox_path}")
    print(f"Wrote PROV N-Triples to: {prov_path}")
    print(f"Moved input CSV to: {dest}")


@flow
def stream_forge_example_ingestion_flow():
    """
    Prefect flow: read a CSV from input_data, build a Stream_Forge_Example ABox,
    validate it, and write both ABox and Meta (PROV) as N-Triples.

    Intended to model ingestion of a Data Product snapshot in the Audience Insights bounded context.
    """
    g, input_csv, input_hash = build_and_validate_graph()
    write_outputs_and_prov(g, input_csv, input_hash)


if __name__ == "__main__":
    stream_forge_example_ingestion_flow()
