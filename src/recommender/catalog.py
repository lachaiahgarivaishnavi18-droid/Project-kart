"""Synthetic catalogue creation, validation, and TF-IDF retrieval."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REQUIRED_COLUMNS = {
    "product_id", "product_name", "category", "brand", "price", "description",
    "specifications", "rating", "review_count", "availability", "channel", "source",
}

PRODUCT_FAMILIES = {
    "Headphones": ("headphones", "audio", 900, 5200, ["wireless", "noise cancelling", "lightweight", "long battery", "foldable", "clear calls"]),
    "Backpacks": ("backpack", "bags", 700, 4200, ["lightweight", "water resistant", "laptop sleeve", "travel friendly", "multiple pockets", "durable fabric"]),
    "Smartphones": ("smartphone", "electronics", 7500, 42000, ["long battery", "fast charging", "OLED display", "sharp camera", "5G", "compact design"]),
    "Running Shoes": ("running shoes", "footwear", 1200, 6500, ["breathable mesh", "cushioned sole", "lightweight", "grip", "flexible fit", "daily running"]),
    "Water Bottles": ("water bottle", "outdoors", 250, 1800, ["insulated", "leak resistant", "lightweight", "stainless steel", "wide mouth", "reusable"]),
    "Watches": ("smartwatch", "wearables", 1800, 12000, ["fitness tracking", "water resistant", "long battery", "bright display", "sleep tracking", "GPS"]),
}
BRANDS = ["Northstar", "Mosaic", "Pioneer", "Evertrail", "Solace", "Vertex"]


def build_demo_catalogue() -> pd.DataFrame:
    """Return 120 deterministic synthetic products; no retailer data is used."""
    records: list[dict[str, Any]] = []
    for family_index, (category, family) in enumerate(PRODUCT_FAMILIES.items()):
        noun, department, low, high, features = family
        for variant in range(20):
            brand = BRANDS[(variant + family_index) % len(BRANDS)]
            feature_a = features[variant % len(features)]
            feature_b = features[(variant * 3 + 2) % len(features)]
            price = low + ((variant * 431 + family_index * 277) % (high - low + 1))
            rating = round(3.2 + ((variant * 7 + family_index * 3) % 18) / 10, 1)
            records.append({
                "product_id": f"SYN-{family_index + 1:02d}-{variant + 1:03d}",
                "product_name": f"{brand} {noun.title()} {variant + 1:02d}",
                "category": category,
                "brand": brand,
                "price": price,
                "description": f"{brand} {noun} for {department}, featuring {feature_a} and {feature_b}.",
                "specifications": f"{feature_a}; {feature_b}",
                "rating": rating,
                "review_count": 12 + ((variant * 37 + family_index * 19) % 1800),
                "availability": "In stock" if variant % 7 else "Limited stock",
                "channel": ["website", "mobile application", "physical store"][(variant + family_index) % 3],
                "source": "synthetic demonstration data",
            })
    return pd.DataFrame.from_records(records)


def validate_catalogue(products: pd.DataFrame) -> pd.DataFrame:
    missing_columns = REQUIRED_COLUMNS - set(products.columns)
    if missing_columns:
        raise ValueError(f"Catalogue is missing columns: {', '.join(sorted(missing_columns))}")
    clean = products.copy()
    clean = clean.drop_duplicates(subset="product_id")
    clean["price"] = pd.to_numeric(clean["price"], errors="coerce")
    clean["rating"] = pd.to_numeric(clean["rating"], errors="coerce")
    clean["review_count"] = pd.to_numeric(clean["review_count"], errors="coerce").fillna(0)
    clean = clean.dropna(subset=["product_id", "product_name", "price", "rating"])
    clean = clean[(clean["price"] >= 0) & clean["rating"].between(0, 5)]
    for column in ("description", "specifications", "category", "brand", "availability", "channel", "source"):
        clean[column] = clean[column].fillna("").astype(str)
    return clean.reset_index(drop=True)


def ensure_catalogue(path: Path) -> pd.DataFrame:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        build_demo_catalogue().to_csv(path, index=False)
    return validate_catalogue(pd.read_csv(path))


class ProductRetriever:
    def __init__(self, products: pd.DataFrame):
        self.products = validate_catalogue(products)
        self.documents = (
            self.products["product_name"] + " " + self.products["category"] + " "
            + self.products["brand"] + " " + self.products["description"] + " "
            + self.products["specifications"]
        )
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query: str, *, category: str | None = None, limit: int = 30) -> pd.DataFrame:
        if not query.strip():
            return self.products.iloc[0:0].assign(retrieval_score=pd.Series(dtype=float))
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        results = self.products.assign(retrieval_score=scores)
        if category and category != "All categories":
            results = results[results["category"].str.casefold() == category.casefold()]
        return results.sort_values(["retrieval_score", "rating"], ascending=False).head(limit).reset_index(drop=True)
