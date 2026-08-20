# Exercise 1-3: Loading Protégé Plugins

**In this exercise, you will learn how to view, install, and activate Protégé plugins. You will install the Pellet reasoner and the Snap SPARQL plugin, both of which are used in later exercises.**

Protégé supports a variety of plugins that extend its functionality. For the exercises in this book, you will need two additional plugins:

* **Pellet Reasoner**
* **Snap SPARQL**

Pellet is particularly useful for these exercises because later chapters use the Semantic Web Rule Language (SWRL).

Snap SPARQL provides a convenient way to experiment with SPARQL directly inside Protégé. It is useful for introductory queries and simple tasks such as generating labels from IRIs.

> **Note:** Snap SPARQL is not a complete implementation of the SPARQL specification and should not be treated as a general-purpose SPARQL environment. Later exercises use more complete SPARQL tools for working with Semantic Knowledge Graphs.

## Step 1: Open the Protégé Plugin Window

When Protégé starts, it may automatically display a window showing available plugins.

If the plugin window does not appear:

**Select `File > Check for plugins`.**

Protégé should display a window listing installed and available plugins.

Your screen should look similar to the following:

<img width="609" height="528" alt="Figure_1-2" src="https://github.com/user-attachments/assets/03be0fcd-55c9-4c81-8fde-55adcafc4594" />

## Step 2: Select the Required Plugins

In the plugin window, locate the following plugins:

* `Pellet Reasoner`
* `Snap SPARQL`

**Select the checkbox next to `Pellet Reasoner`.**

**Select the checkbox next to `Snap SPARQL`.**

The plugin window should now show both plugins selected for installation.

## Step 3: Install the Plugins

**Click `Install` at the bottom of the plugin window.**

The installation may take a minute or two.

When the installation completes, Protégé should display a message similar to:

> Plugins will be available the next time you start Protégé.

## Step 4: Restart Protégé

The newly installed plugins are not available until Protégé is restarted.

**Quit Protégé.**

**Start Protégé again.**

✅ Pellet and Snap SPARQL should now be available in the Protégé desktop environment.

## Next Step

Protégé is now configured with the plugins required for later exercises.

Subsequent exercises will use Pellet for reasoning, including exercises involving SWRL, and Snap SPARQL for introductory SPARQL queries and simple ontology-manipulation tasks.

