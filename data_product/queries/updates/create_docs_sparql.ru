PREFIX docs:    <https://www.michaeldebellis.com/docs/>
PREFIX dp:      <https://www.michaeldebellis.com/dp/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dcat:    <http://www.w3.org/ns/dcat#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
    docs:Creator_Engagement_Report_Q3_2025
      a owl:NamedIndividual , docs:Quarterly_Report ;
      dcterms:title "Creator Engagement Report — Q3 2025"@en ;
      dcterms:description """StreamForge creator engagement improved in Q3 2025, but gains were uneven across creator cohorts and upload frequencies. This report summarizes creator-side engagement metrics, highlights drivers of change, and proposes data product improvements for Q4.

Scope and time window
- Reporting period: Q3 2025 (2025-07-01 to 2025-09-30)
- Population: active creators with at least one upload in the last 90 days
- Exclusions: policy-removed channels and test accounts

Key metrics (Q3 vs Q2)
- Monthly active creators (MAC): +6.2%
- Uploads per active creator: +3.1%
- Creator retention (90-day): +1.4 pp
- Creator “time-to-first-view” median: improved from 46 minutes to 39 minutes
- Creator monetization enrollment: flat (+0.2%)

Drivers and observations
1) Faster “time-to-first-view” correlated strongly with higher creator retention, especially for small channels (<10k subscribers).
2) Improvements concentrated in long-form video; short-form creators did not see comparable lift.
3) Metadata completeness (title, tags, category) was the strongest predictor of search impressions for new uploads.
4) The creator onboarding funnel had a measurable drop at “connect payout account,” but this is outside the primary scope of this report.

Data quality notes
- We observed intermittent missing tag fields in the video metadata feed during August.
- A small fraction of creator profiles contained stale country codes after an upstream identity change.
- These issues did not materially change Q3 directional results, but they do reduce confidence in cohort segmentation.

Recommendations for Q4
- Prioritize the “Video Metadata” data product to improve completeness and freshness of tags and categories.
- Add a creator-facing metadata quality indicator (e.g., “your title/tag coverage is below typical for your category”).
- Publish a weekly “Creator Engagement Snapshot” to reduce dependence on quarterly retrospectives.
- Add SLAs for metadata freshness and completeness, aligned with creator experience metrics (time-to-first-view and impressions).

Open questions
- How much of time-to-first-view improvement came from ranking changes vs metadata improvements?
- Can we isolate the short-form creator cohort and design targeted metadata guidance?"""@en ;
      dcterms:creator "Creator Growth Analytics Team"@en ;
      dcterms:publisher "StreamForge Data Products Group"@en ;
      dcterms:created "2025-10-10"^^xsd:date ;
      docs:uses_data_product dp:SF_Creator_Insights_Product ;
      docs:uses_data_product dp:SF_Video_Metadata_Product ;
      docs:uses_dataset <https://www.michaeldebellis.com/streamforge/dataset/Creator_Engagement_Metrics> ;
      docs:uses_dataset <https://www.michaeldebellis.com/streamforge/dataset/Video_Metadata_Current> .

    docs:Personalization_Performance_Review_Q3_2025
      a owl:NamedIndividual , docs:Quarterly_Report ;
      dcterms:title "Personalization Performance Review — Q3 2025"@en ;
      dcterms:description """This Q3 2025 review assesses StreamForge personalization system performance across home feed ranking, “Up Next,” and notification targeting. We summarize model metrics, user outcomes, and known risks. The goal is to establish a stable baseline for Q4 experiments and to identify data product priorities affecting model quality.

Scope and time window
- Reporting period: Q3 2025 (2025-07-01 to 2025-09-30)
- Surfaces: Home feed, Up Next, Notifications
- Regions: global, with separate monitoring for India and Brazil

User outcome summary (Q3 vs Q2)
- Watch time per daily active user: +2.0%
- Session starts per user: +1.1%
- “Not interested” feedback rate: +0.4 pp (worse)
- Complaint rate (recommendation relevance): +0.2 pp (worse)
- Creator distribution: slightly more concentrated in top 1% channels (+0.6 pp share)

Model and data signals
- Offline AUC improved modestly for home feed ranking (+0.3%), but calibration drift increased in August.
- User embeddings refreshed less frequently than expected for a subset of users due to a pipeline backlog.
- Video metadata freshness had measurable impact on cold-start performance (new uploads and new creators).
- Category and tag coverage remains inconsistent across languages, affecting semantic retrieval features.

Risks and mitigations
- Concentration risk: personalization is increasingly reinforcing already-large channels. Mitigation: exploration controls and fairness-aware re-ranking.
- Drift risk: August calibration issues suggest instability in a small number of features derived from metadata timestamps. Mitigation: feature sanity checks and freshness SLAs.
- Trust risk: rising “Not interested” feedback indicates relevance mismatch for certain cohorts. Mitigation: cohort-specific tuning and better negative-signal modeling.

Recommendations for Q4
- Enforce a strict SLA for “Video Metadata Freshness” and validate timestamp monotonicity.
- Add monitoring for embedding refresh delays and backpressure in the feature pipeline.
- Run a targeted experiment to reduce channel concentration without reducing watch time.
- Improve multilingual tag normalization as a data product enhancement rather than a model-side patch.

Decisions requested
- Approve prioritization of metadata freshness work (pipeline + catalog validation) over new model architecture changes for the first half of Q4."""@en ;
      dcterms:creator "Personalization Platform Team"@en ;
      dcterms:publisher "StreamForge Recommendations & Trust"@en ;
      dcterms:created "2025-10-12"^^xsd:date ;
      docs:uses_data_product dp:SF_Recs_Features_Product ;
      docs:uses_data_product dp:SF_Video_Metadata_Product ;
      docs:uses_dataset <https://www.michaeldebellis.com/streamforge/dataset/Personalization_Events_Q3_2025> ;
      docs:uses_dataset <https://www.michaeldebellis.com/streamforge/dataset/Video_Metadata_Current> .

    docs:Incident_Report_Video_Metadata_Freshness_Regression
      a owl:NamedIndividual , docs:Incident_Report ;
      dcterms:title "Incident Report — Video Metadata Freshness Regression"@en ;
      dcterms:description """On 2025-09-01 we detected a regression in video metadata freshness that caused the cataloged metadata dataset to lag real-time updates by several hours. The incident affected personalization cold-start behavior and search indexing for newly uploaded videos. This report documents the impact, timeline, root cause, and corrective actions.

Impact
- Window of impact: 2025-09-01 08:20 UTC to 2025-09-01 16:05 UTC
- Metadata lag: up to 6.4 hours at peak
- User impact: reduced impressions and slower indexing for new uploads; elevated “not relevant” feedback in new-content cohorts
- Internal impact: multiple downstream jobs consumed stale timestamps, triggering feature drift alerts

Detection
- Primary signal: freshness SLA monitor breached for the Video Metadata dataset
- Secondary signal: downstream model feature drift alerts spiked for timestamp-derived features

Timeline (UTC)
- 08:20: freshness SLA breach detected
- 08:35: incident declared; DRE engaged
- 09:10: suspected backlog in ingestion pipeline
- 11:40: identified retry storm in metadata enrichment step
- 13:15: mitigation applied by throttling retries and clearing stuck partitions
- 16:05: freshness returned to normal; incident resolved

Root cause
A deployment changed retry behavior in the metadata enrichment job. A subset of malformed payloads triggered repeated retries, causing queue saturation and delaying the entire partition set. The system lacked a circuit breaker for repeated failures on the same payload class.

Corrective actions
- Add circuit breaker and dead-letter queue routing for malformed payloads
- Rate-limit retries and cap max retry time per partition
- Introduce payload validation earlier in the ingestion pipeline
- Extend catalog checks to include “freshness monotonicity” and “timestamp plausibility” rules

Follow-up
- Owner: Video Metadata data product team
- Deadline: implement circuit breaker and catalog validation rules by 2025-09-20
- Verification: replay incident window and confirm SLA compliance under fault injection"""@en ;
      dcterms:creator "Data Reliability Engineering (DRE)"@en ;
      dcterms:publisher "StreamForge Platform Operations"@en ;
      dcterms:created "2025-09-03"^^xsd:date ;
      docs:uses_data_product dp:SF_Video_Metadata_Product ;
      docs:uses_dataset <https://www.michaeldebellis.com/streamforge/dataset/Video_Metadata_Current> .}
