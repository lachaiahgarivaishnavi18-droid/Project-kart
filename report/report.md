# Context-Aware Product Recommendation with a Five-Agent TF-IDF Pipeline

## Abstract

This report documents Context Cart, a locally executable demonstration of product recommendation from natural-language shopping queries and explicit customer preferences. Its Python workflow separates query understanding, customer context, product retrieval, ranking, and explanation into five agents coordinated by an orchestrator. Product records are synthetic. Retrieval uses TF-IDF cosine similarity and category metadata; ranking uses a fixed weighted formula with a hard budget filter when eligible items exist. An evaluation script compares keyword, TF-IDF, context-aware TF-IDF, and five-agent ranking on four synthetic category-labelled queries. The measured results describe this implementation and toy dataset only; they do not establish human preference quality or real-world performance.

## 1. Introduction

Retail search often requires combining intent expressed in natural language with constraints such as budget, brand, and channel. This project implements an inspectable end-to-end software baseline. Its emphasis is reproducibility, modularity, trace visibility, and evidence-bounded explanations, rather than a claim of novel algorithmic performance.

## 2. Literature Review

Term weighting and vector-space retrieval are established methods for matching text documents to queries. Salton and Buckley survey term-weighting approaches, providing a foundation for the TF-IDF-style lexical matching used here [1]. Recommender systems span content-based, collaborative, and hybrid techniques; this project is a small content-based prototype and does not have user interaction histories [2]. Retrieval-augmented generation combines retrieval with generation for knowledge-intensive tasks [3]. Context Cart uses retrieval and evidence assembly but intentionally does not generate text with an LLM; explanations are deterministic templates. Thus “RAG” here describes retrieval-grounded recommendation context, not a fully generative RAG model.

## 3. Existing System and Limitations

A plain keyword baseline is easy to understand but does not score semantic similarity or incorporate context. The prototype compares it with TF-IDF and context-aware variants. It does not include retailer inventory, collaborative signals, user histories, online learning, dense embeddings, a vector database, or an external language model. Product claims and evaluation therefore remain constrained to synthetic catalogue text.

## 4. Proposed System and Contributions

The system provides (1) a five-module agent architecture with per-agent execution trace, (2) lexical product retrieval with metadata filtering, (3) transparent context-aware ranking and budget feasibility behavior, (4) catalogue-grounded explanations and side-by-side comparisons, and (5) reproducible metrics and generated artifacts. These are engineering features, not claims of research novelty.

## 5. System Architecture

The Streamlit interface sends query and explicitly chosen context to a central orchestrator. Query Understanding extracts keywords, category, and a budget expression. Customer Context combines those values with optional user settings. Product Retrieval ranks catalogue descriptions with scikit-learn TF-IDF and cosine similarity. Recommendation and Ranking applies metadata and context. Explanation formats only fields present in the retrieved product record. Mermaid source diagrams for the overall architecture, agent interactions, RAG workflow, data flow, deployment design, and user workflow appear in `docs/diagrams/architecture.md`.

## 6. Dataset Description

The application generates 120 deterministic synthetic products across headphones, backpacks, smartphones, running shoes, water bottles, and watches. The schema contains product ID/name, category, brand, price in fictional INR, description, specifications, rating, review count, availability, channel, and source. Every record is labelled `synthetic demonstration data`. No third-party data or actual customer information is used. See `data/DATA_DICTIONARY.md` and `data/SOURCE.md` for field and provenance details. The template-like vocabulary and invented rating/availability values sharply limit external validity.

## 7. Methodology

Product name, category, brand, description, and specifications are concatenated for vectorization. `TfidfVectorizer` uses English stop-word removal and 1–2 grams. Cosine similarity orders retrieval results. Category is an optional exact metadata constraint. Ranking uses `0.50 × normalized retrieval + 0.20 × rating/5 + 0.15 × budget + 0.10 × availability + 0.05 × explicit preference`, where explicit preference averages preferred-brand match and selected-channel match. When a budget is specified and any candidates fit it, over-budget candidates are excluded before ranking; if none fit, over-budget fallback items may appear and are labeled. Explanations cite query similarity, rating, budget status, preferred brand or channel if applicable, description, specifications, and availability. No missing product claim is inferred.

## 8. Implementation

