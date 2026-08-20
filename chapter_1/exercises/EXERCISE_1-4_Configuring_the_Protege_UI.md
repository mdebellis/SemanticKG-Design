# Exercise 1-4: Configuring the Protégé UI

**In this exercise, you will learn how to customize the Protégé user interface by enabling tabs and adding the Snap SPARQL view to the `DL Query` tab.**

The Protégé user interface is highly customizable. It consists primarily of **tabs** and **views**.

A **tab** is a large container that usually contains several views. Protégé provides several preconfigured tabs, and you can decide which of them are visible.

A **view** displays a particular kind of information or functionality within a tab. You can add or remove views to customize the workspace.

For the exercises in this book, you will make a few minor changes so that your Protégé interface contains the tabs and views used in later examples.

## Step 1: Enable the Required Tabs

Protégé lets you control which tabs are visible from the `Window` menu.

**Select `Window > Tabs`.**

The tabs that are currently visible should have check marks next to them.

Make sure the following tabs are selected:

* `DL Query`
* `Individuals by Class`

The `DL Query` tab allows you to execute Description Logic queries. It will also provide a convenient place for the Snap SPARQL view.

The `Individuals by Class` tab provides a convenient way to browse ontology individuals grouped according to their classes.

## Step 2: Open the DL Query Tab

**Select the `DL Query` tab.**

Look at the views displayed within the tab.

If `Snap SPARQL Query` is already present as a view, you do not need to add it again. You can skip to the next exercise.

If it is not present, continue with the following steps.

## Step 3: Add the Snap SPARQL View

Make sure you are still in the `DL Query` tab.

**Select `Window > Views > Query views > Snap SPARQL Query`.**

Protégé should display a blue outline representing the new view.

> **Note:** If `Snap SPARQL Query` does not appear in the `Query views` menu, verify that you installed the Snap SPARQL plugin in the previous exercise and restarted Protégé.

## Step 4: Position the New View

Move the blue outline around within the `DL Query` tab.

As you move it, Protégé changes the outline to show where the new view will be placed.

I recommend positioning `Snap SPARQL Query` so that it appears alongside the existing `DL Query` view.

Your screen should look similar to the following:

*[Screenshot: DL Query tab with Snap SPARQL Query view]*

**When the blue outline is positioned where you want the new view, click the mouse.**

The Snap SPARQL view should now appear as part of the `DL Query` tab.

> 💡 **Tip:** Positioning a new view can be slightly confusing the first time. If it ends up in the wrong place, simply remove it and try again.

## Step 5: Remove a View if Necessary

If you add a view in the wrong location:

**Click the `X` in the upper-right corner of that view.**

You can then repeat the previous steps and add it again.

## Restoring a Tab to Its Default Layout

Protégé also provides a quick way to undo accidental changes to a tab.

If you ever want to restore the currently selected tab to its original configuration:

**Select `Window > Reset selected tab to default state`.**

Protégé will restore the default arrangement of views for that tab.

## Exercise Complete

✅ Your Protégé interface should now include the `DL Query` and `Individuals by Class` tabs, with the `Snap SPARQL Query` view available from the `DL Query` tab.

This configuration will make it easier to follow the examples and complete later exercises involving DL queries and SPARQL.
