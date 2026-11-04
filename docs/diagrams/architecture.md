# Editable Architecture Diagrams

## 1. Overall System Architecture
```mermaid
flowchart LR
  Shopper --> UI[Streamlit frontend]
  UI --> Orch[Recommendation orchestrator]
  Orch --> Agents[Five Python agents]
  Data[(Synthetic CSV)] --> Ingest[Validation and text preparation]
  Ingest --> TFIDF[TF-IDF sparse vectors]
  TFIDF --> Agents
  Agents --> UI
  UI --> Eval[Evaluation scripts]
  Eval --> Artifacts[CSV metrics and chart]
```

## 2. Five-Agent Architecture
```mermaid
flowchart TD
  Q[Query Understanding] --> C[Customer Context]
  C --> R[Product Retrieval]
  R --> K[Recommendation and Ranking]
  K --> E[Evidence Explanation]
  E --> O[Orchestrator response and trace]
```

## 3. RAG Workflow
```mermaid
flowchart LR
  CSV[Product CSV] --> Clean[Validate and normalize]
  Clean --> Docs[Product text documents]
  Docs --> Sparse[TF-IDF sparse vectors]
  Query[Shopping query] --> SparseQuery[TF-IDF query vector]
  Sparse --> Retrieve[Cosine-similarity retrieval]
  SparseQuery --> Retrieve
  Retrieve --> Filter[Category metadata filter]
  Filter --> Context[Retrieved product evidence]
  Context --> Rank[Deterministic ranking]
  Rank --> Explain[Template-based evidence explanation]
```
This is a lexical retrieval-augmented recommendation pipeline. It does not include an LLM, neural embeddings, or vector database.

## 4. Data-Flow Diagram
```mermaid
flowchart LR
  User[Query and optional preferences] --> Parse[Query parsing]
  Parse --> Context[Ephemeral customer context]
  Context --> Search[TF-IDF retrieval]
  Products[(Synthetic catalogue)] --> Search
  Search --> Candidates[Candidate products and scores]
  Candidates --> Rank[Weighted ranking]
  Rank --> Result[Recommendations, reasons, evidence]
  Result --> Browser[Streamlit session]
```

## 5. Agent Sequence Diagram
```mermaid
sequenceDiagram
  participant U as Shopper
  participant O as Orchestrator
  participant Q as Query Agent
  participant C as Context Agent
  participant R as Retrieval Agent
  participant K as Ranking Agent
  participant E as Explanation Agent
  U->>O: query, optional context
  O->>Q: parse query and budget
  Q-->>O: keywords, category, budget
  O->>C: combine explicit preferences
  C-->>O: request-scoped context
  O->>R: query and category filter
  R-->>O: candidates and catalogue evidence
  O->>K: candidates, context, top K
  K-->>O: ranked products and factor scores
  O->>E: products, query, evidence
  E-->>O: grounded explanations
  O-->>U: results and execution trace
```

## 6. Deployment Architecture
```mermaid
flowchart LR
  Browser --> Streamlit[Local or Codespaces Streamlit app]
  Streamlit --> Python[Python process and in-memory TF-IDF index]
  Python --> CSV[(Local synthetic CSV)]
  subgraph Optional future cloud, not deployed
    Registry[Azure Container Registry] --> AKS[Azure Kubernetes Service]
    AKS --> API[FastAPI service]
    API --> Search[Azure AI Search]
    API --> Vault[Key Vault]
    API --> Monitor[Azure Monitor and App Insights]
    Pipeline[Azure DevOps] --> Registry
    IaC[Terraform] --> AKS
  end
```

## 7. Customer Recommendation Workflow
```mermaid
flowchart TD
  A[Enter shopping intent] --> B[Add optional budget, brands, channel]
  B --> C[Parse query]
  C --> D[Retrieve catalogue evidence]
  D --> E{In-budget products available?}
  E -->|Yes| F[Rank eligible items]
  E -->|No| G[Rank candidates and label budget status]
  F --> H[Explain from catalogue fields]
  G --> H
  H --> I[Inspect trace, evidence, and comparison]
```