# Data Dictionary

| Field | Type | Meaning |
|---|---|---|
| `product_id` | string | Stable synthetic product identifier (`SYN-*`). |
| `product_name` | string | Fictional brand and product-family label. |
| `category` | string | One of six synthetic categories. |
| `brand` | string | One of six invented brand names. |
| `price` | integer | Fictional price in Indian rupees (₹). |
| `description` | string | Generated catalogue description; not independently verified. |
| `specifications` | string | Semicolon-separated generated feature text. |
| `rating` | float | Synthetic value on a 0–5 scale. |
| `review_count` | integer | Synthetic count; not consumer reviews. |
| `availability` | string | Synthetic availability label. |
| `channel` | string | Synthetic channel: website, mobile application, or physical store. |
| `source` | string | Always `synthetic demonstration data`. |

Validation checks required columns, removes duplicate `product_id` values, coerces numeric fields, drops rows missing required identifiers/price/rating, bounds price to non-negative and rating to 0–5, and fills optional text fields with empty strings. The source and limitations are detailed in [SOURCE.md](SOURCE.md).