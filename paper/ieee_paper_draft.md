# An Agentic Retrieval-Augmented Architecture for Context-Aware Product Recommendation in Omnichannel Retail

**Author(s):** [Name], [Institution], [Email]

## Abstract

This paper presents Context Cart, a reproducible software prototype for context-aware product recommendation. Five specialized Python agents parse a shopping query, assemble explicitly provided customer context, retrieve product records, rank candidates, and generate explanations grounded in catalogue fields. The retrieval component uses TF-IDF and metadata filtering; the prototype has no language model or vector database. A deterministic synthetic catalogue of 120 products supports local execution without external credentials. Four retrieval and ranking methods are measured using category-derived relevance labels, Precision@5, Recall@5, MRR@5, NDCG@5, latency, and budget satisfaction. In one local run, the five-agent ranking achieved 1.000 Precision@5 and 1.000 budget satisfaction; because the relevance labels and dataset are synthetic and category-filtered, these values are not evidence of real-world recommendation quality. The contribution is an inspectable end-to-end implementation and evaluation baseline rather than a claim of algorithmic novelty.

## Index Terms

Product recommendation, information retrieval, TF-IDF, explainable systems, agent orchestration, synthetic evaluation.

## I. Introduction

Natural-language product discovery requires mapping user intent to catalogue records while respecting explicit constraints. A practical prototype should make retrieval evidence and ranking tradeoffs inspectable. This paper describes a modular implementation that exposes these stages through a Streamlit application.

## II. Related Work

Term weighting is a foundational family of text-retrieval methods [1]. Recommender systems include content-based, collaborative, and hybrid approaches [2]. Retrieval-augmented generation combines retrieval with language generation [3]. The present work uses lexical retrieval and evidence-grounded templating only; it is not an LLM-based RAG system.

## III. Research Gap and Problem Statement

This project addresses the engineering problem of composing query parsing, explicit customer context, catalogue retrieval, transparent ranking, and grounded explanations in a small, reproducible application. It does not claim that existing research lacks such methods or that this architecture is novel. The implementation question is whether these components can be separated, inspected, and evaluated with local synthetic data.

## IV. Objectives

1. Implement five specialized modules under one orchestrator.
2. Provide TF-IDF retrieval with metadata filtering and catalogue evidence.
3. Rank products using documented factors and respect budget when feasible.
4. Expose trace, comparison, and grounded explanations in a local interface.
5. Measure simple baselines with explicit caveats about synthetic labels.

## V. Proposed Architecture

The workflow consists of a Streamlit interface, a central orchestrator, five deterministic agents, an in-memory TF-IDF index, and a generated CSV catalogue. Query Understanding extracts tokens, category, and budget. Customer Context carries user-entered budget, brands, channel, and preferences. Product Retrieval returns product records and lexical similarity. Recommendation and Ranking applies a weighted score. Explanation produces a bounded rationale from retrieved fields. Seven editable diagrams are maintained in `docs/diagrams/architecture.md`.

## VI. Methodology

Product name, category, brand, description, and specifications form TF-IDF documents with unigram/bigram terms and English stop-word removal. Retrieval uses cosine similarity and optional exact category filtering. Ranking is `0.50 relevance + 0.20 rating + 0.15 budget + 0.10 availability + 0.05 explicit preference`, where explicit preference averages preferred-brand match and selected-channel match. A specified budget filters out over-budget candidates whenever at least one candidate is under budget. Otherwise, fallback results remain visible with a false budget flag. Explanations use source catalogue text and explicit score factors; they do not infer missing properties.

## VII. Implementation

The implementation uses Python, Pandas, scikit-learn, and Streamlit. The local synthetic catalogue has 120 records in six categories. The application makes no paid API calls and does not store customer profiles. Synthetic attributes are fictional and labelled in every source row.

## VIII. Experimental Setup

Four fixed queries represent headphones, backpacks, running shoes, and water bottles. The relevant set is category membership, defined by the query specification. The baselines are an exact category keyword filter, global TF-IDF, category-filtered TF-IDF, and five-agent ranking with budget context. The evaluation reports Precision@5, Recall@5, MRR@5, NDCG@5, single-process latency, and budget satisfaction. There are four query intents and no human judgments.

## IX. Results and Discussion

The recorded evaluation run is summarized below; raw metrics and query-level rows are in `outputs/evaluation/`.

| Method | P@5 | R@5 | MRR@5 | NDCG@5 | Mean latency (ms) | Budget satisfaction |
|---|---:|---:|---:|---:|---:|---:|
| Keyword | 0.550 | 0.138 | 0.550 | 0.533 | 1.105 | 0.500 |
| TF-IDF | 0.950 | 0.238 | 1.000 | 0.967 | 2.236 | 0.600 |
| Context-aware TF-IDF | 1.000 | 0.250 | 1.000 | 1.000 | 2.236 | 0.650 |
| Five-agent ranking | 1.000 | 0.250 | 1.000 | 1.000 | 12.227 | 1.000 |

The five-agent method met the encoded budget constraint in this run. Category-filtered methods score strongly because relevance itself is defined by category; accordingly, the table is a code-path sanity check, not a quality comparison on real user judgments. Latencies are one local run and should not be used for capacity planning. No statistical test, user study, or claim of improved real-world performance is made.

## X. Responsible AI Considerations

No sensitive personal data or persistent user profile is required. The product corpus is synthetic, and explanations are bounded by its fields. Bias, accessibility, coverage, and consumer outcomes are unmeasured. Deployment to real retail data would require licensing review, privacy controls, security threat modeling, fairness evaluation, human relevance assessments, and operational monitoring.

## XI. Conclusion and Future Scope

The prototype demonstrates an executable agent-oriented recommendation workflow and a reproducible synthetic evaluation. Future research should replace category-derived labels with consented human judgments, use licensed catalogues, evaluate diverse user intents, and compare lexical retrieval with semantic methods under controlled experimental conditions. No novelty or performance improvement is asserted.

## References

[1] G. Salton and C. Buckley, “Term-weighting approaches in automatic text retrieval,” *Information Processing & Management*, vol. 24, no. 5, pp. 513–523, 1988, doi: 10.1016/0306-4573(88)90021-0.

[2] F. Ricci, L. Rokach, and B. Shapira, Eds., *Recommender Systems Handbook*, 2nd ed. Springer, 2015, doi: 10.1007/978-1-4899-7637-6.

[3] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, vol. 33, 2020.

## Formatting and Verification Note

This is an editable IEEE-style manuscript draft, not a typeset IEEE submission. Before submission, authors should verify bibliographic metadata against publisher/IEEE/Crossref records, add affiliation and funding details, apply the current official conference template, and replace the synthetic evaluation with an approved study if making empirical claims.