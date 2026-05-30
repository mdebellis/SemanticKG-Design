# StreamForge Data Catalog Knowledge Graph

This directory contains the core knowledge graph used throughout the **StreamForge Data Catalog** examples in the book.

## File Overview

### `streamforge_data_catalog_V1.ttl`

This is the **canonical version** of the knowledge graph.

- ✔ Contains only **asserted triples**
- ✔ Designed for use in both **Protégé** and **AllegroGraph**
- ❌ Does **not** include materialized inferences
- ❌ Does **not** include embedding notes

### `streamforge_data_catalog_V1_w_embedding-notes.ttl`

- ✔ Identical to `streamforge_data_catalog_V1.ttl` except
- ✔ Does include materialized inferences
- ✔ Does include embedding_notes
---
## Embedding Notes and Labels

What are `embedding_notes`? you may be asking. Good question. When using a knowledge graph to store the documents in a RAG Corpus there is a great deal of information in the knowledge graph itself that is not available to the LLM. Even when adding `skos:definition` strings and creating vectors for such strings, this is still not ideal because if class Foo has a skos:definition that says "This class must be used with the Bar class for all Foo Bar tasks" the string may not be clear to the LLM. The user browsing the graph knows that the string is associated with class Foo but the LLM doesn't. Hence, embedding_notes are notes that are generated specifically to communicate the information in the knowledge graph to the LLM. 

There are two Python functions: 

`https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/data_product_src/add_embedding_notes_from_classes.py` 

and 

`https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/data_product_src/add_embedding_notes_from_properties.py`

The first function uses the file:

`https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/data_product_src/embedding_classes.txt` 

to determine which classes to generate embedding notes for. That file has the QName (the last part of the IRI with a prefix) for each class that needs a note. For each class in that file the function adds data about which classes are sub and super classes. For each instance of that class it adds to the embedding note a sentence that the instance is an instance of that class. E.g., for `prov:Person` it adds:
"Person is a subclass of Agent" and for each instance of `prov:Person` it adds strings like:
"Security Engineer 1 is an instance of Person". 

The second function uses: 

`https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/data_product_src/embedding_properties.txt`

For each property in that file it finds all the triples that have that property for a predicate and adds: {Subject Label} {Property Label} {Object Label} 
e.g., for the property `dp:has_skill` it adds the string: "Security Engineer 1 has skill GDPR Review" to `Security_Engineer_1`. If the triple has a literal value, then the string of that literal is used. 

There is also a property: `dp:embedding_label`. This is required for properties from DCAT and ODRL that don't follow the standard of "has property" or "is property of". We don't want to deviate from the standard so we don't want to change those labels. For any property that doesn't have a label that yields an intuitive string we create a `dp:embedding_label`. The function checks for a `dp:embedding_label` first and if no such label exists, then it falls back to ther `rdfs:label`, `skos:altLabel`, or `skos:prefLabel`.

## How to Use These Knowledge Graphs

### Option 1: View and Explore in Protégé

If your goal is to explore the ontology and data:

1. Open `streamforge_data_catalog_V1.ttl` in **Protégé**
2. Enable a reasoner (e.g., Pellet) if you want to view inferred relationships
3. Use the class hierarchy and individuals tabs to browse the model

This is the recommended approach for understanding the structure of the ontology and knowledge graph.

---

### Option 2: Use with AllegroGraph (Graph RAG)

If your goal is to run the **Graph RAG examples**:

1. Load `streamforge_data_catalog_V1_w_embedding-notes.ttl` into an AllegroGraph repository
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
