PREFIX :     <https://michaeldebellis.com/consulting_taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

# Map selected skos:narrower edges to rdfs:subClassOf (keep SKOS)
# This adds subclass axioms for the branches you chose as type hierarchies.
INSERT {
  ?child rdfs:subClassOf ?parent .
  ?parent a owl:Class .
  ?child  a owl:Class .
}
WHERE {
  VALUES (?parent ?child) {

    # Service lines
    (:Service_Line :Strategy)
    (:Service_Line :Data_And_AI)
    (:Service_Line :Cybersecurity)
    (:Service_Line :Cloud_Engineering)
    (:Service_Line :Risk_And_Compliance)

    # Industries
    (:Industry :Healthcare)
    (:Industry :Financial_Services)
    (:Industry :Retail)
    (:Industry :Manufacturing)
    (:Industry :Public_Sector)

    # Offerings
    (:Offering :Data_Product_Design)
    (:Offering :Ontology_Engineering)
    (:Offering :Graph_RAG_Implementation)
    (:Offering :Data_Governance_Playbook)
    (:Offering :Reference_Architecture)
    (:Offering :Data_Quality_Assessment)
    (:Offering :SHACL_Validation_Models)
    (:Offering :Metadata_Management)

    # Deliverables (types)
    (:Deliverable :Requirements_Model)
    (:Deliverable :Conceptual_Model)
    (:Deliverable :Design_Model)
    (:Deliverable :Implementation_Pipeline)
    (:Deliverable :Validation_Rules)
    (:Deliverable :Data_Catalog_Entries)
    (:Deliverable :Runbook)
    (:Deliverable :Executive_Readout)

    # Teams (types)
    (:Team :Engagement_Team)
    (:Team :Data_Platform_Team)
    (:Team :Governance_Team)
    (:Team :Security_Team)
    (:Team :Ontology_Team)
  }

  # Safety: only apply if the SKOS relation exists
  ?parent skos:narrower ?child .
}

PREFIX :     <https://michaeldebellis.com/consulting_taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

# Map selected skos:narrower edges to rdf:type (keep SKOS)
# Clients and engagements become individuals typed by their category class.
INSERT {
  ?child rdf:type ?parent .
  ?parent a owl:Class .
}
WHERE {
  VALUES (?parent ?child) {
    # Clients
    (:Client :Northwind_Health)
    (:Client :Acme_Bank)
    (:Client :Contoso_Retail)

    # Engagements
    (:Engagement :Northwind_Claims_RAG)
    (:Engagement :Acme_KYC_Modernization)
    (:Engagement :Contoso_Product_Analytics)
  }

  # Safety: only apply if the SKOS relation exists
  ?parent skos:narrower ?child .
}

PREFIX :     <https://michaeldebellis.com/consulting_taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sulo: <https://w3id.org/sulo/>

# Map selected skos:narrower edges to SULO isDirectPartOf (keep SKOS)
# This maps only the engagement-specific “parts”
INSERT {
  ?part sulo:isDirectPartOf ?whole .
}
WHERE {
  VALUES (?whole ?part) {

    # Northwind Claims RAG parts
    (:Northwind_Claims_RAG :Northwind_Claims_RAG_Engagement_Team)
    (:Northwind_Claims_RAG :Northwind_Claims_RAG_Conceptual_Model)
    (:Northwind_Claims_RAG :Northwind_Claims_RAG_Validation_Rules)

    # Acme KYC Modernization parts
    (:Acme_KYC_Modernization :Acme_KYC_Modernization_Engagement_Team)
    (:Acme_KYC_Modernization :Acme_KYC_Modernization_Requirements_Model)
    (:Acme_KYC_Modernization :Acme_KYC_Modernization_Executive_Readout)
  }

  # Safety: only apply if the SKOS relation exists
  ?whole skos:narrower ?part .
}

PREFIX :     <https://michaeldebellis.com/consulting_taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sulo: <https://w3id.org/sulo/>

# After graph query (OWL relations only, same node set as the SKOS tree)
# Use this after doing the transformations above
# This query returns only the transformed predicates: rdfs:subClassOf, rdf:type, sulo:isDirectPartOf
# It restricts the nodes to those reachable from your scheme’s root using the original SKOS taxonomy. 
# That gives you a revised graph that covers the same conceptual space as the SKOS tree, without dragging in unrelated stuff.
SELECT DISTINCT ?s ?p ?o
WHERE {
  VALUES ?scheme { :Consulting_Firm_Taxonomy }

  # Identify the root of the SKOS taxonomy
  ?root skos:topConceptOf ?scheme .

  # --- Subclass edges (class hierarchy) ---
  {
    ?s rdfs:subClassOf ?o .
    BIND(rdfs:subClassOf AS ?p)

    # Keep only edges where the subject is reachable from the SKOS root
    FILTER EXISTS { ?root (skos:narrower)* ?s }
  }
  UNION

  # --- Instance typing edges ---
  {
    ?s rdf:type ?o .
    BIND(rdf:type AS ?p)

    # Keep only typings where the individual is reachable from the SKOS root
    FILTER EXISTS { ?root (skos:narrower)* ?s }
  }
  UNION

  # --- Mereology edges ---
  {
    ?s sulo:isDirectPartOf ?o .
    BIND(sulo:isDirectPartOf AS ?p)

    # Keep only part-of edges where the part is reachable from the SKOS root
    FILTER EXISTS { ?root (skos:narrower)* ?s }
  }
}

