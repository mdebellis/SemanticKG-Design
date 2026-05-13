## Chapter 9 Files
These files support chapter 9: Implementation. The add_labels.py file contains a simple example of what I call a parameterized SPARQL function. A function that contains a template for a SPARQL
update or query where one or more parts of the query is a string that is passed at run time. In Chapter 3 we saw how we could use SPARQL functions to generate labels that follow underscore for 
blanks pattern and how those updates could be used on a different ontology called Pattern_Examples_No_Labels.ttl simply by changing a string to match the ontology IRI in each update. 
In this chapter we go beyond that and show how to use a Python function that has a string template with the parts of the query that don't change and allows the parts that do change to be passed
at run time to save us the trouble of writing new updates for every namespace IRI. 
