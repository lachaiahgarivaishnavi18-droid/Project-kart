"""Specialized deterministic agents for the recommendation workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from .catalog import PRODUCT_FAMILIES, ProductRetriever


@dataclass
class CustomerContext:
    budget: float | None = None
    preferred_brands: list[str] = field(default_factory=list)
    channel: str = "Any channel"
    preferences: list[str] = field(default_factory=list)


class QueryUnderstandingAgent:
    def run(self, query: str, budget_override: float | None = None) -> dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("Enter a shopping query to get recommendations.")
        budget_match = re.search(r"(?:under|below|less than|max(?:imum)?|budget(?: of)?)\s*₹?\s*([\d,]+(?:\.\d+)?)", query, re.I)
        parsed_budget = float(budget_match.group(1).replace(",", "")) if budget_match else None
        categories = [name for name in PRODUCT_FAMILIES if name.casefold() in query.casefold()]
        if not categories:
            category_terms = {"headphone": "Headphones", "backpack": "Backpacks", "phone": "Smartphones", "shoe": "Running Shoes", "bottle": "Water Bottles", "watch": "Watches"}
            categories = [category for term, category in category_terms.items() if term in query.casefold()]
        words = re.findall(r"[a-zA-Z0-9]+", query.casefold())
        stop = {"for", "the", "and", "with", "under", "below", "less", "than", "₹"}
        return {"keywords": [word for word in words if word not in stop and not word.isdigit()],
                "category": categories[0] if categories else None,
                "budget": budget_override if budget_override is not None else parsed_budget,
                "budget_source": "user setting" if budget_override is not None else ("query" if parsed_budget is not None else "not specified")}


class CustomerContextAgent:
    def run(self, preferences: CustomerContext | None, parsed: dict[str, Any]) -> CustomerContext:
        supplied = preferences or CustomerContext()
        return CustomerContext(budget=parsed["budget"] if parsed["budget"] is not None else supplied.budget,
                               preferred_brands=supplied.preferred_brands,
                               channel=supplied.channel,
                               preferences=supplied.preferences)


class ProductRetrievalAgent:
    def __init__(self, retriever: ProductRetriever):
        self.retriever = retriever

    def run(self, query: str, parsed: dict[str, Any], limit: int = 30) -> pd.DataFrame:
        return self.retriever.search(query, category=parsed["category"], limit=limit)


class RecommendationRankingAgent:
    def run(self, candidates: pd.DataFrame, context: CustomerContext, top_k: int = 5) -> pd.DataFrame:
        if candidates.empty:
            return candidates.copy()
        ranked = candidates.copy()
        budget = context.budget
        if budget is not None:
            within_budget = ranked[ranked["price"] <= budget]
            if not within_budget.empty:
                ranked = within_budget.copy()
            ranked["budget_score"] = (ranked["price"] <= budget).astype(float)
            ranked["budget_score"] += (ranked["price"] <= budget * 1.1).astype(float) * 0.1
        else:
            ranked["budget_score"] = 0.5
        ranked["rating_score"] = ranked["rating"] / 5
        ranked["brand_score"] = ranked["brand"].str.casefold().isin({brand.casefold() for brand in context.preferred_brands}).astype(float)
        ranked["channel_score"] = 1.0 if context.channel == "Any channel" else ranked["channel"].str.casefold().eq(context.channel.casefold()).astype(float)
        ranked["preference_score"] = 0.5 * ranked["brand_score"] + 0.5 * ranked["channel_score"]
        ranked["availability_score"] = ranked["availability"].str.casefold().eq("in stock").astype(float)
        max_relevance = max(float(ranked["retrieval_score"].max()), 1e-9)
        ranked["relevance_score"] = ranked["retrieval_score"] / max_relevance
        ranked["ranking_score"] = (0.50 * ranked["relevance_score"] + 0.20 * ranked["rating_score"]
                                   + 0.15 * ranked["budget_score"] + 0.10 * ranked["availability_score"]
                                   + 0.05 * ranked["preference_score"])
        ranked["within_budget"] = True if budget is None else ranked["price"] <= budget
        return ranked.sort_values(["ranking_score", "rating"], ascending=False).head(top_k).reset_index(drop=True)


class ExplanationAgent:
    def run(self, product: dict[str, Any], query: str, context: CustomerContext) -> str:
        evidence = [str(product["description"]), str(product["specifications"])]
        reasons = []
        if product["retrieval_score"] > 0:
            reasons.append(f"its catalogue description matches the query (TF-IDF score {product['retrieval_score']:.3f})")
        reasons.append(f"catalogue rating {product['rating']}/5")
        if context.budget is not None:
            reasons.append("within the stated budget" if product["price"] <= context.budget else "above the stated budget")
        if product["brand"] in context.preferred_brands:
            reasons.append(f"preferred brand {product['brand']}")
        if context.channel != "Any channel" and product["channel"].casefold() == context.channel.casefold():
            reasons.append(f"available through the selected {context.channel} channel")
        return (f"{product['product_name']} is recommended because " + ", ".join(reasons)
                + f". Catalogue evidence: {' '.join(evidence)}. Availability: {product['availability']}. "
                + "No claims beyond the catalogue fields are inferred.")
