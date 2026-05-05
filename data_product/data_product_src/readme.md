# Python Functions to Generate Embedding Notes

This directory contains the Python code and additional files used for the **StreamForge Data Catalog** examples in the book.


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



---


