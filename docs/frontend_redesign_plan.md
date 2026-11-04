# Context Cart Frontend Redesign Plan

## Inspection Findings

- The frontend is a single Streamlit 1.66 application in `app.py`; there is no React/Next.js project or `package.json`.
- Product data is loaded from `data/products.csv` via `ensure_catalogue()` and is explicitly synthetic.
- Recommendations run in-process through `RecommendationOrchestrator`; no FastAPI service, HTTP client, chat endpoint, or authentication integration exists.
- Evaluation uses the local evaluation module and saved CSV records under `outputs/evaluation/`.
- Existing discovery, recommendation explanation, comparison, agent trace, evidence, evaluation, and About functionality should remain available.

## Implementation

- Retained the existing Streamlit app, recommender, catalogue, evaluation modules, and local navigation. No backend, schema, or API contract was changed.
- Kept dashboard metrics based on catalogue records and browser-session activity; labelled catalogue statistics and inventory as synthetic.
- Preserved product search, filters, ranking, explanation, agent trace, session preferences, and cross-page comparison. Product cards now expose catalogue details and budget, preference, and availability signals; comparisons include recommendation scores when available.
- Added discovery sorting and grid/list layouts, product detail profiles reachable from product cards, and a four-item comparison limit with best-available-value highlighting. Missing product attributes are explicitly marked as unavailable in the catalogue.
- Enhanced Product Details with catalogue-backed brand/category/rating/review/stock facts, a structured feature table, recommendation match signals and evidence citations, inventory/channel disclosure, comparison/navigation actions, and up to four related products.
- Kept the assistant connected to the existing local orchestrator, with loading feedback, suggested prompts, product citations, and comparison controls. The interface explicitly states that no hosted chat model or chat API is configured.
- Used saved local evaluation output when present; otherwise the dashboard displays “Not evaluated yet.” It shows ranking metrics and whole-pipeline latency without implying per-agent timing.
- Added 120 distinct, locally stored Wikimedia Commons product-category reference photographs. The product-ID manifest records each image's source, license, creator/attribution, and category; none is represented as the exact fictional branded SKU. Six earlier Unsplash category references remain only as fallbacks for future unmapped catalogue records. Store locations, stock quantities, pickup, and delivery data remain unavailable and are not fabricated.
- Added responsive layout rules, reduced-motion support, and safe escaping for dynamic values included in custom HTML.
- Verified with the existing pytest and Streamlit `AppTest` suites. A browser screenshot is not claimed because browser automation is not configured in this workspace.

## Design Direction

White workspace, navy navigation rail, teal/blue accents, compact SaaS typography, restrained shadows, accessible contrast, and responsive Streamlit columns. The product catalogue has no image URLs, so unique local Wikimedia Commons product-category photographs are mapped by catalogue ID; source and license notes are in `assets/products/ATTRIBUTION.md`.