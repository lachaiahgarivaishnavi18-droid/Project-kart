"""Check catalogue coverage and detect missing or duplicated product photos."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "data" / "products.csv"
MANIFEST = ROOT / "assets" / "products" / "product_image_mapping.json"


def _difference_hash(path: Path) -> str:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("L").resize((9, 8))
        pixels = image.tobytes()
    value = 0
    for row in range(8):
        for column in range(8):
            value = (value << 1) | int(
                pixels[row * 9 + column] >= pixels[row * 9 + column + 1]
            )
    return f"{value:016x}"


def validate_mapping(root: Path = ROOT) -> tuple[list[str], dict]:
    catalogue_path = root / "data" / "products.csv"
    manifest_path = root / "assets" / "products" / "product_image_mapping.json"
    with catalogue_path.open(encoding="utf-8", newline="") as catalogue:
        products = list(csv.DictReader(catalogue))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mappings = manifest.get("product_images", {})
    errors = []
    product_ids = {product["product_id"] for product in products}

    missing_ids = sorted(product_ids - set(mappings))
    extra_ids = sorted(set(mappings) - product_ids)
    if missing_ids:
        errors.append(f"Missing product-ID mappings: {', '.join(missing_ids)}")
    if extra_ids:
        errors.append(f"Mappings for unknown product IDs: {', '.join(extra_ids)}")

    catalogue_by_id = {product["product_id"]: product for product in products}
    path_groups = defaultdict(list)
    file_hash_groups = defaultdict(list)
    visual_hash_groups = defaultdict(list)
    for product_id, mapping in mappings.items():
        product = catalogue_by_id.get(product_id)
        if product and mapping.get("category") != product["category"]:
            errors.append(
                f"{product_id} is categorized as {mapping.get('category')!r}, "
                f"not {product['category']!r}."
            )
        relative_path = mapping.get("path")
        if not relative_path:
            errors.append(f"{product_id} has no image path.")
            continue
        image_path = (root / relative_path).resolve()
        if not image_path.is_relative_to(root.resolve()):
            errors.append(f"{product_id} has an image path outside the project.")
            continue
        if not image_path.is_file():
            errors.append(f"{product_id} image file is missing: {relative_path}")
            continue
        path_groups[relative_path].append(product_id)
        try:
            with Image.open(image_path) as image:
                image.verify()
            image_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
            file_hash_groups[image_hash].append(product_id)
            visual_hash_groups[_difference_hash(image_path)].append(product_id)
        except (OSError, ValueError) as error:
            errors.append(f"{product_id} image is unreadable: {error}")

    allowed_groups = {
        frozenset(group.get("product_ids", []))
        for group in manifest.get("allowed_shared_groups", [])
        if group.get("reason")
    }
    for label, groups in (
        ("image path", path_groups),
        ("file SHA-256", file_hash_groups),
        ("visual difference hash", visual_hash_groups),
    ):
        for products_sharing_image in groups.values():
            if len(products_sharing_image) > 1 and frozenset(products_sharing_image) not in allowed_groups:
                errors.append(f"Duplicate {label}: {', '.join(sorted(products_sharing_image))}")

    result = {
        "products_checked": len(products),
        "mapped_products": len(set(mappings) & product_ids),
        "unique_paths": len(path_groups),
        "unique_file_hashes": len(file_hash_groups),
        "unique_visual_hashes": len(visual_hash_groups),
        "missing_images": sum("image file is missing" in error for error in errors),
        "duplicate_groups": sum("Duplicate " in error for error in errors),
        "errors": errors,
    }
    return errors, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root to validate.")
    args = parser.parse_args()
    errors, result = validate_mapping(args.root.resolve())
    print(
        "Checked {products_checked} products: {mapped_products} mapped, "
        "{unique_paths} unique paths, {unique_file_hashes} unique file hashes, "
        "{unique_visual_hashes} unique visual hashes, {missing_images} missing images, "
        "{duplicate_groups} duplicate groups.".format(**result)
    )
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
