# Dataset Source and Provenance

`products.csv` is a synthetic demonstration dataset generated locally by `build_demo_catalogue()` in `src/recommender/catalog.py`. It contains 120 deterministic records across six invented product categories. Names, brands, specifications, descriptions, prices, ratings, and review counts are fictional and do not describe an actual retailer or product.

There is no third-party dataset, restricted licence, customer record, or external product feed. The dataset generator is the source of truth; `ensure_catalogue()` creates the CSV if it is absent. Re-run `python scripts/generate_demo_outputs.py` to create the catalogue and sample outputs.

## Limitations

The catalogue is small and templated. Its regular vocabulary and category assignments make it suitable for software demonstrations, not market analysis or claims about shopper behavior. Ratings, review counts, stock, and channel availability are synthetic and must not be interpreted as actual product facts.