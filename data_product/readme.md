## Data Product / Catalog Example

This directory contains a **minimal, self-contained example** used throughout the book to illustrate how **Data Products**, **Catalog metadata**, and **Documents** can be modeled and queried as part of a Retrieval-Augmented Generation (RAG) workflow.

The example is intentionally simple and uses a **single default graph**. Named graphs, pipelines, and more advanced deployment patterns are introduced later in the book.

The contents include:

* TBox ontologies for catalogs, data products, and documents
* An ABox example based on the *StreamForge* domain
* A SPARQL update that generates document instances used as the RAG corpus

---

## Ontologies Used

The following describes the various ontologies that were reused and created for this example.

```text
1) dcat.ttl
   The W3C Data Catalog vocabulary.
   This ontology utilizes Dublin Core, SKOS, AND PROV. 

2) Dublin Core Terms
   Dublin Core provides basic metadata properties. Most are annotation properties.
   It has no dependencies

3) Simple Knowledge Organization System (SKOS)
   SKOS is used for meta data and concept organization

4) prov.ttl
   The W3C vocabulary for data provenance.
   Uses SKOS and Dublin Core

5) dp_ontology.ttl
   Defines the Data Product ontology.
   Uses 1-4

6) docs_ontology.ttl
   Defines the Document ontology used for RAG.
   Uses 1-5

7) streamforge_abox.ttl
   ABox data for the StreamForge example domain. Most of the data in the other ontologies is TBox.
   This is mostly ABox. 
   Uses 1-5

5) create_docs_sparql.ru
   Execute this SPARQL UPDATE to create Document
   instances and link them to data products and datasets.
   
```

---



---

