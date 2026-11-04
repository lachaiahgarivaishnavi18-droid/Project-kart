"""Run the requested sample query and save actual results as JSON and CSV."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from recommender.catalog import ensure_catalogue
from recommender.orchestrator import RecommendationOrchestrator

products = ensure_catalogue(ROOT / "data" / "products.csv")
result = RecommendationOrchestrator(products).recommend(
    "Lightweight wireless headphones for travel under 3000", top_k=5)
result["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
out = ROOT / "outputs" / "examples"
out.mkdir(parents=True, exist_ok=True)
(out / "recommendation.json").write_text(json.dumps(result, indent=2, default=str) + "\n")

if len(result["recommendations"]) >= 2:
    comparison = result["recommendations"][:2]
    (out / "comparison.json").write_text(json.dumps({
        "generated_at_utc": result["generated_at_utc"], "query": result["query"],
        "products": [{key: item[key] for key in ("product_id", "product_name", "brand", "price", "rating", "specifications", "availability", "description", "explanation")} for item in comparison],
        "comparison_note": "Advantages and limitations are restricted to the listed synthetic catalogue fields.",
    }, indent=2) + "\n")
(out / "context_explanation.json").write_text(json.dumps({
    "generated_at_utc": result["generated_at_utc"], "query": result["query"],
    "customer_context": result["context"], "retrieved_evidence": result["retrieved"][:10],
    "ranking_reasons": [step for step in result["trace"] if step["agent"] in ("Recommendation and Ranking Agent", "Explanation Agent")],
    "recommendations": result["recommendations"],
}, indent=2, default=str) + "\n")
print(f"Generated recommendation for {len(result['recommendations'])} products in {out}")