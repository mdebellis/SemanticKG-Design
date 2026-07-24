# Semantic Knowledge Graph Design
For ontology, code and other supporting examples and tools for the book: Designing Semantic Knowledge Graphs: A Guide to Utilizing Semantic Web Technologies for Agile Data Management. This doesn't follow typical standards where all code is under an src directory. The book has several examples of OWL, SHACL, SPARQL, SWRL, and Python. I decided to create a directory for each chapter that has code in it and place the code from that chapter into the corresponding directory. I also have an ontologies directory and a data_product directory. Note that many of the sub-directories also have their own README file, with specific details about the files in that directory. For example: [Verify Directory README](https://github.com/mdebellis/SemanticKG-Design/blob/main/tests/verify/README.md)
# Ontologies
Ontologies can be stored in two types of directories:
1. In a special directory. There are two of these: [Ontologies](https://github.com/mdebellis/SemanticKG-Design/tree/main/ontologies) and [data_product/knowledge_graph](https://github.com/mdebellis/SemanticKG-Design/tree/main/data_product/knowledge_graph) The ontologies directory is for ontologies such as the people_ontology that are used in many chapters. The data_product/knowledge_graph contains the Data Product Knowledge graph which is referenced in chapters 12 and 14.
2. In specific chapter directories. To make thing easier for users I sometimes have duplicates of an ontlogy stored both in the specific directory for the chapter as well as in one of the directories above. This is also true for a small number of SPARQL files. The idea is that the user will already have navigated to that directory when reading the chapter so that when they go to open a new file, chances are good they will be in that directory so having a copy there makes it easier for them to find the file. 

## License
This work is licensed under the [Creative Commons Attribution 4.0 International (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/) license. 
You are free to share and adapt the content as long as you provide proper attribution.
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

When using or adapting this content, please include attribution as follows:
"Based on work by Michael DeBellis, available at [https://github.com/mdebellis/SemanticKG-Design)](https://github.com/mdebellis/SemanticKG-Design)."




