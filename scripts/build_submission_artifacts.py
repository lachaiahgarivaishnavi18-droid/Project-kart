"""Build measured-results chart, PDF report, and editable presentation."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

OUT = ROOT / "outputs" / "evaluation"
metrics_path = OUT / "metrics.csv"
if not metrics_path.exists():
    from recommender.catalog import ensure_catalogue
    from recommender.evaluation import evaluate
    metric_data, detail_data = evaluate(ensure_catalogue(ROOT / "data" / "products.csv"))
    OUT.mkdir(parents=True, exist_ok=True)
    metric_data.to_csv(metrics_path, index=False)
    detail_data.to_csv(OUT / "query_results.csv", index=False)
metrics = pd.read_csv(metrics_path)
examples = ROOT / "outputs" / "examples"

plt.figure(figsize=(9, 4.8))
palette = ["#566e62", "#e17c5b", "#237c63", "#bc9c44"]
plt.bar(metrics["method"], metrics["precision_at_5"], color=palette[:len(metrics)])
plt.ylim(0, 1.08)
plt.ylabel("Precision@5")
plt.title("Synthetic category-label evaluation")
plt.xticks(rotation=16, ha="right")
plt.grid(axis="y", alpha=0.2)
plt.tight_layout()
chart_path = OUT / "evaluation_chart.png"
plt.savefig(chart_path, dpi=160, facecolor="white")
plt.close()

report_dir = ROOT / "report"
report_dir.mkdir(exist_ok=True)
pdf_path = report_dir / "project_report.pdf"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#183c31"), alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=13, leading=16, textColor=colors.HexColor("#237c63"), spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8.6, leading=12, spaceAfter=5))
story = [Paragraph("Context-Aware Product Recommendation with a Five-Agent TF-IDF Pipeline", styles["ReportTitle"]),
         Paragraph("Project Report | Reproducible local demonstration", styles["BodyText"]), Spacer(1, 12)]
sections = [
    ("Abstract", "Context Cart is a locally executable demonstration of product recommendation from natural-language shopping queries and explicit preferences. Five Python agents parse a query, assemble request-scoped context, retrieve catalogue evidence, rank candidate products, and produce evidence-grounded explanations. Retrieval uses TF-IDF and metadata filtering; no LLM or vector database is implemented. A deterministic catalogue of 120 synthetic products supports an evaluation of keyword, TF-IDF, context-aware TF-IDF, and five-agent ranking. Results are limited to synthetic category labels and do not establish human preference quality or real-world performance."),
    ("1. Introduction", "Retail search benefits from combining intent with explicit constraints such as budget, preferred brand, and channel. This project provides an inspectable and reproducible baseline, separating parsing, retrieval, ranking, and explanation."),
    ("2. Literature Review", "Term weighting is a foundation of lexical text retrieval [1]. Recommender systems include content-based, collaborative, and hybrid approaches [2]. Retrieval-augmented generation combines retrieval and language generation [3]. This implementation performs retrieval-grounded recommendation but uses deterministic templates rather than an LLM."),
    ("3. Existing System and Limitations", "The keyword baseline matches category strings but does not score textual relevance or user constraints. The prototype adds TF-IDF, context, ranking, and evidence display. It has no retailer feed, user history, dense embeddings, vector database, or external language model."),
    ("4. Proposed System and Contributions", "The software contribution is an orchestrated five-agent implementation, traceable retrieval/ranking, budget feasibility handling, grounded explanation and comparison, plus reproducible metrics. No research novelty or performance improvement is claimed."),
    ("5. System Architecture", "The Streamlit interface calls a central orchestrator. Five agents parse the query, carry explicit context, retrieve records, rank candidates, and explain results. The catalogue is validated and indexed in memory with scikit-learn TF-IDF. Seven editable Mermaid diagrams are in docs/diagrams/architecture.md."),
    ("6. Dataset Description", "The local generator creates 120 deterministic synthetic products in six categories. Product attributes, brands, prices, ratings, stock, and review counts are fictional. All records state synthetic demonstration data. No restricted third-party dataset or customer information is used. See data/DATA_DICTIONARY.md and data/SOURCE.md."),
    ("7. Methodology", "TF-IDF documents combine product name, category, brand, description, and specifications; English stop-word removal and 1–2 grams are used. Cosine similarity retrieves candidates. The ranking formula is 0.50 relevance + 0.20 rating + 0.15 budget + 0.10 availability + 0.05 explicit preference, which averages preferred-brand and selected-channel match. If any candidate meets a specified budget, over-budget candidates are filtered out. Explanations use catalogue evidence only."),
    ("8. Implementation", "The Python package is under src/recommender and the Streamlit application is app.py. Input catalogue validation enforces required fields and numeric bounds. Customer context is request-scoped and not persisted. No paid API or cloud service is required."),
    ("9. Experimental Setup", "Four fixed query intents use expected category as the relevance label. Baselines are a category keyword filter, global TF-IDF, category-filtered TF-IDF, and five-agent ranking with budget. Metrics are Precision@5, Recall@5, MRR@5, NDCG@5, local single-process latency, and budget satisfaction. Category membership is a synthetic proxy, not a human judgment."),
]
for heading, text in sections:
    story.extend([Paragraph(heading, styles["Section"]), Paragraph(text, styles["BodySmall"])])
story.append(Paragraph("10. Results and Discussion", styles["Section"]))
table_data = [["Method", "P@5", "R@5", "MRR@5", "NDCG@5", "Latency ms", "Budget"]]
for _, row in metrics.iterrows():
    table_data.append([str(row["method"]), *(f"{row[key]:.3f}" for key in ["precision_at_5", "recall_at_5", "mrr_at_5", "ndcg_at_5"]), f"{row['latency_ms_mean']:.2f}", f"{row['budget_satisfaction']:.3f}"])
table = Table(table_data, repeatRows=1, colWidths=[43*mm, 15*mm, 15*mm, 15*mm, 17*mm, 22*mm, 17*mm])
table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183c31")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd7d0")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f5f1")]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
story.extend([table, Spacer(1, 8), Paragraph("The category-filtered methods score strongly because category is also the relevance definition. The figures therefore validate code behavior under a toy label, not shopper relevance. Latency is a single local run and is not a controlled benchmark.", styles["BodySmall"]), Image(str(chart_path), width=160*mm, height=85*mm)])
remaining = [
    ("11. Security, Privacy, Fairness, and Explainability", "No external API or secret is required. Preferences are not persisted; explanations are constrained to retrieved fields. Fairness, accessibility, threat modeling, privacy certification, and penetration testing are not performed or claimed."),
    ("12. Conclusion and Future Scope", "The project delivers a tested local workflow and measured synthetic evaluation. Further work needs licensed realistic catalogues, consented human relevance judgments, ranking ablations, fairness and accessibility evaluation, and operational hardening."),
    ("13. References", "[1] G. Salton and C. Buckley, “Term-weighting approaches in automatic text retrieval,” Information Processing & Management, vol. 24, no. 5, pp. 513–523, 1988, doi: 10.1016/0306-4573(88)90021-0. [2] F. Ricci, L. Rokach, and B. Shapira, Eds., Recommender Systems Handbook, 2nd ed., Springer, 2015, doi: 10.1007/978-1-4899-7637-6. [3] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” NeurIPS, vol. 33, 2020."),
    ("14. Appendix", "Tests cover catalogue schema/uniqueness, sample budget parsing and filtering, evidence-grounded explanations, explicit context, and finite metrics for all four baselines. Actual recommendation, product comparison, and context/evidence JSON are in outputs/examples/. A genuine browser screenshot was not available during artifact generation and is not fabricated. Full data dictionary and diagrams are maintained in the repository."),
]
for heading, text in remaining:
    story.extend([Paragraph(heading, styles["Section"]), Paragraph(text, styles["BodySmall"])])
SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=17*mm, bottomMargin=17*mm, title="Context Cart Project Report").build(story)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]
GREEN = RGBColor(24, 60, 49)
MINT = RGBColor(35, 124, 99)
CORAL = RGBColor(225, 124, 91)
INK = RGBColor(31, 45, 39)
CREAM = RGBColor(248, 249, 245)

def add_slide(title, bullets, note=None, image=None):
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = CREAM
    band = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.18))
    band.fill.solid(); band.fill.fore_color.rgb = MINT; band.line.fill.background()
    title_box = slide.shapes.add_textbox(Inches(0.65), Inches(0.48), Inches(12), Inches(0.72))
    title_frame = title_box.text_frame; title_frame.clear()
    p = title_frame.paragraphs[0]; p.text = title; p.font.name = "Aptos Display"; p.font.size = Pt(28); p.font.bold = True; p.font.color.rgb = GREEN
    body = slide.shapes.add_textbox(Inches(0.85), Inches(1.55), Inches(11.8), Inches(4.9))
    tf = body.text_frame; tf.clear(); tf.word_wrap = True
    for index, bullet in enumerate(bullets):
        para = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        para.text = bullet; para.level = 0; para.font.name = "Aptos"; para.font.size = Pt(20); para.font.color.rgb = INK; para.space_after = Pt(12)
    if image:
        slide.shapes.add_picture(str(image), Inches(7.5), Inches(1.8), width=Inches(5.2))
    if note:
        note_box = slide.shapes.add_textbox(Inches(0.85), Inches(6.7), Inches(11.8), Inches(0.42))
        p = note_box.text_frame.paragraphs[0]; p.text = note; p.font.size = Pt(10); p.font.color.rgb = MINT
    footer = slide.shapes.add_textbox(Inches(12.1), Inches(7.05), Inches(0.6), Inches(0.25))
    p = footer.text_frame.paragraphs[0]; p.text = str(len(prs.slides)); p.alignment = PP_ALIGN.RIGHT; p.font.size = Pt(10); p.font.color.rgb = MINT
    return slide

best = metrics.set_index("method")
recommendation = {}
rec_path = examples / "recommendation.json"
if rec_path.exists():
    import json
    recommendation = json.loads(rec_path.read_text())
top = recommendation.get("recommendations", [])
compare = {}
comp_path = examples / "comparison.json"
if comp_path.exists():
    import json
    compare = json.loads(comp_path.read_text())

add_slide("Context Cart", ["An agentic retrieval-augmented product recommendation prototype", "Author: [Name]  |  Institution: [Institution]", "Local, reproducible, and usable without paid API keys"], "All catalogue products and attributes are synthetic.")
add_slide("Problem Statement", ["Shopping queries express intent, constraints, and preferences together.", "A keyword match alone does not explain retrieval or consistently enforce a budget.", "Goal: build a transparent, testable recommendation workflow."])
add_slide("Objectives", ["Implement five specialized agents under one orchestrator.", "Support TF-IDF retrieval, metadata filtering, and context-aware ranking.", "Show explanations, comparisons, trace, and measured baseline evaluation."])
add_slide("Existing System and Limitations", ["Keyword-only matching misses broader text matches and context.", "No retailer catalogue, purchase history, or collaborative signals are available.", "This demonstration therefore uses a labelled synthetic catalogue."])
add_slide("Proposed System", ["Streamlit UI and Python orchestration.", "TF-IDF lexical retrieval and exact category metadata filter.", "Weighted rank, explicit budget feasibility, catalogue-grounded explanation.", "No LLM, dense embedding model, or vector database is implemented."])
add_slide("Architecture", ["Shopper query and explicit settings → five-agent orchestrator.", "Synthetic CSV → validation → in-memory TF-IDF index.", "Retrieved evidence → ranking → explanation and trace.", "Seven editable Mermaid diagrams are included in docs/diagrams/."])
add_slide("Five Specialized Agents", ["1. Query Understanding: terms, category, and budget.", "2. Customer Context: explicitly provided preferences and channel.", "3. Product Retrieval: TF-IDF scores and catalogue evidence.", "4. Recommendation and Ranking: transparent weighted factors.", "5. Explanation: reasons grounded in retrieved fields."])
add_slide("Dataset", ["120 deterministic synthetic product records; six categories.", "Fields include price, brand, description, specifications, rating, stock, and channel.", "No actual retailer records, customers, or consumer reviews."])
add_slide("Methodology", ["TF-IDF unigram/bigram product text and cosine similarity.", "Rank = 0.50 relevance + 0.20 rating + 0.15 budget + 0.10 availability + 0.05 explicit preference.", "Preference averages preferred-brand and selected-channel match.", "Over-budget items excluded when at least one in-budget candidate exists; labels are synthetic categories."])
add_slide("Application Workflow", ["Search: natural-language query and context controls.", "Inspect recommendation rationale, five-agent trace, and retrieved evidence.", "Compare two or more products using available catalogue fields.", "Actual screenshot not captured in this run; this slide describes the implemented workflow, not a screenshot."])
query_text = recommendation.get("query", "Lightweight wireless headphones for travel under 3000")
top_text = [f"{item['product_name']}: ₹{item['price']}, rating {item['rating']}/5" for item in top[:3]] or ["Run scripts/generate_demo_outputs.py to create the demonstrated result."]
add_slide("Output 1: Recommendation", [f"Query: {query_text}", *top_text, "See outputs/examples/recommendation.json for all ranked products, explanations, context, and trace."])
comparison_items = compare.get("products", [])
comparison_text = [f"{item['product_name']} | {item['brand']} | ₹{item['price']} | {item['rating']}/5 | {item['availability']}" for item in comparison_items]
add_slide("Output 2 and 3: Compare and Explain", [*(comparison_text or ["Actual comparison is saved in outputs/examples/comparison.json."]), "Context and retrieved evidence are saved in outputs/examples/context_explanation.json.", "Advantages and limitations are restricted to synthetic catalogue data."])
result_lines = [f"{row['method']}: P@5 {row['precision_at_5']:.3f}, R@5 {row['recall_at_5']:.3f}, budget {row['budget_satisfaction']:.3f}" for _, row in metrics.iterrows()]
add_slide("Evaluation Results", [*result_lines, "Four synthetic intents; category relevance labels, no human judgments.", "Single local timing run; not a controlled benchmark."], image=chart_path)
add_slide("Limitations and Future Scope", ["No LLM, vector DB, licensed real catalogue, or retailer integration.", "Category labels make retrieval metrics optimistic and limited.", "Next: human relevance labels, realistic licensed data, fairness review, and controlled ablations."])
add_slide("Conclusion and References", ["Runnable, tested, inspectable local recommendation baseline.", "Measured results are implementation checks, not real-world performance claims.", "Salton & Buckley (1988); Ricci et al. (2015); Lewis et al. (NeurIPS 2020)."], "See paper/ieee_paper_draft.md for the editable reference list and submission caveats.")

presentation_dir = ROOT / "presentation"
presentation_dir.mkdir(exist_ok=True)
pptx_path = presentation_dir / "project_presentation.pptx"
prs.save(pptx_path)
print(f"Generated {pdf_path}, {pptx_path}, and {chart_path}")