"""Download and regenerate the explicit product-ID photo mapping."""

import csv
from html import unescape
import io
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "data" / "products.csv"
OUTPUT = ROOT / "assets" / "products"
MANIFEST_PATH = OUTPUT / "product_image_mapping.json"
SOURCES_PATH = OUTPUT / "product_image_sources.json"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = (
    "ContextCartProductImages/1.0 "
    "(https://github.com/lachaiahgarivaishnavi18-droid/Project-kart)"
)
THUMBNAIL_WIDTH = 1280
CATEGORY_FOLDERS = {
    "Headphones": "headphones",
    "Backpacks": "backpacks",
    "Smartphones": "smartphones",
    "Running Shoes": "footwear",
    "Water Bottles": "accessories",
    "Watches": "accessories",
}

# Preserve earlier category photos as an explicit fallback for future SKUs
# without a product-ID assignment. Current catalogue products do not use them.
LEGACY_CATEGORY_IMAGES = {
    "Headphones": {
        "path": "assets/products/headphones/wireless-over-ear-headphones.jpg",
        "alt": "Over-ear headphones, category reference.",
        "source": "Unsplash",
        "photo_id": "photo-1505740420928-5e560c06d30e",
        "source_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?fm=jpg&fit=max&w=1600&q=88",
        "license": "Unsplash License",
        "license_url": "https://unsplash.com/license",
        "attribution_required": False,
    },
    "Backpacks": {
        "path": "assets/products/backpacks/travel-backpack.jpg",
        "alt": "Travel backpack, category reference.",
        "source": "Unsplash",
        "photo_id": "photo-1553062407-98eeb64c6a62",
        "source_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?fm=jpg&fit=max&w=1600&q=88",
        "license": "Unsplash License",
        "license_url": "https://unsplash.com/license",
        "attribution_required": False,
    },
    "Running Shoes": {
        "path": "assets/products/footwear/red-running-shoe.jpg",
        "alt": "Running shoe, category reference.",
        "source": "Unsplash",
        "photo_id": "photo-1542291026-7eec264c27ff",
        "source_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?fm=jpg&fit=max&w=1600&q=88",
        "license": "Unsplash License",
        "license_url": "https://unsplash.com/license",
        "attribution_required": False,
    },
    "Smartphones": {
        "path": "assets/products/smartphones/modern-smartphone.jpg",
        "alt": "Smartphone, category reference.",
        "source": "Unsplash",
        "photo_id": "photo-1511707171634-5f897ff02aa9",
        "source_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?fm=jpg&fit=max&w=1600&q=88",
        "license": "Unsplash License",
        "license_url": "https://unsplash.com/license",
        "attribution_required": False,
    },
    "Watches": {
        "path": "assets/products/accessories/smartwatch.jpg",
        "alt": "Smartwatch, category reference.",
        "source": "Unsplash",
        "photo_id": "photo-1523275335684-37898b6baf30",
        "source_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?fm=jpg&fit=max&w=1600&q=88",
        "license": "Unsplash License",
        "license_url": "https://unsplash.com/license",
        "attribution_required": False,
    },
    "Water Bottles": {
        "path": "assets/products/accessories/insulated-water-bottle.jpg",
        "alt": "Reusable water bottle, category reference.",
        "source": "Unsplash",
        "photo_id": "photo-1602143407151-7111542de6e8",
        "source_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?fm=jpg&fit=max&w=1600&q=88",
        "license": "Unsplash License",
        "license_url": "https://unsplash.com/license",
        "attribution_required": False,
    },
}


def _request_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def _plain_text(value: str) -> str:
    return unescape(re.sub(r"<[^>]*>", "", value)).strip()


def get_file_metadata(titles: list[str]) -> dict[str, dict]:
    records = {}
    for offset in range(0, len(titles), 50):
        batch = titles[offset : offset + 50]
        query = urlencode({
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": THUMBNAIL_WIDTH,
            "titles": "|".join(f"File:{title}" for title in batch),
        })
        data = _request_json(f"{COMMONS_API}?{query}")
        for page in data["query"]["pages"]:
            image_info = page.get("imageinfo")
            if not image_info:
                continue
            info = image_info[0]
            metadata = info.get("extmetadata", {})
            license_name = _plain_text(metadata.get("LicenseShortName", {}).get("value", ""))
            if not (
                license_name.startswith("CC BY")
                or license_name.startswith("CC0")
                or license_name.casefold().startswith("public domain")
            ) or "NC" in license_name or "ND" in license_name:
                raise ValueError(f"Unacceptable or missing license for {page['title']}: {license_name!r}")
            if info.get("width", 0) < 300 or info.get("height", 0) < 300:
                raise ValueError(
                    f"Image is too small for product presentation: {page['title']} "
                    f"({info.get('width')}x{info.get('height')})."
                )
            records[page["title"].removeprefix("File:")] = {
                "title": page["title"].removeprefix("File:"),
                "source_url": info["url"],
                "thumbnail_url": info.get("thumburl", info["url"]),
                "source_page": f"https://commons.wikimedia.org/wiki/{quote(page['title'].replace(' ', '_'))}",
                "license": license_name,
                "license_url": _plain_text(metadata.get("LicenseUrl", {}).get("value", "")),
                "artist": _plain_text(metadata.get("Artist", {}).get("value", "")),
                "attribution": _plain_text(metadata.get("Attribution", {}).get("value", "")),
                "width": info["width"],
                "height": info["height"],
            }
        time.sleep(2)
    missing = set(titles) - set(records)
    if missing:
        raise ValueError(f"Commons did not return these curated files: {sorted(missing)}")
    return records


