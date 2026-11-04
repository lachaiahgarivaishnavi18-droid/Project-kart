from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from recommender.catalog import ensure_catalogue
from recommender.evaluation import evaluate

products = ensure_catalogue(ROOT / "data" / "products.csv")
metrics, rows = evaluate(products)
out = ROOT / "outputs" / "evaluation"
out.mkdir(parents=True, exist_ok=True)
metrics.to_csv(out / "metrics.csv", index=False)
rows.to_csv(out / "query_results.csv", index=False)
print(metrics.to_string(index=False))