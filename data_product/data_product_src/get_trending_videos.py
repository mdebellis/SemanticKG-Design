import os
import re
from typing import List, Dict, Any, Optional
from franz.openrdf.connect import ag_connect

AGRAPH_PASSWORD = os.getenv("AGRAPH_PASSWORD")
if not AGRAPH_PASSWORD:
    raise RuntimeError(
        "Environment variable AGRAPH_PASSWORD is not set. "
        "Please define it before running this script."
    )

conn = ag_connect(
    "stream_forge_data_catalog",
    host="localhost",
    port=10035,
    user="mdebellis",
    password=AGRAPH_PASSWORD
)

def rdf_int(v) -> int:
    """
    Convert an RDF literal value to int.
    Handles:
      99
      "99"
      "99"^^<http://www.w3.org/2001/XMLSchema#integer>
      99"^^<http://www.w3.org/2001/XMLSchema#integer>   (after a naive strip)
    """
    if isinstance(v, int):
        return v

    s = str(v).strip()

    # If it's N-Triples style typed literal: "99"^^<...>
    if "^^" in s:
        s = s.split("^^", 1)[0]  # keep just the lexical part

    # Remove any remaining quotes
    s = s.strip('"')

    # Final cleanup: keep leading sign + digits only
    m = re.match(r"^-?\d+", s)
    if not m:
        raise ValueError(f"Cannot parse integer from RDF literal: {v!r} (as {s!r})")
    return int(m.group(0))


def get_trending_videos(conn, n: int = 5) -> List[Dict[str, Any]]:
    """
    Implementation of the StreamForge analytic port Get_Trending_Videos.
    Returns top N videos ordered by sf:trend_score (descending).
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

    query = f"""
    PREFIX sf:   <https://www.michaeldebellis.com/streamforge/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

    SELECT ?video ?label ?scoreInt ?playsInt
    WHERE {{
      ?video a sf:Video ;
             sf:trend_score ?score ;
             sf:play_count_24h ?plays .
      OPTIONAL {{ ?video rdfs:label ?label }}

      BIND(xsd:integer(?score) AS ?scoreInt)
      BIND(xsd:integer(?plays) AS ?playsInt)
    }}
    ORDER BY DESC(?scoreInt)
    LIMIT {n}
    """

    # Execute query (handle common AG client patterns)
    if hasattr(conn, "executeTupleQuery"):
        rows = conn.executeTupleQuery(query)
    else:
        tq = conn.prepareTupleQuery(query)
        rows = tq.evaluate()

    results: List[Dict[str, Any]] = []

    for row in rows:
        # Dict-like row
        if isinstance(row, dict):
            video = str(row["video"])
            label = str(row["label"]) if row.get("label") is not None else None
            score = rdf_int(score_val)
            plays = rdf_int(plays_val)

        # Binding-set style row
        else:
            video_val = row.getValue("video")
            label_val = row.getValue("label")
            score_val = row.getValue("scoreInt")
            plays_val = row.getValue("playsInt")

            video = str(video_val)
            label = str(label_val) if label_val is not None else None
            score = rdf_int(score_val)
            plays = rdf_int(plays_val)

        results.append(
            {"video": video, "label": label, "score": score, "plays_24h": plays}
        )

    return results


if __name__ == "__main__":
    top5 = get_trending_videos(conn, n=5)
    for item in top5:
        print(item["score"], item["plays_24h"], item["label"], item["video"])
