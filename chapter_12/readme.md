## Files for Chapter 12 Semi-Formal Modeling

This directory contains ontologies and SPARQL queries that support Chapter 12. This chapter focuses on Information Architecture and what I call semi-formal models, models such as Glossaries, Taxnomies, and Folksonomies. 

This chapter is based on the ideas from Jessica Talisman's article [The Ontology Pipleine](https://jessicatalisman.substack.com/p/the-ontology-pipeline). The core idea being that semiformal models
can be a way to develop ontologies by first creating models that have some formal structure but don't require the depth or rigor of an OWL ontology. One of the best tools to implement this idea is
the Simple Knowledge Organization System (SKOS). SKOS is one of the first and most used W3C ontology vocabularies. It is deliberately general using classes such as Concept and properties such as broader/narrower.
Broader/narrower models the general relation of more/less abstract concepts. This allows users to first focus on models that are easy to develop and focus on understandability over formal rigor. Such
models are highly valuable artifacts in themselves and also can be a starting point for more elaborate domain model ontologies. 

The primary example is a consulting taxonomy organization structure taxonomy. Organization taxonomies are one of the most common examples in Information Architecture because they illustrate how hierarchies
that don't conform to one formal model such as subclasses or sub-parts can be highly intuitive and help give someone an imddediate understanding of the basic structure of complex organizations. 

---

## Ontologies and SPARQL Files

The following describes the various ontologies that were reused and created for this example.

1) [consulting_skos_taxonomy.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/chapter_12/consulting_skos_taxonomy.ttl)  This is the initial consulting taxonomy.  
2) [consulting_semantic_taxonomy.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/chapter_12/consulting_semantic_taxonomy.ttl) This is the first evolution of the taxonomy in 1. In this version I use SPARQL queries to transform the broader/narrower hierarchy into the appropriate kind of
formal model. In some cases subclasses, in others sub-parts, and some are special domain specific relations for the consulting domain. 
3) [consulting_ontology.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/chapter_12/consulting_ontology.ttl) This is the second evolution. It takes the model in 2 and transforms it into a complete ontology with classes, subclasses, properties, and axioms.
4) [taxonomy_skos_transformations.sparql](https://github.com/mdebellis/SemanticKG-Design/blob/main/chapter_12/taxonomy_skos_transformations.sparql) These are the SPARQL transformations I used to automate the evolution of the model from 1 to 2 and then to 3.
5) [glossary-skos-imports.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/chapter_12/glossary-skos-imports.ttl)  This is a SKOS version of the book's [glossary](https://github.com/mdebellis/SemanticKG-Design/wiki/Glossary). I didn't discuss this in the chapter but created it as
   another example of an actual informal model created from a text document. 

---

