# Exercise Standards for the Online Tutorials



The exercises for *Designing Semantic Knowledge Graphs* are designed to be practical, step-by-step tutorials. The online versions may contain additional explanations, screenshots, examples, and updated instructions that are not included in the printed book.

Because software and user interfaces change over time, these online exercises may also be updated after publication.

## What You Will Learn

Each exercise begins with a short statement describing what you will learn or accomplish.

For example:

**In this exercise, you will learn how to install Protégé and verify that it is working correctly.**

When an exercise requires files, software, or work completed in an earlier exercise, these prerequisites will be identified before the first step.

## Steps

Exercises are divided into numbered steps with descriptive headings.

For example:

### Step 1: Open Protégé

### Step 2: Load the People Ontology

### Step 3: Start the Reasoner

A step should normally represent one meaningful stage of the exercise rather than every individual mouse click.

## User Actions

Actions that you should perform are shown in **bold**.

For example:

**Click `Run Query`.**

**Select `File > Preferences > Renderer`.**

**Enter `Person` in the search field and press Enter.**

Explanatory text is not bold. This makes it easy to scan an exercise and distinguish what you need to **do** from information explaining why you are doing it.

## Menus, Tabs, Buttons, and Other UI Elements

Names of user-interface elements are shown in `inline code`.

Examples include:

* `File`
* `Preferences`
* `Renderer`
* `Run Query`
* `Classes`
* `Active Ontology`

A sequence of menu or dialog selections is written using `>`.

For example:

`File > Preferences > Renderer`

This means:

1. Select `File`.
2. Select `Preferences`.
3. Select the `Renderer` tab or option in the dialog that appears.

The same convention may be used for nested menus and similar navigation paths.

## OWL and RDF Entities

Names of classes, properties, individuals, prefixes, and other ontology entities are shown in `inline code`.

For example:

* Class: `Person`
* Object property: `has_parent`
* Individual: `Albert_Einstein`
* Prefixed name: `foaf:Person`
* Property: `rdf:type`

Full IRIs are also shown in `inline code` when they occur within normal prose:

`https://www.michaeldebellis.com/people/Person`

This distinguishes formal ontology identifiers from ordinary English terms.

## File Names, Paths, Commands, and Values

File names, directory names, paths, commands, parameters, and values that you should enter exactly are shown in `inline code`.

Examples:

* `people.ttl`
* `chapter_1/exercises/`
* `python example.py`
* `localhost:10035`
* `0.75`

Longer commands or groups of commands are displayed in code blocks.

## Code

Programming language and query examples are displayed in fenced code blocks with the appropriate language identifier.

Python:

```python
for person in people:
    print(person)
```

SPARQL:

```sparql
SELECT ?person
WHERE {
    ?person rdf:type :Person .
}
```

Turtle:

```turtle
:Albert_Einstein
    rdf:type :Person ;
    rdfs:label "Albert Einstein" .
```

Other languages and formats, such as JSON, XML, Bash, or Java, use the corresponding code-block format whenever possible.

Short fragments that occur within ordinary sentences use `inline code` instead.

For example:

The triple pattern `?person rdf:type :Person` selects resources that are instances of `Person`.

## Screenshots

Screenshots are used when they make it easier to verify that you are following the exercise correctly.

A screenshot should normally appear **after the action that produces the screen being illustrated**.

The surrounding text should explain what the screenshot demonstrates rather than merely saying "see the following screenshot."

For example:

After loading the ontology, the `Classes` tab should display a hierarchy similar to the following.

*[Screenshot]*

Screenshots do not have to match your display exactly. Differences in operating system, software version, window size, and configuration may cause minor visual differences.

When only one part of the interface matters, screenshots should be cropped or annotated so that the relevant area is easy to identify.

## Expected Results

Whenever it is useful, the exercise describes what you should expect after completing a step.

For example:

**Run the query.**

The results should include `Albert_Einstein`, `Kurt_Godel`, and the predicates that connect them.

For visual tools, the exercise may instead say that your display should look similar to an accompanying screenshot.

Expected results are especially useful after operations that could fail silently or where an incorrect configuration might otherwise become apparent only several steps later.

## Notes, Tips, and Warnings

Supplementary information may be identified as a **Note**, **Tip**, or **Warning**.

> **Note:** Provides useful background or clarification that is not required to complete the step.

> **Tip:** Describes a shortcut, useful technique, or alternative approach.

> **Warning:** Identifies something that could cause an error, data loss, or significant confusion.

These should be used selectively. Information essential to completing the exercise belongs in the main instructions rather than in a note.

## Explaining What the Exercise Is Doing

The exercises are tutorials rather than simple lists of commands. When useful, a short explanation follows an action to describe what happened and why it matters.

For example:

**Run the reasoner.**

Protégé now computes the inferred class hierarchy. Classes that appear under a new superclass may have been placed there because of logical axioms rather than explicit `rdfs:subClassOf` statements.

Explanations should be long enough to help you understand the operation, but short enough that the procedural flow remains easy to follow.

## Links

Links should use descriptive text whenever possible rather than displaying long URLs in the middle of an instruction.

For example:

Download Protégé from the [Protégé website](https://protege.stanford.edu/).

Relative links are preferred for files and resources that are part of this repository.

## Exercise Completion

When useful, an exercise ends with a short statement describing what you have accomplished and how it relates to subsequent exercises.

For example:

You now have Protégé installed and running. In the next exercise, you will install and configure the plugins used in later chapters.

Not every exercise requires a formal summary. The goal is to give you enough confirmation to know that you have successfully completed the exercise.