The Python package lives in `src/recommender/`; the Streamlit interface is `app.py`. CSV validation enforces required columns and numeric ranges, removes duplicate IDs, coerces numeric fields, and fills missing text. The application requires no API key. Context is passed through the current workflow and is not stored in a customer profile. No external API or cloud deployment is involved.

## 9. Experimental Setup

The evaluation uses four fixed query/category/budget pairs and the generated catalogue. The relevant set for each query is every product with the expected synthetic category. This is a deterministic proxy label, not a human judgment. Four methods are compared: a first-five exact-category keyword filter, top-five global TF-IDF, top-five TF-IDF after category filtering, and the five-agent ranking with context. Metrics are Precision@5, Recall@5, MRR@5, NDCG@5, measured local latency, and budget satisfaction. Latency is an informational single-process timing, not a controlled benchmark.

## 10. Results and Discussion

The recorded run is in `outputs/evaluation/metrics.csv`, with per-query detail in `outputs/evaluation/query_results.csv`. Results from this environment:

| Method | Precision@5 | Recall@5 | MRR@5 | NDCG@5 | Mean latency (ms) | Budget satisfaction |
|---|---:|---:|---:|---:|---:|---:|
| Keyword | 0.550 | 0.138 | 0.550 | 0.533 | 1.105 | 0.500 |
| TF-IDF | 0.950 | 0.238 | 1.000 | 0.967 | 2.236 | 0.600 |
| Context-aware TF-IDF | 1.000 | 0.250 | 1.000 | 1.000 | 2.236 | 0.650 |
| Five-agent ranking | 1.000 | 0.250 | 1.000 | 1.000 | 12.227 | 1.000 |

The five-agent method satisfies the constructed budget constraint in this run because the ranking stage filters over-budget items when feasible. The category labels explain the perfect category precision of metadata-filtered methods by construction; this should not be read as a general relevance result. The increase in measured latency reflects Python workflow and result construction in a small local run; it is not a robust performance estimate. No statistical significance or human preference evaluation is claimed.

## 11. Security, Privacy, Fairness, and Explainability

The prototype has no external model or secret-bearing integration. Inputs are validated, numeric UI controls are bounded, and catalogue values are cleaned. Preferences are request-scoped and not persisted. Explanations are restricted to product catalogue fields and explicit ranking factors. Prompt injection is not part of the current non-LLM execution path. No fairness, accessibility, privacy certification, threat-model review, or penetration test has been completed. Synthetic product diversity and the ranking formula can encode arbitrary tradeoffs; broader data and stakeholder review would be necessary before real use.

## 12. Conclusion and Future Scope

This work delivers a tested local recommendation application with explicit retrieval, context, ranking, evidence, and evaluation stages. The results show that the code follows its synthetic category and budget rules, not that it improves real shopping outcomes. Next steps include consented human relevance annotations, realistic licensed catalogues, ranking ablations, fairness and accessibility evaluation, optional semantic retrieval, and deployment hardening.

## 13. References

[1] G. Salton and C. Buckley, “Term-weighting approaches in automatic text retrieval,” *Information Processing & Management*, vol. 24, no. 5, pp. 513–523, 1988, doi: 10.1016/0306-4573(88)90021-0.

[2] F. Ricci, L. Rokach, and B. Shapira, Eds., *Recommender Systems Handbook*, 2nd ed. Springer, 2015, doi: 10.1007/978-1-4899-7637-6.

[3] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, vol. 33, 2020.

## 14. Appendix

### A. Test cases

| Test | Expected behavior | Status in this implementation |
|---|---|---|
| Catalogue schema and row count | At least 100 unique synthetic products | Pass |
| Sample budget query | Extract 3000 and return eligible products when present | Pass |
| Explanation grounding | Include catalogue evidence fields | Pass |
| Explicit brand/channel context | Carry supplied values into result | Pass |
| Evaluation metric generation | Return finite metrics for four baselines | Pass |

### B. Demonstrated outputs

The actual recommendation, first-two-product comparison, and context/evidence records are stored in `outputs/examples/`. They are generated by running the local orchestrator, not manually authored. No screenshots are claimed in this report until captured from a real browser session.

### C. Data dictionary

See `data/DATA_DICTIONARY.md` for all 12 field definitions and validation behavior.