# 🧪 Ontology Verification Suite

**Directory:** `/test/verify/`
**Purpose:**
This folder contains a set of SPARQL queries used to verify structural and modeling consistency across all BRO-based ontologies (Basic Reusable Ontology, Data Product Ontology, People Ontology, etc.).

Each file checks a specific integrity constraint or modeling convention.
All queries are written in standard SPARQL 1.1 and can be executed in Protege, AllegroGraph, GraphDB, or any other SPARQL endpoint that supports the loaded ontology.

**Usage pattern:**

1. Load the ontology to be tested into your triplestore or Protege environment.
2. Execute each `.sparql` file in order.
3. Each query’s comment header and `Expected Result` section describe what a “clean” outcome should look like.
4. Address any reported issues before committing changes or incrementing the ontology version.

---

## 🧾 Verification Queries

### **01-verify-prefixes.sparql**

**Purpose:**
Checks that all namespaces use canonical `http://` identifiers for standard vocabularies (RDF, RDFS, OWL, XSD, SKOS, PROV, DCTERMS, etc.).
**Expected Result:** Zero rows.
**Action:** Replace any `https://` occurrences with canonical `http://` IRIs.

---

### **02-verify-language-tags.sparql**

**Purpose:**
Ensures that all human-readable annotations (`rdfs:label`, `rdfs:comment`, `skos:definition`, etc.) include a language tag.
**Expected Result:** Zero rows (no missing language tags).
**Action:** Add `@en` or the appropriate language tag to all string literals used for labels and definitions.

---

### **03-verify-label-uniqueness.sparql**

**Purpose:**
Detects cases where two distinct IRIs share the same `rdfs:label`.
**Expected Result:** Zero rows.
**Action:** Update labels to ensure uniqueness within a given namespace.

---

### **04-verify-domain-and-range.sparql**

**Purpose:**
Reports object and data properties that lack explicit `rdfs:domain` or `rdfs:range` declarations.
**Expected Result:** Zero rows.
**Action:** Define missing domains and ranges to support reasoning and validation.

---

### **05-verify-agent-alignment.sparql**

**Purpose:**
Checks that `dcterms:Agent` and `prov:Agent` are declared equivalent and that `dcterms:Agent` is marked deprecated.
**Expected Result:** One row showing equivalence; no missing or conflicting definitions.
**Action:** Add or correct the `owl:equivalentClass` and `owl:deprecated` statements if missing.

---

### **06-verify-dc-usage.sparql**

**Purpose:**
Flags any usage of deprecated `dc:*` properties (e.g., `dc:title`, `dc:creator`).
**Expected Result:** Zero rows.
**Action:** Replace all `dc:*` predicates with the corresponding `dcterms:*` forms.

---

### **07-verify-provenance-consistency.sparql**

**Purpose:**
Checks that all entities involved in provenance relations (`prov:wasDerivedFrom`, `prov:wasAttributedTo`, etc.) have valid `prov:Agent` or `prov:Entity` types.
**Expected Result:** Zero rows.
**Action:** Add missing types or correct mis-typed entities.

---

### **08-verify-skos-structure.sparql**

**Purpose:**
Validates that SKOS concepts are properly linked using `skos:broader`, `skos:narrower`, or `skos:related` and that these relations are not misapplied to non-concepts.
**Expected Result:** Zero rows.
**Action:** Restrict SKOS relations to instances of `skos:Concept`.

---

### **09-verify-label-language-tags.sparql**

**Purpose:**
Duplicate check focusing specifically on `rdfs:label` to ensure all labels have language tags (useful when labels are generated automatically).
**Expected Result:** Zero rows.
**Action:** Add `@en` or other appropriate language tags.

---

### **10-detect-multiple-declarations.sparql**

**Purpose:**
Ensures that no entity (IRI) in the ontology is declared with more than one OWL role.
This check detects *punning* errors—cases where the same IRI is defined both as an `owl:AnnotationProperty`, `owl:DataProperty`, `owl:ObjectProperty`, `owl:Class`, or `owl:NamedIndividual`.
These are almost always unintentional and can cause Protege or reasoner warnings such as

> *“Illegal redeclarations of entities: reuse of entity X in punning not allowed.”*

**Expected Result:**
The query should return **zero rows**.
If any rows appear, the `declaredAs` column lists multiple OWL types assigned to the same IRI.
Open that entity in Protege and delete redundant declarations, keeping only the correct role (usually the one defined by the imported vocabulary).

**Example output:**

| entity                                                                             | declaredAs                                        |
| ---------------------------------------------------------------------------------- | ------------------------------------------------- |
| [http://www.w3.org/ns/prov#wasRevisionOf](http://www.w3.org/ns/prov#wasRevisionOf) | ObjectProperty, AnnotationProperty                |
| [http://purl.org/dc/terms/modified](http://purl.org/dc/terms/modified)             | AnnotationProperty, DataProperty, NamedIndividual |

**Action:**
Remove the extra declaration(s) so that each IRI has exactly one role.

---

## 🧭 General Notes

* All queries return **zero results** when the ontology is in a consistent, publishable state.
* Non-zero results indicate issues that should be resolved before releasing or tagging a new ontology version.
* Each `.sparql` file is independent and can be run individually or as part of an automated validation pipeline.

---
