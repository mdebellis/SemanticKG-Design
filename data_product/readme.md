## Data Product / Catalog Example

This directory contains ontologies, knowledge graphs, SPARQL, and Python to develop a Data Catalog example based on the concepts of Data Products and Domain Driven Design (DDD). 

The example is is based on a made-up video streaming company called StreamForge

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

