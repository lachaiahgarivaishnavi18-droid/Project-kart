from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from recommender.catalog import build_demo_catalogue
from recommender.evaluation import evaluate


def test_evaluation_returns_finite_metrics_for_all_baselines():
    metrics, details = evaluate(build_demo_catalogue())
    assert set(metrics["method"]) == {"Keyword", "TF-IDF", "Context-aware TF-IDF", "Five-agent ranking"}
    assert len(details) == 16
    assert metrics.select_dtypes("number").notna().all().all()