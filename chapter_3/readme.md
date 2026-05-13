## Supporting Files for Chapter 3
The files in this directory support chapter 3. The files with labels that include "SPARQL" are collections of SPARQL listings in that chapter. The standard I use is that files that 
contain only SPARQL updates (SPARQL that adds and/or deletes triples) end in ".ru". Files that only contain queries end in ".rq". Files that contain both updates and queries end in ".sparql". 
This isn't a universal standard, but it is what I most typically see at clients. The file Pattern_Examples_No_Labels.ttl is provided to allow the reader to load the file into Protégé and then use the
SPARQL_Label_Generation_Updates in Snap SPARQL to add labels. The specific ontology is not important. It is work in progress. I began to define some of the patterns in Fowler's Analysis Patterns book
but didn't get very far with it. The point of the file is to give the user an ontology with classes, properties, etc. that don't have labels. Remember, if you use user generated IRIs in Protégé
then Protégé will not generate labels for you. However, as long as you follow the standard of using underscores where there would be blanks you can apply the transformations and generate the labels. 
I encourage the reader to begin with the file used to generate labels for the People Ontology: SPARQL_Label_Generation_Updates_People.ru and make the trivial changes to the string matched in each update
from 'people/' to 'pattern_examples/'. However, for those who don't wish to, they can simply use the SPARQL_Label_Generation_Updates_Patterns.ru and run each one in Snap SPARQL in the patterns ontology. 
The change is subtle but you will see that some entities with underscores now have spaces. In future chapters we'll expand on these by showing how to write a Python funciton that takes the pattern to match as an input and runs all the SPARQL updates at once (Chapter 9)
a parameter so that we don't need to create new files with minor variations of each SPARQL update for every new namespace. 
