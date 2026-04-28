## Data Product / Catalog Example

This directory contains ontologies, knowledge graphs, SPARQL, and Python to develop a Data Catalog example based on the concepts of Data Products and Domain Driven Design (DDD). 

The example is is based on a made-up video streaming company called StreamForge

The Semantic Knowledge Graph is here: https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/knowledge_graph/streamforge_data_catalog_V1.ttl

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
## Additional Directories
There are several sub-directories under this directory. They all have code and text examples that are part of the Semantic Knowledge Graph Data Catalog Streamforge example. Some directories such as REST, graphql, and kafka have various examples of mock interfaces defined for data ports on the data products in the data catalog. For example, the Video_Data_Product has the Query_Port: Video_Metadata_Query. That port has two implementations: one for [GraphQL](https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/graphql/Get_Video_Metadata_GraphQL_Implementation.md), one for [REST/OpenAPI](https://github.com/mdebellis/SemanticKG-Design/blob/main/data_product/REST/Get_Video_Metadata_REST-OpenAPI_Implementation.md). The URLs for those two are saved as part of the different Port Implementations for that Data Product. In an actual Data Catalog, those would be IRIs with the appropriate parameters to the appropriate systems, here they are documents that stand for such external interfaces. 




---

