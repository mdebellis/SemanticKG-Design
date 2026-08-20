# Exercise 3-2: Getting Access to AllegroGraph

`EXERCISE_3-2_Getting_Access_to_AllegroGraph.md`

**In this exercise, you will learn how to get access to AllegroGraph so that you can run the more advanced SPARQL queries used in later exercises.**

In the previous exercise, you used the Wikidata Query Service to execute SPARQL queries against Wikidata. That works well when the data you want to query is already in Wikidata, but it does not let you load and query the ontologies used in this book.

For the remaining SPARQL exercises, you will use **AllegroGraph**.

AllegroGraph provides a complete implementation of SPARQL and includes **Gruff**, a graphical tool that you will later use to explore and visualize Semantic Knowledge Graphs and SPARQL query results.

## Choose How You Want to Run AllegroGraph

There are three ways to use the free Community version of AllegroGraph:

1. **AllegroGraph Cloud** — the easiest way to get started.
2. **Docker** — a good option if you want AllegroGraph running locally on your computer.
3. **Linux Tar distribution** — a native Linux installation for users who prefer to install AllegroGraph directly on a Linux system.

For the exercises in this book, I recommend that you begin with **AllegroGraph Cloud**. It requires the least setup and lets you start working with AllegroGraph quickly.

If you later decide that you want a persistent local environment for your own Semantic Knowledge Graph projects, Docker is generally the easiest next step.

> **Note:** The Community Cloud environment is designed for active use. If you do not log in for a period of time, you may receive notices that your account is inactive and that repositories you created may eventually be deleted. For long-term work, you may therefore prefer a local installation.

---

## Option 1: Use AllegroGraph Cloud

### Step 1: Open the AllegroGraph Downloads Page

Go to the [AllegroGraph Downloads page](https://allegrograph.com/downloads/).

### Step 2: Open the Cloud Login

**Select `AllegroGraph Cloud Login`.**

This takes you to the AllegroGraph Cloud login page.

### Step 3: Create an Account

If you do not already have an AllegroGraph Cloud account:

**Select `Don't have an account? Sign up`.**

Follow the instructions to create your account.

### Step 4: Log In

**Log in to AllegroGraph Cloud using the account you created.**

✅ You now have access to an AllegroGraph environment and are ready for the subsequent exercises.

If you are using AllegroGraph Cloud, you can stop here.

---

## Option 2: Run AllegroGraph with Docker

If you prefer to run AllegroGraph locally, Docker provides a convenient alternative to the Cloud version.

Open the [AllegroGraph Docker installation instructions](https://franz.com/agraph/support/documentation/docker.html).

The instructions walk you through installing Docker Desktop and then downloading and running the AllegroGraph Docker container.

Docker requires more initial setup than the Cloud version, but after installation you have an AllegroGraph environment running locally on your own computer.

---

## Option 3: Install AllegroGraph Directly on Linux

You can also download the AllegroGraph Tar distribution and install it directly on a Linux system.

This option is most appropriate if you already work in a Linux environment and prefer a native installation rather than Docker.

For simply completing the exercises in this book, however, you do not need to install AllegroGraph this way. The Cloud version is the quickest route, and Docker provides an easier local alternative.

## Exercise Complete

✅ You should now have access to AllegroGraph through one of the following:

* AllegroGraph Cloud
* a local Docker installation
* a native Linux installation

The next AllegroGraph exercises will build on this environment by loading ontologies, executing SPARQL queries, and using Gruff to explore query results.
