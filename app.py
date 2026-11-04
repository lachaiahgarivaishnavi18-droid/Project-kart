from datetime import datetime
from html import escape
import json
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
PRODUCT_IMAGE_DIR = ROOT / "assets" / "products"
PRODUCT_IMAGE_MANIFEST = json.loads(
    (PRODUCT_IMAGE_DIR / "product_image_mapping.json").read_text(encoding="utf-8")
)
sys.path.insert(0, str(ROOT / "src"))

from recommender.agents import CustomerContext
from recommender.catalog import ensure_catalogue
from recommender.orchestrator import RecommendationOrchestrator

st.set_page_config(page_title="Context Cart | Product Intelligence", page_icon="C", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --navy: #10243a;
  --navy-soft: #1b3652;
  --teal: #087f82;
  --teal-light: #e8f5f4;
  --blue: #3878c7;
  --ink: #1d2b3a;
  --muted: #718096;
  --line: #e6ebf0;
  --surface: #ffffff;
  --canvas: #f5f8fb;
}
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], button, input, textarea { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, h4 { font-family: 'Manrope', sans-serif; color: var(--ink); letter-spacing: 0; }
.stApp { background: var(--canvas); color: var(--ink); }
[data-testid="stAppViewContainer"] > .main { background: var(--canvas); }
[data-testid="stMainBlockContainer"] { width: 100%; max-width: 1540px; padding: 1.5rem 2rem 3rem; }
[data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
[data-testid="stSidebar"] > div:first-child { background: var(--navy); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #d7e1eb; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fff; }
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: .28rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  padding: .72rem .82rem; border-radius: 10px; transition: background .18s ease, color .18s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #1a3652; color: #fff; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background: #174b5a; color: #fff; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p { color: #fff; font-weight: 700; }
[data-testid="stSidebar"] hr { border-color: #31465c; }
[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 1.05rem 1.15rem; box-shadow: 0 5px 18px rgba(19, 42, 64, .045); }
[data-testid="stMetricLabel"] { color: var(--muted); font-size: .82rem; }
[data-testid="stMetricValue"] { color: var(--navy); font-family: 'Manrope', sans-serif; font-size: 1.75rem; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 5px 18px rgba(19, 42, 64, .045); transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease; }
[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #cbd9e5; box-shadow: 0 9px 24px rgba(19, 42, 64, .075); }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div { border-radius: 7px; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button { border-radius: 9px; transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease; }
[data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(16, 36, 58, .12); }
.brand-mark { width: 38px; height: 38px; display: inline-flex; align-items: center; justify-content: center; border-radius: 11px; background: #20a5a4; color: white; font: 800 17px 'Manrope', sans-serif; margin-right: 9px; }
.brand-row { display: flex; align-items: center; padding: .55rem .1rem 1rem; }
.brand-title { color: white; font: 800 17px 'Manrope', sans-serif; }
.brand-subtitle { color: #a9bacb; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
.eyebrow { color: var(--teal); font-weight: 700; font-size: .77rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: .35rem; }
.page-title { color: var(--navy); font: 800 31px 'Manrope', sans-serif; line-height: 1.2; margin: .05rem 0 .45rem; }
.page-subtitle { color: var(--muted); font-size: 1rem; margin-bottom: 1.25rem; }
.hero { background: linear-gradient(110deg, #10243a 0%, #173c59 60%, #146b71 100%); color: white; padding: 2rem 2.2rem; border-radius: 18px; margin-bottom: 1.25rem; box-shadow: 0 12px 30px rgba(16, 36, 58, .14); }
.hero h1 { color: white; font-size: 31px; margin: .2rem 0 .45rem; }
.hero p { color: #dce8f1; max-width: 720px; margin: 0; }
.hero .eyebrow { color: #83d6d0; }
.section-title { color: var(--navy); font: 700 18px 'Manrope', sans-serif; margin: .45rem 0 .7rem; }
.product-name { color: var(--navy); font: 700 16px 'Manrope', sans-serif; line-height: 1.3; min-height: 42px; }
.product-meta { color: var(--muted); font-size: .85rem; }
.price { color: var(--navy); font: 800 22px 'Manrope', sans-serif; }
[data-testid="stImage"] { overflow: hidden; border-radius: 13px; background: linear-gradient(145deg, #f5f8fb, #e8f0f4); margin-bottom: .8rem; }
[data-testid="stImage"] img { width: 100%; height: 176px; object-fit: contain; display: block; padding: .3rem; }
.st-key-product-detail-image [data-testid="stImage"] img { height: min(38vw, 360px); min-height: 250px; }
.st-key-product-detail-image [data-testid="stImage"] { border: 1px solid var(--line); box-shadow: 0 8px 26px rgba(19, 42, 64, .07); }
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stImage"] { margin-top: .15rem; }
[data-testid="stVerticalBlockBorderWrapper"] .product-name { margin-top: .15rem; }
.detail-price-panel { background: linear-gradient(120deg, #f1f8f8, #f7fafc); border: 1px solid #dcebea; border-radius: 14px; padding: 1rem 1.15rem; margin: .9rem 0 1rem; }
.detail-price-panel .price { font-size: 30px; }
.detail-rating { color: #536779; font-size: .92rem; margin: .35rem 0; }
.detail-section { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 1.05rem 1.15rem; margin: .8rem 0; }
.detail-section-title { color: var(--navy); font: 700 17px 'Manrope', sans-serif; margin-bottom: .65rem; }
.detail-stock { display: inline-block; border-radius: 999px; padding: .3rem .65rem; background: #e7f5ef; color: #21744f; font-size: .8rem; font-weight: 700; }
.detail-stock.limited { background: #fff3e3; color: #96621c; }
.detail-fact { color: #526579; font-size: .9rem; padding: .28rem 0; }
.detail-action-row [data-testid="stButton"] button { min-height: 2.7rem; }
.rank-pill { display: inline-block; background: var(--teal-light); color: #087478; padding: 4px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; }
.signal-row { display: flex; flex-wrap: wrap; gap: .4rem; margin: .55rem 0; }
.signal-pill { display: inline-block; background: #f0f4f8; color: #526579; padding: 4px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }
.signal-pill.good { background: #e7f5ef; color: #21744f; }
.signal-pill.caution { background: #fff3e3; color: #96621c; }
.source-note { border-left: 3px solid var(--teal); background: #edf6f6; padding: .7rem .9rem; color: #435967; border-radius: 0 6px 6px 0; font-size: .88rem; }
.sidebar-foot { color: #9eb0c1; font-size: .75rem; border-top: 1px solid #31465c; padding-top: .8rem; margin-top: 1rem; }
@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"] { padding: 1.1rem 1.25rem 2rem; }
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .65rem; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: min(100%, 260px); }
}
@media (max-width: 560px) {
  [data-testid="stMainBlockContainer"] { padding: .8rem .85rem 1.5rem; }
  .page-title, .hero h1 { font-size: 24px; }
  .hero { padding: 1.2rem; border-radius: 14px; }
  .page-subtitle { font-size: .92rem; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: min(100%, 100%); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_products():
    return ensure_catalogue(ROOT / "data" / "products.csv")


@st.cache_resource
def load_orchestrator(products):
    return RecommendationOrchestrator(products)


try:
    products = load_products()
    orchestrator = load_orchestrator(products)
except Exception as error:
    st.error(f"The product catalogue could not be loaded: {error}")
    st.stop()

if "comparison_ids" not in st.session_state:
    st.session_state.comparison_ids = []
if "activity" not in st.session_state:
    st.session_state.activity = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "settings" not in st.session_state:
    st.session_state.settings = {"top_k": 5, "channel": "Any channel", "brands": []}

NAV_ITEMS = [
    "▦  Dashboard", "⌕  Product Discovery", "✧  AI Shopping Assistant",
    "☆  Recommendations", "▣  Product Details", "⇄  Product Comparison", "⌖  Inventory & Store Availability",
    "▥  Evaluation Dashboard", "⚙  Settings", "ⓘ  About",
]
NAV_TO_PAGE = {item: item.split("  ", 1)[1] for item in NAV_ITEMS}
PAGE_COPY = {
    "Dashboard": ("PRODUCT INTELLIGENCE", "Discover Products Smarter with AI", "Agentic retrieval brings your shopping intent together with catalogue evidence and preferences."),
    "Product Discovery": ("EXPLORE CATALOGUE", "Product Discovery", "Search naturally, narrow the catalogue, and inspect why each match was selected."),
    "AI Shopping Assistant": ("SHOPPING ASSISTANT", "A more considered way to shop", "Ask the local recommendation workflow for products and see the evidence behind every result."),
    "Recommendations": ("YOUR SHORTLIST", "Recommendations", "Review the latest ranked results, preference matches, budget fit, and availability."),
    "Product Details": ("PRODUCT PROFILE", "Product Details", "Inspect catalogue-backed product information, recommendation context, and related items."),
    "Product Comparison": ("SIDE BY SIDE", "Product Comparison", "Compare saved products using the attributes available in the catalogue."),
    "Inventory & Store Availability": ("CATALOGUE OPERATIONS", "Inventory & Store Availability", "Inspect synthetic stock and channel coverage. These are demo values, not live retailer inventory."),
    "Evaluation Dashboard": ("QUALITY MEASURES", "Evaluation Dashboard", "Measured retrieval and ranking metrics from the local synthetic evaluation set."),
    "Settings": ("PREFERENCES", "Settings", "Set defaults for this browser session. Preferences are not stored as a customer profile."),
    "About": ("PROJECT NOTES", "About Context Cart", "An academic prototype for explainable, context-aware product recommendation."),
}


def page_link(label: str, query: str | None = None):
    if query is not None:
        st.session_state.discovery_query = query
    st.session_state.nav_page = label


def submit_dashboard_search():
    st.session_state.discovery_query = st.session_state.get("dashboard_query", "")
    st.session_state.nav_page = NAV_ITEMS[1]


def toggle_comparison(product_id: str):
    selected = list(st.session_state.comparison_ids)
    if product_id in selected:
        selected.remove(product_id)
        st.session_state.pop("comparison_notice", None)
    elif len(selected) >= 4:
        st.session_state.comparison_notice = "Product comparison is limited to four items."
    else:
        selected.append(product_id)
    st.session_state.comparison_ids = selected


def product_image_path(product_id: str, category: str | None = None) -> Path | None:
    product_entry = PRODUCT_IMAGE_MANIFEST["product_images"].get(str(product_id))
    if product_entry:
        image_path = ROOT / product_entry["path"]
        if image_path.is_file():
            return image_path
        category = category or product_entry["category"]
    if category is None:
        product_match = products.loc[products["product_id"].eq(product_id), "category"]
        category = str(product_match.iloc[0]) if not product_match.empty else None
    category_entry = PRODUCT_IMAGE_MANIFEST["category_images"].get(category)
    if category_entry:
        image_path = ROOT / category_entry["path"]
        if image_path.is_file():
            return image_path
    return None


def render_product_image(product_id: str, product_name: str, category: str):
    image_path = product_image_path(product_id, category)
    if image_path is None:
        st.warning(f"No local product photograph is mapped for {product_name}.")
        return
    product_photo = PRODUCT_IMAGE_MANIFEST["product_images"].get(str(product_id), {})
    category_photo = PRODUCT_IMAGE_MANIFEST["category_images"].get(category, {})
    alt_text = product_photo.get(
        "alt", category_photo.get("alt", f"{category} category-reference photograph")
    )
    source_title = product_photo.get("source_title")
    st.image(
        str(image_path),
        caption=f"{product_name} · {alt_text}"
        + (
            f" Reference only, not the exact catalogue model. Source: {source_title}."
            if source_title
            else " Category reference photo, not the exact catalogue model."
        ),
        width="stretch",
    )


def open_product_details(product_id: str):
    st.session_state.selected_product_id = product_id
    st.session_state.nav_page = "▣  Product Details"


def go_to_recommendations():
    st.session_state.nav_page = "☆  Recommendations"


def reveal_related_products():
    st.session_state.show_related_products = True


def build_recommendation(query: str, *, category: str | None = None, price_range=None,
                         brands=None, minimum_rating: float = 0, availability: str = "Any availability",
                         context: CustomerContext | None = None, top_k: int = 5):
    if not query.strip():
        raise ValueError("Enter a shopping query to continue.")
    active_context = context or CustomerContext(channel=st.session_state.settings["channel"],
                                                 preferred_brands=st.session_state.settings["brands"])
    effective_query = f"{category} {query}" if category else query
    result = orchestrator.recommend(effective_query, active_context, top_k=30)
    candidates = pd.DataFrame(result["retrieved"])
    if not candidates.empty:
        if category:
            candidates = candidates[candidates["category"] == category]
        if price_range:
            candidates = candidates[candidates["price"].between(price_range[0], price_range[1])]
        if brands:
            candidates = candidates[candidates["brand"].isin(brands)]
        if minimum_rating:
            candidates = candidates[candidates["rating"] >= minimum_rating]
        if availability != "Any availability":
            candidates = candidates[candidates["availability"].str.casefold() == availability.casefold()]
    ranked = orchestrator.ranking_agent.run(candidates, active_context, top_k=len(candidates))
    recommendation_pool = ranked.to_dict(orient="records")
    for product in recommendation_pool:
        product["explanation"] = orchestrator.explanation_agent.run(product, query, active_context)
    result["query"] = query
    result["context"] = {
        "budget": active_context.budget,
        "preferred_brands": active_context.preferred_brands,
        "channel": active_context.channel,
        "preferences": active_context.preferences,
    }
    result["recommendations"] = recommendation_pool[:top_k]
    result["display_pool"] = recommendation_pool
    result["display_limit"] = top_k
    result["retrieved"] = candidates.to_dict(orient="records")
    result["generated_at"] = datetime.now().strftime("%H:%M")
    result["trace"][-1]["detail"] = "Ranking and evidence-grounded explanations generated from filtered catalogue records."
    st.session_state.last_result = result
    st.session_state.activity = ([{
        "query": query,
        "count": len(result["recommendations"]),
        "time": result["generated_at"],
        "product_ids": [item["product_id"] for item in result["recommendations"][:3]],
    }]
                                 + st.session_state.activity)[:8]
    return result


def render_product_card(product: dict, *, compact: bool = False, key_prefix: str = "product"):
    product_id = str(product["product_id"])
    compared = product_id in st.session_state.comparison_ids
    with st.container(border=True):
        render_product_image(product_id, str(product["product_name"]), str(product["category"]))
        top = st.columns([1.2, 1])
        top[0].markdown(f"<span class='rank-pill'>{escape(str(product['category']))}</span>", unsafe_allow_html=True)
        if "ranking_score" in product:
            top[1].markdown(f"<div style='text-align:right'><span class='rank-pill'>Score {product['ranking_score']:.2f}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-name'>{escape(str(product['product_name']))}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='product-meta'>{escape(str(product['brand']))} &nbsp;·&nbsp; "
            f"{product['rating']:.1f} / 5 &nbsp;·&nbsp; {escape(str(product['availability']))}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='price'>₹{product['price']:,.0f}</div>", unsafe_allow_html=True)
        signals = []
        if "within_budget" in product:
            within_budget = bool(product["within_budget"])
            signals.append(
                f"<span class='signal-pill {'good' if within_budget else 'caution'}'>"
                f"{'Within budget' if within_budget else 'Over budget'}</span>"
            )
        if product.get("preference_score", 0) > 0:
            signals.append("<span class='signal-pill good'>Preference match</span>")
        signals.append(
            f"<span class='signal-pill {'good' if str(product['availability']).casefold() == 'in stock' else ''}'>"
            f"{escape(str(product['availability']))}</span>"
        )
        st.markdown(f"<div class='signal-row'>{''.join(signals)}</div>", unsafe_allow_html=True)
        if not compact:
            st.caption(product["description"])
            if product.get("explanation"):
                with st.expander("Why this match"):
                    st.write(product["explanation"])
            with st.expander("View product details"):
                st.write(f"**Specifications:** {product['specifications'] or 'Not provided'}")
                st.write(f"**Category:** {product['category']}")
                st.write(f"**Channel:** {product['channel']}")
                st.caption(f"Product ID {product_id} · Source: {product['source']}")
        button_label = "✓ Added to comparison" if compared else "＋ Compare"
        st.button(button_label, key=f"{key_prefix}_{product_id}", on_click=toggle_comparison, args=(product_id,),
                  width="stretch")
        st.button(
            "View product details",
            key=f"{key_prefix}_details_{product_id}",
            on_click=open_product_details,
            args=(product_id,),
            width="stretch",
        )


def render_products(items: list[dict], *, key_prefix: str = "catalogue",
                    limit: int | None = None, layout: str = "Grid"):
    visible = items if limit is None else items[:limit]
    if not visible:
        st.info("No products match these filters. Widen your price range or remove a filter.")
        return
    if layout == "List":
        for product in visible:
            render_product_card(product, key_prefix=key_prefix)
        return
    for start in range(0, len(visible), 3):
        columns = st.columns(3)
        for column, product in zip(columns, visible[start:start + 3]):
            with column:
                render_product_card(product, key_prefix=key_prefix)


def sort_products(items: list[dict], sort_by: str) -> list[dict]:
    sort_keys = {
        "Relevance": ("ranking_score", "retrieval_score", "rating"),
        "Price: low to high": ("price",),
        "Rating: high to low": ("rating",),
        "Popularity": ("review_count", "rating"),
    }
    keys = sort_keys[sort_by]
    return sorted(
        items,
        key=lambda item: tuple(item.get(key, 0) for key in keys),
        reverse=sort_by in {"Relevance", "Rating: high to low", "Popularity"},
    )


def product_feature(product: pd.Series, feature: str) -> str:
    specs = str(product.get("specifications", ""))
    description = str(product.get("description", ""))
    source = f"{specs}; {description}"
    if feature.casefold() in {"ram", "storage"}:
        return "Not provided in catalogue"
    matched = [part.strip() for part in source.split(";") if feature.casefold() in part.casefold()]
    return "; ".join(dict.fromkeys(matched)) if matched else "Not provided in catalogue"


def product_specification_rows(specifications: str) -> list[dict[str, str]]:
    features = [value.strip() for value in specifications.split(";") if value.strip()]
    return [
        {"Specification": f"Catalogue feature {index}", "Value": value}
        for index, value in enumerate(features, start=1)
    ] or [{"Specification": "Specifications", "Value": "Not provided in catalogue"}]


def recommendation_match_facts(product: pd.Series, recommendation: dict | None,
                               result: dict) -> list[tuple[str, str]]:
    if not recommendation:
        return []
    facts = []
    retrieval_score = recommendation.get("retrieval_score")
    if retrieval_score is not None:
        facts.append(("Shopping query match", f"Retrieved from the query (TF-IDF score {retrieval_score:.3f})."))
    budget = result.get("context", {}).get("budget")
    if budget is not None:
        within_budget = recommendation.get("within_budget")
        status = "within" if within_budget is True else "above" if within_budget is False else "not evaluated"
        facts.append(("Budget compatibility", f"₹{product['price']:,.0f} is {status} the ₹{budget:,.0f} budget."))
    brand_score = recommendation.get("brand_score")
    channel_score = recommendation.get("channel_score")
    if brand_score is not None or channel_score is not None:
        matched = []
        preferences = result.get("context", {})
        if brand_score and product["brand"] in preferences.get("preferred_brands", []):
            matched.append(f"preferred brand: {product['brand']}")
        channel = preferences.get("channel", "Any channel")
        if channel_score and channel != "Any channel":
            matched.append(f"selected channel: {channel}")
        explicit_preferences = preferences.get("preferences", [])
        if explicit_preferences:
            matched.extend(
                f"preference: {value}"
                for value in explicit_preferences
                if value.casefold() in str(product["specifications"]).casefold()
            )
        facts.append(("Preference match", "; ".join(matched) if matched else "No explicit preference match recorded."))
    query = str(result.get("query", ""))
    specifications = str(product.get("specifications", ""))
    query_terms = [term for term in query.casefold().split() if len(term) > 2]
    matched_terms = [term.strip(".,!?;:") for term in query_terms
                     if term.strip(".,!?;:") in specifications.casefold()]
    if recommendation.get("retrieval_score") is not None:
        facts.append((
            "Specification match",
            f"Matching catalogue features: {', '.join(dict.fromkeys(matched_terms))}."
            if matched_terms else "No literal query terms found in the listed specifications.",
        ))
    return facts


def page_heading(page: str):
    eyebrow, title, subtitle = PAGE_COPY[page]
    st.markdown(f"<div class='eyebrow'>{eyebrow}</div><div class='page-title'>{title}</div><div class='page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def render_result_evidence(result: dict):
    with st.expander(f"Agent execution trace · {len(result['trace'])} stages"):
        for step in result["trace"]:
            st.markdown(f"**{step['agent']}** · {step['status']}  \n{step['detail']}")
    with st.expander(f"Retrieved evidence · {len(result['retrieved'])} catalogue records"):
        evidence = pd.DataFrame(result["retrieved"])
        if evidence.empty:
            st.write("No catalogue evidence matched this query.")
        else:
            columns = ["product_id", "product_name", "brand", "price", "rating", "availability", "retrieval_score", "source"]
            st.dataframe(evidence[columns], hide_index=True, width="stretch")


st.sidebar.markdown("<div class='brand-row'><span class='brand-mark'>C</span><div><div class='brand-title'>Context Cart</div><div class='brand-subtitle'>Product intelligence</div></div></div>", unsafe_allow_html=True)
st.sidebar.caption("WORKSPACE")
selected_nav = st.sidebar.radio("Navigate", NAV_ITEMS, key="nav_page", label_visibility="collapsed")
active_page = NAV_TO_PAGE[selected_nav]
st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(st.session_state.comparison_ids)}** products in comparison")
if st.session_state.get("comparison_notice"):
    st.sidebar.warning(st.session_state.pop("comparison_notice"))
st.sidebar.markdown("<div class='sidebar-foot'>LOCAL DEMONSTRATION<br>Catalogue and ratings are synthetic</div>", unsafe_allow_html=True)

eyebrow, title, subtitle = PAGE_COPY[active_page]
_, header_right = st.columns([5, 1])
with header_right:
    st.markdown("<div style='text-align:right;padding-top:.45rem'><span class='rank-pill'>LOCAL · SYNTHETIC DATA</span></div>", unsafe_allow_html=True)

if active_page == "Dashboard":
    st.markdown("<section class='hero'><div class='eyebrow'>CONTEXT-AWARE PRODUCT DISCOVERY</div><h1>Discover Products Smarter with AI</h1><p>Agentic retrieval brings your shopping intent together with product evidence, budget, and preferences. Every recommendation stays inspectable.</p></section>", unsafe_allow_html=True)
    recommendation_count = sum(item["count"] for item in st.session_state.activity)
    metrics = st.columns(4)
    metrics[0].metric("Total products", f"{len(products):,}")
    metrics[1].metric("Product categories", products["category"].nunique())
    metrics[2].metric("Recommendations this session", recommendation_count)
    metrics[3].metric("Active session", "1", help="This browser session only; no cross-user session analytics are collected.")
    st.markdown("<div class='section-title'>Start with a shopping need</div>", unsafe_allow_html=True)
    with st.form("dashboard_discovery", clear_on_submit=False):
        search_col, button_col = st.columns([5, 1])
        dashboard_query = search_col.text_input("Describe what you are looking for", placeholder="e.g. Lightweight wireless headphones for travel under ₹5,000", label_visibility="collapsed", key="dashboard_query")
        button_col.form_submit_button("Discover", type="primary", width="stretch", on_click=submit_dashboard_search)
    suggested = st.columns(4)
    suggested_queries = ["Travel headphones under ₹5,000", "Water-resistant daypack", "Cushioned running shoes", "Insulated water bottle"]
    for column, query in zip(suggested, suggested_queries):
        with column:
            st.button(query, key=f"suggest_{query}", on_click=page_link, args=(NAV_ITEMS[1], query), width="stretch")
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("<div class='section-title'>Popular catalogue picks</div>", unsafe_allow_html=True)
        st.caption("Sorted by synthetic rating and review count; no sales or click trend data is available.")
        top_rated = products.sort_values(["rating", "review_count"], ascending=False).head(3).to_dict(orient="records")
        featured = st.columns(3)
        for column, item in zip(featured, top_rated):
            with column:
                with st.container(border=True):
                    render_product_image(
                        item["product_id"], item["product_name"], item["category"],
                    )
                    st.markdown(f"**{item['product_name']}**")
                    st.caption(f"{item['brand']} · {item['category']} · ★ {item['rating']:.1f}/5")
                    st.markdown(f"<div class='price'>₹{item['price']:,.0f}</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='section-title'>Recent recommendation activity</div>", unsafe_allow_html=True)
        if st.session_state.activity:
            for item in st.session_state.activity[:5]:
                with st.container(border=True):
                    product_ids = item.get("product_ids", [])
                    if product_ids:
                        recent_product = products.loc[products["product_id"].eq(product_ids[0])]
                        if not recent_product.empty:
                            recent_product = recent_product.iloc[0]
                            render_product_image(
                                str(recent_product["product_id"]),
                                str(recent_product["product_name"]),
                                str(recent_product["category"]),
                            )
                    st.markdown(f"**{item['query']}**")
                    st.caption(f"{item['count']} results · {item['time']}")
        else:
            st.info("Your searches in this browser session will appear here.")
        mean_rating = products["rating"].mean()
        availability_rate = products["availability"].str.casefold().eq("in stock").mean() * 100
        leading_category = products["category"].value_counts().idxmax()
        leading_category_count = int(products["category"].value_counts().iloc[0])
        st.markdown("<div class='section-title'>AI-powered insights</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='source-note'>The catalogue contains <b>{leading_category_count}</b> "
            f"products in its largest category ({escape(str(leading_category))}). Synthetic average rating: "
            f"<b>{mean_rating:.1f}/5</b>; marked in stock: <b>{availability_rate:.0f}%</b>."
            "<br>Signals are computed from demo catalogue fields, not live sales or customer behavior.</div>",
            unsafe_allow_html=True,
        )

elif active_page == "Product Discovery":
    page_heading(active_page)
    with st.form("discovery_form"):
        query = st.text_input("Natural-language search", value=st.session_state.get("discovery_query", ""), placeholder="Find lightweight wireless headphones for travel under ₹5,000")
        filter_cols = st.columns(4)
        category = filter_cols[0].selectbox("Category", ["All categories", *sorted(products["category"].unique())])
        brands = filter_cols[1].multiselect("Brand", sorted(products["brand"].unique()))
        minimum_rating = filter_cols[2].selectbox("Minimum rating", [0.0, 3.5, 4.0, 4.5], format_func=lambda value: "Any rating" if value == 0 else f"{value:.1f}+ stars")
        availability = filter_cols[3].selectbox("Availability", ["Any availability", "In stock", "Limited stock"])
        price_range = st.slider("Price range (₹)", int(products["price"].min()), int(products["price"].max()), (int(products["price"].min()), int(products["price"].max())), step=100)
        context_cols = st.columns(3)
        budget = context_cols[0].number_input("Maximum budget (optional)", min_value=0, value=0, step=500)
        channel = context_cols[1].selectbox("Shopping channel", ["Any channel", "website", "mobile application", "physical store"], index=["Any channel", "website", "mobile application", "physical store"].index(st.session_state.settings["channel"]))
        top_k = context_cols[2].slider("Number of recommendations", min_value=1, max_value=10, value=st.session_state.settings["top_k"])
        preferences_text = st.text_input("Additional preferences", placeholder="foldable, long battery, compact")
        search_submitted = st.form_submit_button("Search catalogue", type="primary")
    if search_submitted:
        context = CustomerContext(budget=budget or None, preferred_brands=brands, channel=channel,
                                  preferences=[term.strip() for term in preferences_text.split(",") if term.strip()])
        try:
            with st.spinner("Retrieving catalogue evidence and ranking matches..."):
                result = build_recommendation(query, category=None if category == "All categories" else category,
                                              price_range=price_range, brands=brands, minimum_rating=minimum_rating,
                                              availability=availability, context=context, top_k=top_k)
            st.success(f"{len(result['recommendations'])} recommendations from {len(result['retrieved'])} filtered products")
        except (ValueError, KeyError) as error:
            st.error(str(error))
    result = st.session_state.get("last_result")
    if result:
        st.markdown(f"<div class='section-title'>Matches for “{escape(str(result['query']))}”</div>", unsafe_allow_html=True)
        display_cols = st.columns([1, 1, 2])
        sort_by = display_cols[0].selectbox(
            "Sort by", ["Relevance", "Price: low to high", "Rating: high to low", "Popularity"],
            key="discovery_sort",
        )
        layout = display_cols[1].radio("View", ["Grid", "List"], horizontal=True, key="discovery_layout")
        if sort_by == "Popularity":
            display_cols[2].caption("Popularity uses the catalogue review-count field; counts are synthetic.")
        display_pool = result.get("display_pool", result["recommendations"])
        visible_products = sort_products(display_pool, sort_by)[:result.get("display_limit", len(result["recommendations"]))]
        render_products(visible_products,
                        key_prefix="discovery", layout=layout)
        render_result_evidence(result)
    else:
        st.markdown("<div class='source-note'>Product cards use locally stored Unsplash category-reference photographs. They depict the product category, not the fictional branded catalogue model. Results use generated product descriptions, features, ratings, and availability.</div>", unsafe_allow_html=True)

elif active_page == "AI Shopping Assistant":
    page_heading(active_page)
    st.markdown("<div class='source-note'>Local agent workflow · Not connected to a hosted chat model or chat API. Recommendations are generated by the existing deterministic retrieval and ranking pipeline.</div>", unsafe_allow_html=True)
    suggestions = st.columns(3)
    assistant_suggestions = ["Lightweight headphones for travel under ₹5,000", "A water-resistant backpack for a laptop", "Running shoes with cushioning"]
    for column, prompt in zip(suggestions, assistant_suggestions):
        with column:
            if st.button(prompt, key=f"chat_suggest_{prompt}", width="stretch"):
                st.session_state.pending_chat = prompt
    prompt = st.chat_input("Ask about products, budget, or preferences")
    pending = st.session_state.pop("pending_chat", None)
    incoming = prompt or pending
    if incoming:
        st.session_state.chat_messages.append({"role": "user", "content": incoming})
        try:
            with st.spinner("The product agents are checking the catalogue..."):
                result = build_recommendation(incoming, top_k=st.session_state.settings["top_k"])
            answer = {"role": "assistant", "content": f"I found {len(result['recommendations'])} catalogue matches. They are ranked using query relevance, rating, budget fit, availability, and your current preference settings.", "result": result}
            st.session_state.chat_messages.append(answer)
        except ValueError as error:
            st.session_state.chat_messages.append({"role": "assistant", "content": str(error)})
    for message_index, message in enumerate(st.session_state.chat_messages):
        with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
            st.write(message["content"])
            result = message.get("result")
            if result:
                for product in result["recommendations"][:3]:
                    render_product_card(
                        product,
                        compact=True,
                        key_prefix=f"chat_{message_index}",
                    )
                    st.caption(product["explanation"])
                    st.caption(f"Catalogue citation: {product['product_id']} · {product['source']}")
                with st.expander("Agent trace"):
                    for step in result["trace"]:
                        st.caption(f"{step['agent']}: {step['detail']}")
    if not st.session_state.chat_messages:
        st.info("Try a suggested query or describe a product and the constraints that matter to you.")

elif active_page == "Recommendations":
    page_heading(active_page)
    result = st.session_state.get("last_result")
    if not result:
        st.info("No recommendations yet. Start with Product Discovery or ask the Shopping Assistant.")
        st.button("Open Product Discovery", on_click=page_link, args=("⌕  Product Discovery",), type="primary")
    else:
        summary = st.columns(4)
        summary[0].metric("Products ranked", len(result["recommendations"]))
        summary[1].metric("Budget", f"₹{result['context']['budget']:,.0f}" if result["context"]["budget"] else "Not set")
        summary[2].metric("Brand preferences", len(result["context"]["preferred_brands"]))
        summary[3].metric("Shopping channel", result["context"]["channel"])
        st.caption(f"Latest query: {result['query']} · This ranking is based on the displayed synthetic catalogue.")
        render_products(sort_products(result["recommendations"], "Relevance"),
                        key_prefix="recommendation")
        render_result_evidence(result)

elif active_page == "Product Details":
    page_heading(active_page)
    selected_id = st.session_state.get("selected_product_id")
    selected_product = products[products["product_id"] == selected_id]
    if selected_product.empty:
        st.info("Choose View product details from a product card to open its profile.")
        st.button("Open Product Discovery", on_click=page_link, args=("⌕  Product Discovery",), type="primary")
    else:
        product = selected_product.iloc[0]
        latest = st.session_state.get("last_result", {})
        recommendation = next(
            (item for item in latest.get("display_pool", latest.get("recommendations", []))
             if item["product_id"] == selected_id),
            None,
        )
        image_col, details_col = st.columns([1.12, 1])
        with image_col:
            with st.container(key="product-detail-image"):
                render_product_image(
                    selected_id, str(product["product_name"]), str(product["category"]),
                )
        with details_col:
            st.markdown(f"<div class='eyebrow'>{escape(str(product['category']))}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='page-title'>{escape(str(product['product_name']))}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='detail-rating'><b>{escape(str(product['brand']))}</b>"
                f" &nbsp;·&nbsp; {escape(str(product['category']))}"
                f" &nbsp;·&nbsp; ★ {product['rating']:.1f} / 5"
                f" &nbsp;·&nbsp; {int(product['review_count']):,} reviews</div>",
                unsafe_allow_html=True,
            )
            stock_status = str(product["availability"])
            stock_class = "limited" if stock_status.casefold() == "limited stock" else ""
            st.markdown(
                f"<span class='detail-stock {stock_class}'>{escape(stock_status)}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='detail-price-panel'><div class='eyebrow'>PRICE</div>"
                f"<div class='price'>₹{product['price']:,.0f}</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div class='detail-section-title'>Product description</div>", unsafe_allow_html=True)
            st.write(product["description"])
            st.markdown(
                f"<div class='detail-fact'>Catalogue channel: "
                f"{escape(str(product['channel']))}</div>",
                unsafe_allow_html=True,
            )
            action_cols = st.columns(2)
            action_cols[0].button(
                "Add to Comparison" if selected_id not in st.session_state.comparison_ids else "✓ In Comparison",
                key=f"details_compare_{selected_id}",
                on_click=toggle_comparison,
                args=(selected_id,),
                width="stretch",
            )
            action_cols[1].button(
                "Back to Recommendations",
                key=f"details_back_{selected_id}",
                on_click=go_to_recommendations,
                width="stretch",
            )
            st.button(
                "View Related Products ↓",
                key=f"details_related_{selected_id}",
                on_click=reveal_related_products,
                width="stretch",
            )

        st.markdown("<div class='section-title'>Product specifications</div>", unsafe_allow_html=True)
        specifications = pd.DataFrame(product_specification_rows(str(product["specifications"])))
        st.dataframe(specifications, hide_index=True, width="stretch")

        st.markdown(
            "<div class='detail-section'><div class='detail-section-title'>"
            "Why This Product Is Recommended</div></div>",
            unsafe_allow_html=True,
        )
        if recommendation:
            facts = recommendation_match_facts(product, recommendation, latest)
            if facts:
                fact_cols = st.columns(2)
                for index, (label, value) in enumerate(facts):
                    with fact_cols[index % 2]:
                        with st.container(border=True):
                            st.markdown(f"**{label}**")
                            st.write(value)
            if recommendation.get("explanation"):
                st.markdown("**Recommendation explanation**")
                st.write(recommendation["explanation"])
            if "ranking_score" in recommendation:
                st.metric("Recommendation score", f"{recommendation['ranking_score']:.2f}")
            evidence = next(
                (item for item in latest.get("retrieved", [])
                 if item.get("product_id") == selected_id),
                None,
            )
            if evidence:
                st.markdown("**Catalogue evidence and citation**")
                st.write(evidence.get("description", ""))
                if evidence.get("specifications"):
                    st.caption(f"Listed features: {evidence['specifications']}")
                st.caption(f"Citation: {evidence.get('product_id')} · {evidence.get('source')}")
                st.caption("The current local workflow uses TF-IDF catalogue retrieval; no RAG citations are available.")
            else:
                st.info("No retrieved evidence record is available for this product in the latest recommendation.")
        else:
            st.info("No AI recommendation explanation or match scores are available for this product yet.")

        st.markdown("<div class='section-title'>Inventory information</div>", unsafe_allow_html=True)
        channel = str(product["channel"]).casefold()
        stock = str(product["availability"])
        online_status = stock if channel in {"website", "mobile application"} else "Not listed in online channels"
        store_status = stock if channel == "physical store" else "Not listed as physical-store stock"
        inventory_cols = st.columns(4)
        inventory_cols[0].metric("Online availability", online_status)
        inventory_cols[1].metric("Store availability", store_status)
        inventory_cols[2].metric("Delivery options", "Not provided")
        inventory_cols[3].metric("Pickup availability", "Not provided")
        st.caption("Inventory is limited to the catalogue's availability and channel fields; store-level, delivery, and pickup data are not supplied.")

        related = products[
            (products["category"] == product["category"])
            & (products["product_id"] != selected_id)
        ].sort_values(["rating", "review_count"], ascending=False).head(4).to_dict(orient="records")
        with st.expander(
            "Related products",
            expanded=st.session_state.get("show_related_products", False),
        ):
            st.caption(f"Other products in {product['category']}, sorted by synthetic catalogue rating.")
            render_products(related, key_prefix=f"related_{selected_id}")

elif active_page == "Product Comparison":
    page_heading(active_page)
    selected_ids = st.session_state.comparison_ids
    if not selected_ids:
        st.info("Add products to comparison from Product Discovery or Recommendations.")
        st.button("Browse products", on_click=page_link, args=("⌕  Product Discovery",), type="primary")
    else:
        available = products[products["product_id"].isin(selected_ids)].copy()
        label_by_id = dict(zip(available["product_id"], available["product_name"]))
        selected_ids = st.multiselect("Products in comparison (2–4)", selected_ids, default=selected_ids,
                                      max_selections=4,
                                      format_func=lambda value: label_by_id.get(value, value), key="compare_selector")
        st.session_state.comparison_ids = selected_ids
        compare = available[available["product_id"].isin(selected_ids)].copy()
        if len(compare) < 2:
            st.warning("Select at least two products for a side-by-side comparison.")
        elif not compare.empty:
            latest = st.session_state.get("last_result", {})
            score_by_id = {
                item["product_id"]: item["ranking_score"]
                for item in latest.get("display_pool", latest.get("recommendations", []))
                if "ranking_score" in item
            }
            compare["recommendation_score"] = compare["product_id"].map(score_by_id)
            compare["recommendation_score"] = compare["recommendation_score"].map(
                lambda score: f"{score:.2f}" if pd.notna(score) else "Not evaluated"
            )
            compare["RAM"] = compare.apply(lambda item: product_feature(item, "RAM"), axis=1)
            compare["Storage"] = compare.apply(lambda item: product_feature(item, "storage"), axis=1)
            compare["Battery"] = compare.apply(lambda item: product_feature(item, "battery"), axis=1)
            compare["Display"] = compare.apply(lambda item: product_feature(item, "display"), axis=1)
            compare["Price"] = compare["price"].map(lambda value: f"₹{value:,.0f}")
            compare["Rating"] = compare["rating"].map(lambda value: f"{value:.1f} / 5")
            compare["Availability"] = compare["availability"]
            compare["Features"] = compare["specifications"].replace("", "Not provided in catalogue")
            compare["Recommendation score"] = compare["recommendation_score"]
            display = compare.set_index("product_name")[
                ["brand", "Price", "Rating", "RAM", "Storage", "Battery", "Display",
                 "Features", "Availability", "channel", "Recommendation score"]
            ].T
            best_for = {
                "Price": compare.loc[compare["price"].idxmin(), "product_name"],
                "Rating": compare.loc[compare["rating"].idxmax(), "product_name"],
                "Availability": compare.loc[
                    compare["availability"].str.casefold().eq("in stock"), "product_name"
                ].iloc[0] if compare["availability"].str.casefold().eq("in stock").any() else None,
                "Recommendation score": compare.loc[
                    pd.to_numeric(compare["recommendation_score"], errors="coerce").idxmax(),
                    "product_name",
                ] if pd.to_numeric(compare["recommendation_score"], errors="coerce").notna().any() else None,
            }
            for field, winner in best_for.items():
                if winner:
                    display.loc[field, winner] = f"Best · {display.loc[field, winner]}"
            product_image_columns = st.columns(len(compare))
            for image_column, (_, compared_product) in zip(
                product_image_columns, compare.iterrows(),
            ):
                with image_column:
                    render_product_image(
                        str(compared_product["product_id"]),
                        str(compared_product["product_name"]),
                        str(compared_product["category"]),
                    )
            st.dataframe(display, width="stretch")
            st.caption("Best labels are based only on available catalogue values. Missing specifications are not inferred.")

elif active_page == "Inventory & Store Availability":
    page_heading(active_page)
    st.markdown("<div class='source-note'>This project has no live retailer inventory connection. All stock and channel labels below are synthetic demo records.</div>", unsafe_allow_html=True)
    filters = st.columns(3)
    inventory_category = filters[0].selectbox("Category", ["All categories", *sorted(products["category"].unique())], key="inventory_category")
    inventory_channel = filters[1].selectbox("Channel", ["All channels", *sorted(products["channel"].unique())], key="inventory_channel")
    inventory_status = filters[2].selectbox("Stock status", ["All statuses", *sorted(products["availability"].unique())], key="inventory_status")
    inventory = products.copy()
    if inventory_category != "All categories":
        inventory = inventory[inventory["category"] == inventory_category]
    if inventory_channel != "All channels":
        inventory = inventory[inventory["channel"] == inventory_channel]
    if inventory_status != "All statuses":
        inventory = inventory[inventory["availability"] == inventory_status]
    stock_summary = st.columns(3)
    stock_summary[0].metric("Catalogue records", len(inventory))
    stock_summary[1].metric("In stock", int(inventory["availability"].eq("In stock").sum()))
    stock_summary[2].metric("Channels represented", inventory["channel"].nunique())
    st.info("The catalogue has no store locations, stock quantities, pickup, or delivery fields. Channel availability shown below is catalogue data only.")
    st.dataframe(inventory[["product_name", "category", "brand", "price", "availability", "channel", "source"]], hide_index=True, width="stretch")

elif active_page == "Evaluation Dashboard":
    page_heading(active_page)
    try:
        metrics_path = ROOT / "outputs" / "evaluation" / "metrics.csv"
        details_path = ROOT / "outputs" / "evaluation" / "query_results.csv"
        if not metrics_path.exists():
            st.info("Not evaluated yet. Run the local evaluation script to populate this dashboard.")
            not_evaluated = st.columns(4)
            for column, label in zip(
                not_evaluated, ["Precision@5", "Recall@5", "MRR@5", "NDCG@5"],
            ):
                column.metric(label, "Not evaluated yet")
            runtime = st.columns(3)
            runtime[0].metric("Retrieval quality", "Not evaluated yet")
            runtime[1].metric("Response latency", "Not evaluated yet")
            trace = st.session_state.get("last_result", {}).get("trace", [])
            runtime[2].metric("Agent execution status", "Complete" if trace else "Not run")
            if trace:
                for step in trace:
                    st.caption(f"{step['agent']}: {step['status']}")
        else:
            metrics = pd.read_csv(metrics_path)
            details = pd.read_csv(details_path) if details_path.exists() else pd.DataFrame()
            required_metrics = {
                "method", "precision_at_5", "recall_at_5", "mrr_at_5", "ndcg_at_5",
                "latency_ms_mean",
            }
            missing_metrics = required_metrics - set(metrics.columns)
            if missing_metrics:
                raise ValueError(f"Evaluation results are missing columns: {', '.join(sorted(missing_metrics))}")
            if metrics.empty:
                raise ValueError("Evaluation results contain no measurements.")
            metric_cols = st.columns(4)
            preferred = metrics[metrics["method"] == "Five-agent ranking"]
            selected_metrics = preferred.iloc[0] if not preferred.empty else metrics.iloc[0]
            metric_cols[0].metric("Precision@5", f"{selected_metrics['precision_at_5']:.3f}")
            metric_cols[1].metric("Recall@5", f"{selected_metrics['recall_at_5']:.3f}")
            metric_cols[2].metric("MRR@5", f"{selected_metrics['mrr_at_5']:.3f}")
            metric_cols[3].metric("NDCG@5", f"{selected_metrics['ndcg_at_5']:.3f}")
            st.caption("Saved local evaluation · Four synthetic query intents · Category membership is the relevance label, not a human judgment.")
            agentic = metrics[metrics["method"] == "Five-agent ranking"]
            if not agentic.empty:
                st.markdown("<div class='section-title'>Agent execution performance</div>", unsafe_allow_html=True)
                performance = st.columns(4)
                performance[0].metric("Response latency", f"{agentic.iloc[0]['latency_ms_mean']:.2f} ms")
                trace = st.session_state.get("last_result", {}).get("trace", [])
                performance[1].metric("Agent execution status", "Complete" if trace else "Not run")
                performance[2].metric("Workflow stages", len(trace) if trace else "Not run")
                performance[3].metric(
                    "Evaluated queries",
                    details["query"].nunique() if "query" in details.columns else "Unavailable",
                )
                st.caption("Latency measures the complete local recommendation method; per-agent timings are not recorded.")
            chart_left, chart_right = st.columns(2)
            with chart_left:
                st.markdown("<div class='section-title'>Retrieval quality by method</div>", unsafe_allow_html=True)
                quality = metrics.set_index("method")[["precision_at_5", "recall_at_5", "mrr_at_5", "ndcg_at_5"]]
                st.bar_chart(quality, y_label="Score")
            with chart_right:
                st.markdown("<div class='section-title'>Agent and retrieval execution latency</div>", unsafe_allow_html=True)
                st.bar_chart(metrics.set_index("method")[["latency_ms_mean"]], y_label="Milliseconds")
            st.markdown("<div class='section-title'>Baseline results</div>", unsafe_allow_html=True)
            st.dataframe(metrics, hide_index=True, width="stretch")
            if not details.empty:
                with st.expander("Per-query evaluation detail"):
                    st.dataframe(details, hide_index=True, width="stretch")
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Evaluation results could not be loaded: {error}")

elif active_page == "Settings":
    page_heading(active_page)
    settings = st.session_state.settings
    with st.form("settings_form"):
        st.markdown("<div class='section-title'>Recommendation defaults</div>", unsafe_allow_html=True)
        default_top_k = st.slider("Default recommendation count", 1, 10, settings["top_k"])
        default_channel = st.selectbox("Default shopping channel", ["Any channel", "website", "mobile application", "physical store"], index=["Any channel", "website", "mobile application", "physical store"].index(settings["channel"]))
        default_brands = st.multiselect("Preferred brands", sorted(products["brand"].unique()), default=settings["brands"])
        saved = st.form_submit_button("Save session preferences", type="primary")
    if saved:
        st.session_state.settings = {"top_k": default_top_k, "channel": default_channel, "brands": default_brands}
        st.success("Preferences saved for this browser session only.")
    st.markdown("<div class='section-title'>Privacy and session data</div>", unsafe_allow_html=True)
    st.caption("The app does not persist customer profiles. Recommendation history and assistant messages stay in Streamlit session state.")
    if st.button("Clear this session's activity and chat", key="clear_activity"):
        st.session_state.activity = []
        st.session_state.chat_messages = []
        st.session_state.comparison_ids = []
        st.session_state.pop("last_result", None)
        st.success("Session activity, chat, recommendations, and comparison list cleared.")

else:
    page_heading(active_page)
    st.markdown("### Project overview")
    st.write("Context Cart demonstrates a modular, evidence-grounded recommendation workflow for omnichannel retail. Five local Python agents parse a query, carry explicit context, retrieve catalogue records, rank products, and explain results.")
    st.markdown("### Implemented in this workspace")
    st.write("Streamlit frontend, 120 synthetic products, scikit-learn TF-IDF retrieval, deterministic ranking, product comparison, evaluation metrics, report and presentation artifacts.")
    st.markdown("### Not implemented")
    st.write("No hosted chat API, generative LLM, vector database, retailer inventory integration, real customer profile, or cloud deployment is connected. Product images are locally stored Unsplash category-reference photographs, not photographs of the fictional branded catalogue models; sales trends are not present in the dataset.")
    st.markdown("### Data and privacy")
    st.write("All product attributes, ratings, prices, and stock labels are synthetic. Session preferences are not written to a persistent user store. Evaluation relevance is based on synthetic category labels.")