def _download_and_normalize(photo: dict, destination: Path, *, force: bool = False) -> None:
    if destination.is_file() and not force:
        try:
            with Image.open(destination) as existing:
                existing.verify()
            return
        except (OSError, ValueError):
            destination.unlink()

    request = Request(photo["thumbnail_url"], headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=60) as response:
                content = response.read()
            break
        except HTTPError as error:
            if error.code != 429 or attempt == 5:
                raise RuntimeError(f"Could not download {photo['title']}: {error}") from error
            time.sleep(min(30 * (attempt + 1), 120))

    with Image.open(io.BytesIO(content)) as opened:
        image = ImageOps.exif_transpose(opened)
        if image.width < 300 or image.height < 300:
            raise ValueError(f"Downloaded thumbnail is too small: {photo['title']}")
        image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_WIDTH), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="JPEG", quality=90, optimize=True)
    time.sleep(1)


def _write_attribution(product_images: dict[str, dict]) -> None:
    lines = [
        "# Product Photograph Sources and Licensing",
        "",
        "The synthetic catalogue has no image URLs. Each current SKU is mapped by product ID "
        "to a distinct locally stored Wikimedia Commons photograph of a physical product in "
        "the same category. These are category references, not the exact synthetic catalogue "
        "model or brand.",
        "",
        "Images are resized local derivatives of the cited Commons originals. The file-specific "
        "creator/attribution and license details below come from Commons metadata. Preserve "
        "the listed attribution and license when redistributing the photos.",
        "",
        "| Product ID | Local photo | Commons file | Creator | License | Source |",
        "|---|---|---|---|---|---|",
    ]
    for product_id, image in sorted(product_images.items()):
        creator = image["artist"] or image["attribution"] or "Not specified in Commons metadata"
        lines.append(
            f"| {product_id} | `{Path(image['path']).name}` | "
            f"[{image['source_title']}]({image['source_page']}) | "
            f"{creator.replace('|', '&#124;')} | [{image['license']}]({image['license_url']}) | "
            f"[Wikimedia Commons]({image['source_page']}) |"
        )
    (OUTPUT / "ATTRIBUTION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    with CATALOGUE.open(encoding="utf-8", newline="") as catalogue:
        products = list(csv.DictReader(catalogue))
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    catalogue_ids = {product["product_id"] for product in products}
    if set(sources) != catalogue_ids:
        raise ValueError(
            f"Product-ID sources must exactly match the catalogue. "
            f"Missing: {sorted(catalogue_ids - set(sources))}; "
            f"unknown: {sorted(set(sources) - catalogue_ids)}"
        )
    previous_mappings = {}
    if MANIFEST_PATH.is_file():
        previous_mappings = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")).get(
            "product_images", {}
        )

    titles = []
    for product in products:
        source = sources[product["product_id"]]
        if source.get("category") != product["category"]:
            raise ValueError(
                f"{product['product_id']} source category {source.get('category')!r} "
                f"does not match catalogue category {product['category']!r}."
            )
        if product["category"] not in CATEGORY_FOLDERS:
            raise ValueError(f"No product image folder for category {product['category']!r}.")
        title = source.get("source_title", "").strip()
        if not title:
            raise ValueError(f"{product['product_id']} has no Commons source title.")
        titles.append(title)
    if len(set(titles)) != len(titles):
        raise ValueError("A Commons photograph is assigned to more than one product ID.")

    metadata = get_file_metadata(titles)
    product_images = {}
    download_jobs = []
    for product in products:
        product_id = product["product_id"]
        source_title = sources[product_id]["source_title"]
        source = metadata[source_title]
        path = (
            f"assets/products/{CATEGORY_FOLDERS[product['category']]}/"
            f"{product_id}.jpg"
        )
        entry = {
            "category": product["category"],
            "path": path,
            "alt": f"{product['category']} reference photograph: {source_title}",
            "source": "Wikimedia Commons",
            "source_title": source_title,
            "source_url": source["source_url"],
            "source_page": source["source_page"],
            "license": source["license"],
            "license_url": source["license_url"],
            "artist": source["artist"],
            "attribution": source["attribution"],
            "source_dimensions": [source["width"], source["height"]],
            "product_identity_note": (
                "Category-reference photograph only; not a photograph of the synthetic "
                "catalogue SKU or its fictional brand."
            ),
        }
        product_images[product_id] = entry
        force = previous_mappings.get(product_id, {}).get("source_title") != source_title
        download_jobs.append((source, ROOT / path, force))

    for source, destination, force in download_jobs:
        _download_and_normalize(source, destination, force=force)

    manifest = {
        "catalogue_path": "data/products.csv",
        "unique_image_policy": "one distinct, locally stored photograph per product ID",
        "allowed_shared_groups": [],
        "license": "See per-image license and attribution metadata.",
        "category_images": LEGACY_CATEGORY_IMAGES,
        "product_images": product_images,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_attribution(product_images)
    downloaded = sum(force for _, _, force in download_jobs)
    print(
        f"Downloaded {downloaded} and verified {len(download_jobs) - downloaded} "
        "Commons product photographs."
    )
    print(f"Mapped {len(product_images)} product IDs in {MANIFEST_PATH.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
