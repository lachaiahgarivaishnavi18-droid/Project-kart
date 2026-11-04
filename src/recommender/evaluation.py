"""Reproducible, label-based retrieval and ranking metrics."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .agents import CustomerContext
from .catalog import PRODUCT_FAMILIES, ProductRetriever
from .orchestrator import RecommendationOrchestrator

EVAL_QUERIES = [
    {"query": "lightweight wireless headphones", "category": "Headphones", "budget": 3000},
    {"query": "water resistant travel backpack", "category": "Backpacks", "budget": 3500},
    {"query": "cushioned running shoes breathable", "category": "Running Shoes", "budget": 5000},
    {"query": "insulated stainless steel water bottle", "category": "Water Bottles", "budget": 1200},
]


def _metrics(ranked_ids: list[str], relevant_ids: set[str], k: int) -> dict[str, float]:
    top = ranked_ids[:k]
    hits = [1 if item in relevant_ids else 0 for item in top]
    precision = sum(hits) / k
    recall = sum(hits) / max(len(relevant_ids), 1)
    reciprocal_rank = next((1 / (index + 1) for index, hit in enumerate(hits) if hit), 0.0)
    dcg = sum(hit / np.log2(index + 2) for index, hit in enumerate(hits))
    ideal_count = min(len(relevant_ids), k)
    idcg = sum(1 / np.log2(index + 2) for index in range(ideal_count))
    return {"precision_at_5": precision, "recall_at_5": recall, "mrr_at_5": reciprocal_rank,
            "ndcg_at_5": dcg / idcg if idcg else 0.0}


def evaluate(products: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    products = products.reset_index(drop=True)
    retriever = ProductRetriever(products)
    orchestrator = RecommendationOrchestrator(products)
    docs = (products["product_name"] + " " + products["description"] + " " + products["specifications"])
    keyword_docs = docs.str.casefold()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(docs)
    measurements = []
    detail_rows = []
    for item in EVAL_QUERIES:
        relevant = set(products.loc[products["category"] == item["category"], "product_id"])
        start = time.perf_counter()
        keyword = products.loc[keyword_docs.str.contains(item["category"].split()[0].casefold(), regex=False)].head(5)
        keyword_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        scores = cosine_similarity(vectorizer.transform([item["query"]]), matrix).ravel()
        tfidf_ids = products.assign(_score=scores).sort_values("_score", ascending=False)["product_id"].head(5).tolist()
        tfidf_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        agentic = orchestrator.recommend(item["query"], CustomerContext(budget=item["budget"]), top_k=5)
        agentic_ms = (time.perf_counter() - start) * 1000
        category_pool = retriever.search(item["query"], category=item["category"], limit=len(products))
        context_ids = category_pool["product_id"].head(5).tolist()
        agentic_ids = [product["product_id"] for product in agentic["recommendations"]]
        # The category relevance labels are explicit synthetic intent labels, not human judgments.
        for name, ids, elapsed in [("Keyword", keyword["product_id"].tolist(), keyword_ms),
                                   ("TF-IDF", tfidf_ids, tfidf_ms),
                                   ("Context-aware TF-IDF", context_ids, tfidf_ms),
                                   ("Five-agent ranking", agentic_ids, agentic_ms)]:
            scores_for_run = _metrics(ids, relevant, 5)
            budget_satisfaction = (float(products.set_index("product_id").loc[ids, "price"].le(item["budget"]).mean()) if ids else 0.0)
            measurements.append({"method": name, **scores_for_run, "latency_ms_mean": elapsed,
                                 "budget_satisfaction": budget_satisfaction})
            detail_rows.append({"query": item["query"], "method": name, "recommended_product_ids": ", ".join(ids),
                                "relevant_category": item["category"], **scores_for_run,
                                "latency_ms": elapsed, "budget_satisfaction": budget_satisfaction})
    metrics = pd.DataFrame(measurements).groupby("method", as_index=False).mean(numeric_only=True)
    return metrics, pd.DataFrame(detail_rows)
