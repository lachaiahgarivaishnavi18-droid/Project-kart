# Project Video Script (8–12 minutes)

## 0:00–0:45 | Introduction
“This project demonstrates a context-aware product recommendation workflow for omnichannel retail. It accepts a natural-language shopping query and optional preferences, retrieves product catalogue evidence, ranks candidates transparently, and explains the result. The application runs locally without a paid API key.”

## 0:45–1:45 | Problem and objectives
“A simple keyword search can miss the intent behind a shopping request and may not apply a budget consistently. The prototype combines query terms, an optional category, budget, preferred brands, and shopping channel. Its goals are inspectability, reproducibility, and a clear separation between retrieval, ranking, and explanation.”

## 1:45–3:15 | Architecture and agents
Show the architecture diagram. “The Streamlit interface calls one orchestrator, which runs five modules: Query Understanding extracts terms, category, and budget; Customer Context carries user-supplied settings for this request; Product Retrieval uses TF-IDF and category metadata; Recommendation and Ranking computes a weighted score; Explanation presents catalogue evidence. The UI displays each step’s trace.”

## 3:15–4:00 | Dataset
“The application creates 120 deterministic synthetic products in six categories. The brand names, prices, ratings, specifications, availability, and review counts are fictional. The data dictionary defines each field. This keeps the demo reproducible and avoids presenting third-party retail data as real.”

## 4:00–6:30 | Live output 1: recommendation
Enter “Lightweight wireless headphones for travel under 3000”. Show the detected budget, candidate evidence, rankings, prices, ratings, and explanations. “The retrieval score is lexical TF-IDF similarity. The rank score weights relevance 0.50, rating 0.20, budget 0.15, availability 0.10, and explicit preferences 0.05. The preference score averages preferred brand and selected-channel match. If an in-budget product exists, over-budget items are excluded. Explanations only repeat evidence in the displayed catalogue fields.”

## 6:30–7:30 | Live output 2: comparison
Select two recommendations. Compare price, brand, rating, specifications, and availability. “Advantages and limitations are based on these available synthetic fields; missing specification fields are not guessed.”

## 7:30–8:15 | Live output 3: context explanation
Show the applied customer context, evidence rows, trace, and final explanation. “The selected channel and preferences are request-scoped; the app does not create stored customer profiles.”

## 8:15–9:45 | Evaluation
Run the evaluation view and show the result table. “Four fixed synthetic query intents use category membership as the relevance label. We report Precision@5, Recall@5, MRR@5, NDCG@5, latency, and budget satisfaction for keyword, TF-IDF, context-aware TF-IDF, and five-agent ranking. These are measurements of this toy dataset and label design, not human relevance judgments or evidence of real-world improvement.”

## 9:45–10:45 | Limitations and future work
“This version has no LLM, semantic embedding model, vector database, retailer integration, or production customer data. Future work could collect consented human relevance judgments, evaluate diverse and real catalogues, audit fairness, add an optional model behind a secure interface, and benchmark a managed vector index.”

## 10:45–11:15 | Conclusion
“The deliverable is a runnable, testable baseline with visible evidence and measured synthetic evaluation. The key contribution here is an inspectable end-to-end software workflow, not a claim of novel ranking performance. Thank you.”