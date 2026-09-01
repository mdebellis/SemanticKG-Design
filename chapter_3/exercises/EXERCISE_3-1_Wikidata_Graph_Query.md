# Exercise 3-1: Exploring Linked Data and SPARQL with Wikidata

`EXERCISE_3-1_Exploring_Linked_Data_and_SPARQL_with_Wikidata.md`

**In this exercise, you will learn how to use the Wikidata Query Service as a SPARQL endpoint, run and modify SPARQL queries, explore Linked Data, and display query results as tables, maps, and interactive graphs.**

Wikidata provides one of the most useful public examples of Linked Data and a SPARQL endpoint.

A **SPARQL endpoint** is a web service that accepts SPARQL queries and returns results from a knowledge graph. SPARQL can also use the `SERVICE` keyword to combine information from a local knowledge graph with information obtained from remote SPARQL endpoints.

This makes Linked Data especially powerful: rather than treating each knowledge graph as an isolated database, applications can query data distributed across multiple graphs.

For this exercise, you will work directly with the Wikidata Query Service.

You can also find the queries used in this exercise in the book's GitHub repository:

[Wikidata SPARQL Queries](https://github.com/mdebellis/SemanticKG-Design/blob/main/chapter_3/Wikidata_SPARQL_Queries.rqtxt)

## Step 1: Open the Wikidata Query Service

Open the [Wikidata Query Service](https://query.wikidata.org/).

The upper part of the page contains a SPARQL query editor. Results appear below the editor after a query runs.

To execute a query:

**Paste the query into the query editor and click the ▶ Run button.**

You will use this same process for each of the following examples.

---

## Step 2: Find People Born in New York City

The first query finds humans recorded in Wikidata as having been born in New York City.

It also finds people whose birthplace is represented more specifically—for example, as a hospital or borough contained within New York City.

**Copy the following query into the Wikidata Query Service and run it:**

```sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>

# Humans born in New York City
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?sitelinks
WHERE {
    ?item wdt:P31 wd:Q5;
          wdt:P19/wdt:P131* wd:Q60;
          wikibase:sitelinks ?sitelinks.

    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en"
    }
}
ORDER BY DESC(?sitelinks)
```

The results include:

* `?item` — the Wikidata entity for each person
* `?itemLabel` — the human-readable name
* `?itemDescription` — a short description
* `?sitelinks` — the number of Wikipedia language editions that contain pages associated with the item

The results are sorted by number of sitelinks, which provides a rough indication of how widely referenced the person is.

## Step 3: Examine the SELECT Clause

Look at the first part of the query:

```sparql
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?sitelinks
```

The `SELECT` clause identifies the variables that should be returned.

The `DISTINCT` keyword removes duplicate solutions from the result set. This is often useful in SPARQL because different graph paths can sometimes produce identical result rows.

## Step 4: Identify Humans

Now look at the beginning of the `WHERE` clause:

```sparql
?item wdt:P31 wd:Q5;
```

In Wikidata:

* `wdt:P31` means **instance of**
* `wd:Q5` identifies **human**

This pattern therefore says:

> Find an `?item` that is an instance of human.

Wikidata frequently uses identifiers such as `P31`, `Q5`, and `Q60` rather than descriptive names in its IRIs. These are examples of **opaque identifiers**.

## Step 5: Follow the Birthplace Property Path

The next part is more interesting:

```sparql
wdt:P19/wdt:P131* wd:Q60;
```

Here:

* `wdt:P19` means **place of birth**
* `wdt:P131` means **located in the administrative territorial entity**
* `wd:Q60` identifies **New York City**

The `/` combines properties into a **property path**.

The `*` means **zero or more occurrences** of the preceding property.

The query can therefore match both:

* a person whose birthplace is directly recorded as New York City, and
* a person whose birthplace is a more specific location that is contained within New York City through one or more administrative relationships.

For example, a birthplace might be a hospital that is located within a borough that is part of New York City.

This illustrates an important advantage of graph queries: the query can follow relationships rather than requiring every value to be represented at exactly the same level of detail.

## Step 6: Retrieve and Sort by Sitelinks

The next statement is:

```sparql
wikibase:sitelinks ?sitelinks.
```

This retrieves the number of Wikipedia sitelinks associated with each Wikidata item.

The query ends with:

```sparql
ORDER BY DESC(?sitelinks)
```

This sorts the results from the largest number of sitelinks to the smallest.

As a result, widely referenced people tend to appear near the top.

## Step 7: Examine the Wikidata Label Service

The query also contains:

```sparql
SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en"
}
```

The SPARQL `SERVICE` keyword normally allows one query to retrieve information from another SPARQL service.

Wikidata also provides several built-in services. `wikibase:label` is one of them.

It automatically retrieves readable labels and descriptions for Wikidata entities.

The language specification:

```text
[AUTO_LANGUAGE],mul,en
```

tells Wikidata to try:

1. the language associated with the current interface or query context,
2. multilingual labels,
3. English as a fallback.

> **Note:** `wikibase:label` behaves like a SPARQL service, but it is a special feature provided by the Wikidata Query Service rather than an independent remote SPARQL endpoint.

---

## Step 8: Find Nobel Prize Winners in Physics

Now use Wikidata to retrieve Nobel Prize winners in Physics, along with their birthplaces and links to their English-language Wikipedia pages.

**Replace the previous query with the following query and run it:**

```sparql
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>

SELECT ?winner ?winnerLabel ?birthPlace ?birthPlaceLabel ?wikiPage
WHERE {
    ?winner wdt:P166 wd:Q38104;
            wdt:P19 ?birthPlace.

    OPTIONAL {
        ?wikiPage schema:about ?winner;
                  schema:inLanguage "en";
                  schema:isPartOf <https://en.wikipedia.org/>.
    }

    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en".
    }
}
ORDER BY ?winnerLabel
LIMIT 50
```

The query returns:

* the Wikidata entity for the winner
* the winner's name
* the winner's birthplace
* the human-readable name of the birthplace
* an English-language Wikipedia page, when one is available

The results are sorted alphabetically by the winner's name and limited to 50 rows.

## Step 9: Examine OPTIONAL

Look at this part of the query:

```sparql
OPTIONAL {
    ?wikiPage schema:about ?winner;
              schema:inLanguage "en";
              schema:isPartOf <https://en.wikipedia.org/>.
}
```

This attempts to retrieve an English-language Wikipedia page for each Nobel laureate.

The `OPTIONAL` keyword is important.

Without `OPTIONAL`, a Nobel laureate would appear in the results only if all of these Wikipedia-related triples existed.

With `OPTIONAL`, the laureate can still appear even if Wikidata cannot provide an English Wikipedia page.

This is a common SPARQL pattern:

> Use `OPTIONAL` when information is useful if available, but its absence should not eliminate the resource from the results.

## Step 10: Examine the schema.org Vocabulary

The Wikipedia portion of the query uses the schema.org vocabulary:

```sparql
schema:about ?winner;
schema:inLanguage "en";
schema:isPartOf <https://en.wikipedia.org/>.
```

These statements specify that:

* `schema:about ?winner` — the page is about the Wikidata entity
* `schema:inLanguage "en"` — the page is in English
* `schema:isPartOf <https://en.wikipedia.org/>` — the page is part of English Wikipedia

schema.org is a widely used vocabulary for representing structured information on the Web.

It is a good example of the original Semantic Web idea: independently developed websites and systems can use common vocabularies to make their data easier for software to understand and integrate.

In this query, schema.org connects structured Wikidata information with human-readable Wikipedia content.

---

## Step 11: Display Hospitals on a World Map

Wikidata can display query results in formats other than tables.

The next query finds hospitals around the world that have geographic coordinates and displays them on a map.

**Run the following query:**

```sparql
# Map of hospitals across the world
#defaultView:Map

SELECT DISTINCT *
WHERE {
    ?item wdt:P31/wdt:P279* wd:Q16917;
          wdt:P625 ?geo.
}
```

Instead of the normal table, the results should appear as a map.

At the initial zoom level, many markers may overlap and appear as large concentrations of color.

**Zoom in on the map using your mouse wheel or the available zoom controls.**

Continue zooming until you reach the state, province, or city level.

**Select individual map markers to inspect specific hospitals.**

💡 You may find the map easier to explore by using the full-screen control associated with the results.

## Step 12: Understand the Map View

The line:

```sparql
#defaultView:Map
```

looks like a SPARQL comment, but the Wikidata Query Service interprets it specially.

It is sometimes referred to as a **magic comment**.

It tells Wikidata to display the query results using its Map View instead of the default table.

This instruction is not part of the SPARQL standard. It is a feature of the Wikidata Query Service.

The map works because the query retrieves geographic coordinates:

```sparql
wdt:P625 ?geo.
```

`wdt:P625` is the Wikidata property for geographic coordinates.

## Step 13: Examine the Hospital Property Path

The other important part of the query is:

```sparql
?item wdt:P31/wdt:P279* wd:Q16917;
```

Here:

* `wdt:P31` means **instance of**
* `wdt:P279` means **subclass of**
* `wd:Q16917` identifies **hospital**

The expression:

```sparql
wdt:P31/wdt:P279*
```

allows the query to find not only resources directly typed as hospitals but also resources typed as more specialized kinds of hospitals.

For example, it can follow subclass relationships involving categories such as:

* children's hospitals
* military hospitals
* teaching hospitals

The `*` means that SPARQL can follow zero or more `subclass of` relationships.

> **Note:** In an OWL environment with the relevant subclass relationships available to a reasoner, transitive subclass inference can provide similar information without requiring every level of the hierarchy to be traversed explicitly in the query.

---

## Step 14: Explore Ada Lovelace Using the Graph View

For the final example, you will use another Wikidata visualization: the Graph View.

This query begins with Ada Lovelace and retrieves relationships to other Wikidata resources.

**Run the following query:**

```sparql
# Use the graph view to view people and concepts related to Ada Lovelace
#defaultView:Graph

SELECT ?item ?itemLabel ?itemImage ?value ?valueLabel ?valueImage ?edgeLabel
WHERE {
    BIND(wd:Q7259 AS ?item)  # Ada Lovelace

    ?item ?wdt ?value.

    ?edge a wikibase:Property;
          wikibase:propertyType wikibase:WikibaseItem;
          wikibase:directClaim ?wdt.

    OPTIONAL {
        ?item wdt:P18 ?itemImage.
    }

    OPTIONAL {
        ?value wdt:P18 ?valueImage.
    }

    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en".
    }
}
```

The line:

```sparql
#defaultView:Graph
```

tells Wikidata to display the results as an interactive graph.

The line:

```sparql
BIND(wd:Q7259 AS ?item)
```

sets the starting entity to Ada Lovelace.

`Q7259` is Ada Lovelace's Wikidata identifier, or **Q-ID**.

After the query runs:

**Scroll to the Graph View.**

**Move the mouse over or select nodes in the graph to explore the related entities.**

The graph lets you visually explore relationships between Ada Lovelace and people, concepts, organizations, places, and other Wikidata resources.

---

## Step 15: Find a Different Wikidata Q-ID

You can reuse the same Graph View query for almost any person or concept represented in Wikidata.

Open [Wikidata](https://www.wikidata.org/).

**Enter the name of a person or concept in the search box.**

For example, you might search for:

* Alan Turing
* Taylor Swift
* quantum computing
* a scientist
* an artist
* a city
* a technology

**Select the result that represents the specific entity you want to explore.**

The URL for a Wikidata entity will contain a Q-ID similar to:

```text
https://www.wikidata.org/wiki/Q7251
```

In this example:

```text
Q7251
```

is the Q-ID.

> **Tip:** Search results may include several related entries. Make sure you select the Wikidata item for the actual person or concept you want rather than an article or another entity that merely refers to it.

## Step 16: Modify the Graph Query

Return to the Graph View query in the Wikidata Query Service.

Find this line:

```sparql
BIND(wd:Q7259 AS ?item)
```

**Replace `Q7259` with the Q-ID you found.**

For example:

```sparql
BIND(wd:QXXXXXX AS ?item)
```

where `QXXXXXX` is your chosen Wikidata identifier.

**Run the modified query.**

**Explore the resulting graph.**

Try selecting and examining several of the related nodes.

✅ You have now modified an existing SPARQL query to explore a Wikidata entity of your own choosing.

## Exercise Complete

In this exercise, you used the Wikidata Query Service to explore several important capabilities of SPARQL and Linked Data.

You:

* queried a public SPARQL endpoint;
* used Wikidata identifiers and properties;
* followed relationships with SPARQL property paths;
* removed duplicate results with `DISTINCT`;
* enriched results with the Wikidata label service;
* used `OPTIONAL` to retrieve information that may not exist for every resource;
* used schema.org to connect Wikidata entities with Wikipedia pages;
* displayed geographic data using Wikidata's Map View;
* displayed relationships using Wikidata's Graph View; and
* modified a query to explore an entity of your own choosing.

These examples illustrate an important idea behind Linked Data: a Semantic Knowledge Graph does not have to be limited to the information stored locally. SPARQL endpoints make it possible to query and integrate information from knowledge graphs distributed across the Web.

