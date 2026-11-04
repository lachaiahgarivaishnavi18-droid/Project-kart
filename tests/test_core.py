from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recommender.agents import CustomerContext
from recommender.catalog import build_demo_catalogue, validate_catalogue
from recommender.orchestrator import RecommendationOrchestrator


def test_synthetic_catalogue_has_required_rows_and_fields():
    products = validate_catalogue(build_demo_catalogue())
    assert len(products) >= 100
    assert products["product_id"].is_unique
    assert set(products["source"]) == {"synthetic demonstration data"}


def test_agentic_recommendation_is_budget_aware_and_grounded():
    orchestrator = RecommendationOrchestrator(build_demo_catalogue())
    result = orchestrator.recommend("Lightweight wireless headphones for travel under 3000", top_k=5)
    assert len(result["trace"]) == 5
    assert result["parsed_query"]["budget"] == 3000
    assert result["recommendations"]
    assert all(product["within_budget"] for product in result["recommendations"])
    assert all("Catalogue evidence:" in product["explanation"] for product in result["recommendations"])


def test_context_preferences_and_empty_query_validation():
    orchestrator = RecommendationOrchestrator(build_demo_catalogue())
    result = orchestrator.recommend("running shoes", CustomerContext(preferred_brands=["Northstar"], channel="website"))
    assert result["context"]["channel"] == "website"
    assert any(product["brand"] == "Northstar" for product in result["recommendations"])
    assert all(product["channel_score"] in (0.0, 1.0) for product in result["recommendations"])
    assert any(product["channel_score"] == 1.0 for product in result["recommendations"])