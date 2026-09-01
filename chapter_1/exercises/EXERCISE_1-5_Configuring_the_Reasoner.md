# Exercise 1-5: Configuring the Reasoner

**In this exercise, you will learn how to load an ontology into Protégé, configure the reasoner to display all available inferences, and verify that Pellet is working correctly.**

You will use the People Ontology from the book’s GitHub repository to test the reasoner.

## Step 1: Download the People Ontology

Open the [People Ontology on GitHub](https://github.com/mdebellis/SemanticKG-Design/blob/main/ontologies/people_ontology.ttl).

If you are familiar with GitHub, you may prefer to clone the entire repository. Otherwise, you can simply download files as you need them.

**Download `people_ontology.ttl` to your computer.**

## Step 2: Open the Ontology in Protégé

Start Protégé if it is not already running.

**Select `File > Open`.**

Navigate to the location where you saved `people_ontology.ttl`.

**Select the file and open it.**

Protégé should load the People Ontology.

## Step 3: Configure the Displayed Inferences

OWL reasoners can calculate several different kinds of inferences. Some are not displayed by default because calculating them can take significant time for large ontologies.

The ontologies used in these introductory exercises are small, so you can enable all available inference types.

**Select `Reasoner > Configure`.**

A configuration dialog should appear with two Tabs.

**Select the `Displayed Inferences` Tab if it is not already selected.**

**Select every available inference option.**

Protégé may warn you that some inference types can take additional time to calculate. That should not be a concern for the small ontologies used in these exercises.

**Click `OK`.**

## Step 4: Select Pellet as the Reasoner

**Open the `Reasoner` menu again.**

A black dot should appear next to the currently selected reasoner.

**Verify that the black dot appears next to `Pellet`.**

If another reasoner is selected:

**Click `Pellet` to make it the active reasoner.**

## Step 5: Start the Reasoner

**Select `Reasoner > Start reasoner`.**

After Pellet finishes processing the ontology, look at the lower-right corner of the Protégé window.

You should see:

`Reasoner Active`

You should also see the `Show Inferences` option selected.

✅ The reasoner is now active and synchronized with the ontology.

## Step 6: Examine Inferred Information

**Select the `Individuals by class` Tab.**

In the class hierarchy:

**Expand `Agent`.**

**Select `Person`.**

The View below the class hierarchy should display several individuals that are instances of `Person`.

**Select `Mary Doe`.**

Your Protégé interface should look similar to the following:

<img width="2006" height="1778" alt="Chapter1_People_Ontology" src="https://github.com/user-attachments/assets/504309fc-e074-473b-be35-fa588887c2f7" />

Notice that several values are highlighted in yellow.

These values are not explicitly asserted in the ontology. They have been **inferred by the reasoner** from the axioms and rules defined in the ontology.

This is one of the key capabilities of OWL: information can be derived logically from information that is explicitly represented.

## Step 7: Synchronize the Reasoner After Changes

Whenever you load an ontology or make a change that could affect inferences, the message in the lower-right corner of Protégé may change to:

`Reasoner state out of sync with active ontology`

This means that the ontology has changed since the last time the reasoner ran.

**Select `Reasoner > Synchronize reasoner`.**

When synchronization is complete, the status should return to:

`Reasoner Active`

For the exercises in this book, especially while you are learning Protégé, it is a good practice to synchronize the reasoner after almost every change that could produce new inferences.

There are three important reasons for doing this:

1. **You see new inferences immediately.**
   Changes to the ontology may cause the reasoner to derive additional facts. You will not see those new inferences until the reasoner is synchronized.

2. **The ontologies used in introductory exercises are small.**
   Synchronizing the reasoner is usually very fast.

3. **You can identify inconsistencies quickly.**
   If a change makes the ontology inconsistent, running the reasoner immediately makes it much easier to identify which change caused the problem.

If you make many changes before running the reasoner, several inconsistencies may be introduced at once. Diagnosing the source of the problem can then be considerably more difficult.

> **Note:** Changes involving only Annotation Property values generally do not affect logical reasoning because Annotation Properties are not interpreted by the OWL reasoner.

## Tip: Use Protégé Auto-Completion

Protégé supports auto-completion when you enter entity names.

Type the first few characters of an entity name and then press:

`Ctrl + Space`

If the characters uniquely identify an entity, Protégé completes the name automatically.

If several entities match, Protégé displays a list of possible choices.

For example:

**Type `ha` and press `Ctrl + Space`.**

Protégé may display properties whose names begin with `has`.

This can save typing and reduce errors.

If the ontology uses labels, begin by typing a quotation mark and then use `Ctrl + Space` to search using labels.

## Tip: Use the Search Tool

If you are not sure of an entity's exact name, Protégé also provides a Search tool.

**Click the magnifying-glass icon in the upper-right corner of Protégé.**

Begin typing part of the entity name.

Protégé displays matching entities as you type.

The Search tool also provides options for controlling the search, including whether matching is case-sensitive and which parts of the ontology should be searched.

## Exercise Complete

✅ Pellet is now configured as the active reasoner, all available displayed inferences are enabled, and you have verified that Protégé can infer additional information from the People Ontology.

As you work through later exercises, remember to synchronize the reasoner frequently whenever you make changes that could affect logical inferences.

