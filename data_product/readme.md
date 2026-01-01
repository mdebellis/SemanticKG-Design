## Data Product / Catalog Example

This directory contains a **minimal, self-contained example** used throughout the book to illustrate how **Data Products**, **Catalog metadata**, and **Documents** can be modeled and queried as part of a Retrieval-Augmented Generation (RAG) workflow.

The example is intentionally simple and uses a **single default graph**. Named graphs, pipelines, and more advanced deployment patterns are introduced later in the book.

The contents include:

* TBox ontologies for catalogs, data products, and documents
* An ABox example based on the *StreamForge* domain
* A SPARQL update that generates document instances used as the RAG corpus

---

## Loading Order

Load all files into the **default graph**, then run the reasoner if your environment supports it.

```text
1) dcat.ttl
   The W3C Data Catalog vocabulary.
   This ontology has no dependencies.

2) dp_ontology.ttl
   Defines the Data Product ontology.
   May reference entities defined in DCAT.

3) docs_ontology.ttl
   Defines the Document ontology used for RAG.
   May reference entities defined in the Data Product ontology.

4) streamforge_abox.ttl
   ABox data for the StreamForge example domain
   (datasets, data products, organizations, etc.).

5) create_docs_sparql.ru
   Execute this SPARQL UPDATE to create Document
   instances and link them to data products and datasets.
   
6) Run the reasoner. 
```

---

## Notes
* Baseline StreamForge Data Product / Catalog RAG example. All data in default graph. Docs generated via create_docs_sparql.ru.
After Loading and Running MaterializerVerified counts:
- ABox triples: 3849
- docs:Document instances: 3
- linked to core data products: 3
* All data is loaded into the **default graph** for clarity and ease of understanding.
* The SPARQL update generates the document instances used by the RAG examples in later chapters.
* Additional examples (e.g., data pipelines, trending analytics, named graphs) are intentionally kept separate to avoid conflating concerns.

---

