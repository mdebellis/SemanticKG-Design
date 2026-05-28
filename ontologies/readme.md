# People Ontology and Basic Reusable Ontology (BRO)
This directory holds the [People Ontology](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/people_ontology.ttl) and the [Basic Reusable Ontology](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/Basic_Reusable_Ontology.ttl). It also has different versions of the People Ontology to demonstrate different kinds of errors and changes. 
The Widoco dodumentation for the People Ontology can be found at: [People Ontology Documentation](https://mdebellis.github.io/SemanticKG-Design/peopleOntology/)

## People Ontology with Patterns
The [people_ontology_w_patterns.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/people_ontology_w_patterns.ttl) is a version of the ontology after I added the n-ary relation pattern (see Chapter 7 in the book) so that we can model that Von Neuman had more than one job.

## People Ontology with Syntax Error
The [people_ontology_syntax_error.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/people_ontology_syntax_error.ttl) is an example of an ontology I created to illustreate how to debug syntax errors in Protege. The relevant "tip" page that uses this version
(which is designed to cause a parsing error in Protege) can be found here: [Tip: Debugging Protege Parsing Errors](https://github.com/mdebellis/SemanticKG-Design/wiki/Debugging-Parsing-Errors-in-Prot%C3%A9g%C3%A9) 

## People Ontology with Test Data
The [people_ontology_test_data.ttl](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/people_ontology_test_data.ttl) is an ontology I saved with test data generated for me by ChatGPT. See the section: *Using an LLM to Define Test Data Instances* near the end of Chapter 7. If you load this ontology into Protégé and run the reasoner you will see an error. In fact there are (by design) three errors. Sometimes if there is more than one error, the Protégé reasoner can't be of much help, but they've been getting better. In this case when you run the reasoner it will point you to one error that you can fix, then run again and fix the second and then the third.  

## Basic Reusable Ontology
The [Basic Reusable Ontology](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/Basic_Reusable_Ontology.ttl) is a collection of metadata properties (and a few classes) from PROV, SULO, Dublin Core, and SKOS. More on that can be found here: 
[Basic Reusable Ontology GitHub Repository](https://github.com/mdebellis/Basic_Reusable_Ontology)
