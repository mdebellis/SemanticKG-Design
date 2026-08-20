# Exercise 3-3: Loading the People Ontology into AllegroGraph

**In this exercise, you will learn how to create an AllegroGraph repository, load the People Ontology, generate inferred triples with the AllegroGraph reasoner, and open the resulting Semantic Knowledge Graph in Gruff.**

This exercise assumes that you have access to AllegroGraph as described in the previous exercise and that you have already downloaded the People Ontology to your computer.

If you have not already downloaded it, you can get it from the book's GitHub repository:

[People Ontology](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/people_ontology.ttl)

## Step 1: Log In to AllegroGraph

**Open AllegroGraph and log in using the credentials you created in the previous exercise.**

You should arrive at the main AllegroGraph page. Depending on the environment you are using, you may see several example repositories that are already available.

The [AllegroGraph Documentation](https://franz.com/agraph/support/documentation/index.html) includes additional exercises that use these example repositories and are worth exploring separately.

For this exercise, however, you will create a new repository for the People Ontology.

## Step 2: Create the People Repository

Locate the large button in the upper-right area of the page.

**Click `+ CREATE REPOSITORY`.**

A form for creating a new repository should appear.

In the `Name of new repository` field:

**Enter `People`.**

Leave the remaining options at their default values.

**Click `CREATE & OPEN`.**

AllegroGraph creates the repository and opens its main page.

## Step 3: Open the Data Import Tools

The new repository page provides several ways to populate and work with the repository.

In the panel on the left:

**Select `Add, delete & import data`.**

This option should appear near the top of the panel, below `Query`.

The page should now display a heading similar to:

`Choose action`

with several available operations.

## Step 4: Select RDF File Import

Under `Choose action`:

**Select `Import RDF from an uploaded file`.**

AllegroGraph should display a page headed:

`Select file to import`

Below the heading, you should see an area labeled something similar to:

`Drag-N-Drop an RDF file or click here to select files`

## Step 5: Select the People Ontology

**Click the file-selection area.**

Your operating system's file-selection dialog should appear.

**Navigate to the location where you saved `people_ontology.ttl` and select the file.**

You could also drag the ontology file directly into the upload area if your browser and operating system support drag-and-drop.

## Step 6: Specify Turtle as the RDF Format

Below the file-selection area, locate `Import Options`.

**Expand `Import Options`.**

The RDF format will initially be set to something similar to:

`Format: Auto-detect`

Although AllegroGraph can often determine the RDF syntax automatically, explicitly selecting the format removes any ambiguity.

**Change `Format` from `Auto-detect` to `Turtle`.**

Leave the other import options at their default values.

## Step 7: Verify and Import the Ontology

**Click `VERIFY & IMPORT FILE`.**

AllegroGraph first verifies the RDF and then loads it into the `People` repository.

When the import completes successfully, you should see a confirmation message similar to:

> **Success:** 2319 statements were imported successfully!

✅ The People Ontology is now loaded into AllegroGraph.

> **Note:** The exact statement count can vary if the version of the People Ontology in the repository is updated. The important result is that the import completes successfully without RDF parsing errors.

## Step 8: Open the Reasoning Controls

Next you will generate additional triples that follow from the ontology's axioms.

In the left panel:

**Select `Repository control`.**

Locate the search box within the repository-control page.

It may initially contain a default value such as your user name.

**Enter `Manage reasoning` in the search box.**

As you type, AllegroGraph should display matching options.

**Select `Manage Reasoning`.**

## Step 9: Generate Inferred Triples

Use the reasoning controls to generate the inferred triples for the repository.

After reasoning completes, AllegroGraph should display a success message similar to:

> **Success:** Generated 2901 triples!

These additional triples represent information that AllegroGraph derived from the explicitly asserted RDF statements and the semantic relationships defined in the ontology.

> **Note:** As with the imported-statement count, the exact number of generated triples may change if the ontology or reasoning configuration is updated. A successful reasoning operation is more important than matching the exact number shown here.

✅ The repository now contains both the explicitly loaded information and additional information generated through reasoning.

## Step 10: Open the Repository in Gruff

Now you can explore the resulting Semantic Knowledge Graph visually.

In the left panel, locate the `Gruff` option near the bottom.

**Click `Gruff`.**

AllegroGraph should open the `People` repository in Gruff.

Gruff provides tools for visually exploring graph data and for running SPARQL queries. You will use it extensively in subsequent exercises.

## Exercise Complete

You have now:

* created an AllegroGraph repository named `People`;
* imported the People Ontology in Turtle format;
* generated additional triples using AllegroGraph reasoning; and
* opened the resulting Semantic Knowledge Graph in Gruff.

✅ Your AllegroGraph environment is now ready for the SPARQL and graph-exploration exercises that follow.

