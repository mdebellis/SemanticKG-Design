# StreamForge Data Catalog Knowledge Graph

This directory contains the core knowledge graph used throughout the **StreamForge Data Catalog** examples in the book.

## File Overview

### `streamforge_data_catalog_V1.ttl`

This is the **canonical version** of the knowledge graph.

- ✔ Contains only **asserted triples**
- ✔ Designed for use in both **Protégé** and **AllegroGraph**
- ❌ Does **not** include materialized inferences

---

## How to Use This Knowledge Graph

### Option 1: View and Explore in Protégé

If your goal is to explore the ontology and data:

1. Open `streamforge_data_catalog_V1.ttl` in **Protégé**
2. Enable a reasoner (e.g., Pellet) if you want to view inferred relationships
3. Use the class hierarchy and individuals tabs to browse the model

This is the recommended approach for understanding the structure of the ontology and knowledge graph.

---

### Option 2: Use with AllegroGraph (Graph RAG)

If your goal is to run the **Graph RAG examples**:

1. Load `streamforge_data_catalog_V1.ttl` into an AllegroGraph repository
2. Run the **Materializer** to generate inferred triples
3. Proceed with:
   - Embedding generation
   - Vector database creation
   - ChatState / RAG queries

> ⚠️ **Important:**  
> The Graph RAG examples assume that inferred triples have been materialized.  
> If you skip this step, some queries and retrieval results may be incomplete.

---

## Why Materialized Triples Are Not Included

This repository intentionally avoids storing materialized inferences because:

- They can significantly increase file size
- They introduce redundancy (inferred triples can always be recomputed)
- They can clutter ontology views in tools like Protégé
- They depend on the specific reasoning configuration used

Instead, this project follows a **clean separation**:

- **Ontology + asserted data** → stored in the repository  
- **Inferred data** → generated as needed in the runtime environment  

---

## Notes for Advanced Users

- The ontology uses OWL reasoning patterns (e.g., subclass hierarchies, transitive properties) that are leveraged during materialization
- Some downstream processes (e.g., embedding generation and RAG retrieval) benefit from having these inferences explicitly present
- If you modify the ontology, you should re-run the materializer before regenerating embeddings

---

## Related Directories

- `../data_product_src/` — Python scripts for embedding generation and processing
- `../ontologies/` — Core ontology definitions used by the knowledge graph

---

## Summary

| Use Case                | Recommended Approach                          |
|------------------------|-----------------------------------------------|
| Learn the ontology     | Open in Protégé                               |
| Run Graph RAG          | Load into AllegroGraph + run Materializer     |
| Modify the model       | Edit TTL → re-materialize → regenerate embeddings |

---

This design keeps the repository simple, consistent, and aligned with real-world Semantic Knowledge Graph workflows.
