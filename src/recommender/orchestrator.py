"""Central coordination and observable trace for the five agents."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .agents import (CustomerContext, CustomerContextAgent, ExplanationAgent,
                     ProductRetrievalAgent, QueryUnderstandingAgent, RecommendationRankingAgent)
from .catalog import ProductRetriever


class RecommendationOrchestrator:
    def __init__(self, products):
        retriever = ProductRetriever(products)
        self.query_agent = QueryUnderstandingAgent()
        self.context_agent = CustomerContextAgent()
        self.retrieval_agent = ProductRetrievalAgent(retriever)
        self.ranking_agent = RecommendationRankingAgent()
        self.explanation_agent = ExplanationAgent()

    def recommend(self, query: str, context: CustomerContext | None = None,
                  budget_override: float | None = None, top_k: int = 5) -> dict[str, Any]:
        trace = []
        parsed = self.query_agent.run(query, budget_override)
        trace.append({"agent": "Query Understanding Agent", "status": "complete", "detail": f"Detected category: {parsed['category'] or 'not specified'}; budget: {parsed['budget'] if parsed['budget'] is not None else 'not specified'}; keywords: {', '.join(parsed['keywords'][:8])}"})
        customer = self.context_agent.run(context, parsed)
        trace.append({"agent": "Customer Context Agent", "status": "complete", "detail": f"Channel: {customer.channel}; brand preferences: {', '.join(customer.preferred_brands) or 'none'}; explicit preferences: {', '.join(customer.preferences) or 'none'}"})
        retrieval_query = " ".join([query, *customer.preferences])
        candidates = self.retrieval_agent.run(retrieval_query, parsed)
        preference_detail = ", ".join(customer.preferences) or "none"
        trace.append({"agent": "Product Retrieval Agent", "status": "complete", "detail": f"TF-IDF catalogue search returned {len(candidates)} candidates; metadata category filter: {parsed['category'] or 'none'}; explicit preference terms: {preference_detail}"})
        ranked = self.ranking_agent.run(candidates, customer, top_k)
        trace.append({"agent": "Recommendation and Ranking Agent", "status": "complete", "detail": "Weighted score = 0.50 relevance + 0.20 rating + 0.15 budget + 0.10 availability + 0.05 explicit preference (brand/channel)"})
        recommendations = ranked.to_dict(orient="records")
        for product in recommendations:
            product["explanation"] = self.explanation_agent.run(product, query, customer)
        trace.append({"agent": "Explanation Agent", "status": "complete", "detail": f"Generated evidence-grounded explanations for {len(recommendations)} products using catalogue fields only"})
        return {"query": query, "context": asdict(customer), "parsed_query": parsed,
                "retrieved": candidates.to_dict(orient="records"), "recommendations": recommendations,
                "trace": trace}
