import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw
from streamlit.testing.v1 import AppTest


def test_product_photograph_mapping_covers_catalogue_with_local_jpegs():
    root = Path(__file__).resolve().parents[1]
    with (root / "data" / "products.csv").open(encoding="utf-8", newline="") as catalogue:
        products = list(csv.DictReader(catalogue))
    manifest = json.loads(
        (root / "assets" / "products" / "product_image_mapping.json").read_text(encoding="utf-8")
    )
    sources = json.loads(
        (root / "assets" / "products" / "product_image_sources.json").read_text(encoding="utf-8")
    )
    mappings = manifest["product_images"]
    assert set(mappings) == {product["product_id"] for product in products}
    assert set(sources) == set(mappings)
    assert len({mapping["source_title"] for mapping in mappings.values()}) == len(products)
    paths = []
    image_hashes = []
    for product in products:
        mapping = mappings[product["product_id"]]
        assert sources[product["product_id"]] == {
            "category": product["category"],
            "source_title": mapping["source_title"],
        }
        assert mapping["category"] == product["category"]
        assert mapping["source"] == "Wikimedia Commons"
        assert mapping["license"]
        assert mapping["source_page"].startswith("https://commons.wikimedia.org/wiki/")
        image = root / mapping["path"]
        assert image.is_file()
        assert image.read_bytes().startswith(b"\xff\xd8\xff")
        paths.append(mapping["path"])
        image_hashes.append(hashlib.sha256(image.read_bytes()).hexdigest())
    assert len(set(paths)) == len(products)
    assert len(set(image_hashes)) == len(products)
    assert len(manifest["category_images"]) == len({product["category"] for product in products})
    shoe_ids = ["SYN-04-004", "SYN-04-002", "SYN-04-020"]
    shoe_paths = [mappings[product_id]["path"] for product_id in shoe_ids]
    shoe_hashes = [hashlib.sha256((root / path).read_bytes()).hexdigest() for path in shoe_paths]
    assert len(set(shoe_paths)) == 3
    assert len(set(shoe_hashes)) == 3


def test_product_photo_validator_reports_success():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_product_images.py")],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "120 products" in result.stdout


def test_product_photo_validator_detects_duplicate_files(tmp_path):
    scripts_path = Path(__file__).resolve().parents[1] / "scripts"
    sys.path.insert(0, str(scripts_path))
    from validate_product_images import validate_mapping

    (tmp_path / "data").mkdir()
    image_path = tmp_path / "duplicate.jpg"
    image = Image.new("RGB", (256, 256), "white")
    ImageDraw.Draw(image).ellipse((64, 64, 192, 192), fill="navy")
    image.save(image_path, format="JPEG")
    (tmp_path / "data" / "products.csv").write_text(
        "product_id,category\nSYN-04-001,Running Shoes\nSYN-04-002,Running Shoes\n",
        encoding="utf-8",
    )
    manifest_dir = tmp_path / "assets" / "products"
    manifest_dir.mkdir(parents=True)
    mapping = {
        "category": "Running Shoes",
        "path": "duplicate.jpg",
    }
    (manifest_dir / "product_image_mapping.json").write_text(
        json.dumps({
            "product_images": {"SYN-04-001": mapping, "SYN-04-002": mapping},
            "allowed_shared_groups": [],
        }),
        encoding="utf-8",
    )

    errors, _ = validate_mapping(tmp_path)
    assert any("Duplicate image path" in error for error in errors)
    assert any("Duplicate file SHA-256" in error for error in errors)
    assert any("Duplicate visual difference hash" in error for error in errors)


def test_home_navigation_and_example_recommendation_render():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not app.exception
    expected_pages = {
        "▦  Dashboard", "⌕  Product Discovery", "✧  AI Shopping Assistant",
        "☆  Recommendations", "▣  Product Details", "⇄  Product Comparison", "⌖  Inventory & Store Availability",
        "▥  Evaluation Dashboard", "⚙  Settings", "ⓘ  About",
    }
    assert set(app.sidebar.radio[0].options) == expected_pages
    app.form_submit_button[0].click().run()
    assert app.sidebar.radio[0].value == "⌕  Product Discovery"
    app.text_input[0].set_value("Lightweight wireless headphones under 5000")
    app.form_submit_button[0].click().run()
    assert not app.exception
    assert app.session_state["last_result"]["recommendations"]


def test_comparison_and_evaluation_pages_render():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.sidebar.radio[0].set_value("⌕  Product Discovery").run()
    app.text_input[0].set_value("Lightweight wireless headphones under 5000")
    app.form_submit_button[0].click().run()
    for _ in range(2):
        next(button for button in app.button if button.label == "＋ Compare").click().run()
    assert len(app.session_state["comparison_ids"]) == 2
    app.sidebar.radio[0].set_value("⇄  Product Comparison").run()
    assert not app.exception
    assert len(app.dataframe) >= 1
    assert "Recommendation score" in app.dataframe[0].value.index
    app.sidebar.radio[0].set_value("▥  Evaluation Dashboard").run()
    assert not app.exception
    assert len(app.dataframe) >= 2
    assert any(metric.label == "Response latency" for metric in app.metric)
    assert any(metric.label == "Agent execution status" for metric in app.metric)


def test_all_navigation_pages_and_local_assistant_render():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    for label in app.sidebar.radio[0].options:
        app.sidebar.radio[0].set_value(label).run()
        assert not app.exception, f"Page failed to render: {label}"

    app.sidebar.radio[0].set_value("✧  AI Shopping Assistant").run()
    app.chat_input[0].set_value("wireless headphones under 5000").run()
    assert not app.exception
    messages = app.session_state["chat_messages"]
    assert messages[-1]["result"]["recommendations"]
    assert messages[-1]["result"]["trace"]


def test_product_details_open_from_discovery_card():
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.sidebar.radio[0].set_value("⌕  Product Discovery").run()
    app.text_input[0].set_value("wireless headphones under 5000")
    app.form_submit_button[0].click().run()
    next(button for button in app.button if button.label == "View product details").click().run()
    assert not app.exception
    assert app.sidebar.radio[0].value == "▣  Product Details"
    image_manifest = json.loads(
        (root / "assets" / "products" / "product_image_mapping.json").read_text(encoding="utf-8")
    )
    assert (root / image_manifest["product_images"]["SYN-01-001"]["path"]).is_file()
    assert not any("Product image not supplied" in element.value for element in app.markdown)
    assert any("Why This Product Is Recommended" in element.value for element in app.markdown)
    assert any("Shopping query match" in element.value for element in app.markdown)
    assert any("Catalogue evidence and citation" in element.value for element in app.markdown)
    assert any(metric.label == "Delivery options" for metric in app.metric)
    assert any(metric.label == "Pickup availability" for metric in app.metric)
    assert any(button.label == "Add to Comparison" for button in app.button)
    assert any(button.label == "Back to Recommendations" for button in app.button)
    assert len(app.dataframe) >= 1
    next(button for button in app.button if button.label == "View Related Products ↓").click().run()
    assert app.session_state["show_related_products"]
    next(button for button in app.button if button.label == "Back to Recommendations").click().run()
    assert app.sidebar.radio[0].value == "☆  Recommendations"