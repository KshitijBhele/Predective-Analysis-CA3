"""
generate_report.py
Generates the comprehensive academic and industry project report:
Predictive_Analytics_CA3_Report.docx
for the End-to-End Predictive Analytics Model on Dual Datasets:
1. UCI Online Shoppers Purchasing Intention Dataset
2. Retailrocket E-Commerce Recommender & Clickstream Dataset
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner cell padding in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = Document()

    # Set standard page margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Styles
    # Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(40, 44, 52)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Helper function for headings
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = RGBColor(24, 43, 73)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(18)
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.italic = True
        run.font.color.rgb = RGBColor(90, 105, 120)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(24, 43, 73)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(41, 128, 185)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(50, 70, 90)
        return p

    def add_callout(text, prefix="KEY FINDING: "):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r_pre = p.add_run(prefix)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(24, 43, 73)
        r_txt = p.add_run(text)
        r_txt.font.color.rgb = RGBColor(40, 44, 52)
        doc.add_paragraph()

    # =========================================================================
    # COVER / HEADER
    # =========================================================================
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_meta = p_meta.add_run("PREDICTIVE ANALYTICS  |  CA3 END-TO-END PROJECT REPORT\nOctober 2026")
    r_meta.font.size = Pt(9.5)
    r_meta.font.bold = True
    r_meta.font.color.rgb = RGBColor(120, 130, 140)

    add_title("End-to-End Predictive Analytics:\nDual-Dataset E-Commerce Consumer Conversion Modeling")
    add_subtitle("Integrating Macro-Session Dynamics (UCI) and Micro-Clickstream Event Funnels (Retailrocket) with Data Leakage Isolation")

    # Author metadata box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Candidate Name / Author:", "Kshitij Bhele"),
        ("Course / Assessment:", "Predictive Analytics (CA3 End-to-End Project - 10 Marks)"),
        ("Primary Datasets Utilized:", "1. UCI Online Shoppers Purchasing Intention (12,330 sessions)\n2. Retailrocket Recommender & Clickstream Dataset (2,756,101 events)"),
        ("Repository & Artifacts:", "https://github.com/KshitijBhele/Predective-Analysis-CA3")
    ]
    for row_idx, (lbl, val) in enumerate(meta_info):
        c0 = meta_table.cell(row_idx, 0)
        c1 = meta_table.cell(row_idx, 1)
        c0.paragraphs[0].add_run(lbl).bold = True
        c1.paragraphs[0].add_run(val)
        set_cell_background(c0, "EAECEE")
        set_cell_background(c1, "F8F9F9")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

    doc.add_paragraph()

    # Abstract
    add_h2("Executive Summary / Abstract")
    doc.add_paragraph(
        "This project presents an industry-grade, end-to-end Predictive Analytics framework engineered to classify and "
        "predict e-commerce consumer purchasing intention during active web browsing. Recognizing the inherent dichotomy "
        "between aggregate session telemetry and granular event clickstreams in digital retail, the investigation integrates "
        "two distinct real-world datasets: (1) the benchmark UCI Online Shoppers Purchasing Intention Dataset (12,330 sessions), "
        "and (2) the high-throughput Retailrocket E-Commerce Clickstream Dataset (2,756,101 raw event logs across 1,407,580 visitors). "
        "Following the rigorous 5-stage Knowledge Discovery in Databases (KDD) process, we execute data selection, automated cleaning, "
        "standardized transformation, clickstream sessionization, feature engineering, and multi-model machine learning. "
        "A foundational methodological contribution of this research is the empirical isolation of retrospective feature leakage "
        "caused by Google Analytics' PageValues metric and late-stage cart interaction signals. Across both datasets, we benchmark "
        "five distinct algorithms (Logistic Regression, Decision Trees, Random Forests, Gradient Tree Boosting, and Dummy baseline) "
        "under 5-Fold Stratified Cross-Validation. Results demonstrate that while retrospective signals yield artificially inflated "
        "ROC-AUCs (>0.93 to 0.99), production-safe early-session pipelines achieve robust discriminatory power (ROC-AUC 0.784 on UCI, "
        "0.963 on Retailrocket pre-cart interactions). Finally, a simulated real-time inference engine is implemented to trigger "
        "automated, dynamic promotional interventions before visitor session abandonment occurs."
    )

    # Table of Contents
    add_h2("Table of Contents")
    toc_items = [
        "1. Chapter 1: Introduction",
        "   1.1 Background and Industrial Motivation",
        "   1.2 Problem Statement",
        "   1.3 Project Objectives",
        "   1.4 Dual-Dataset Description (UCI & Retailrocket)",
        "   1.5 Scope, Delimitations, and Operational Context",
        "   1.6 Report Organisation",
        "2. Chapter 2: Literature Review",
        "   2.1 Knowledge Discovery in Databases (KDD) & Predictive Modeling Paradigms",
        "   2.2 Clickstream Telemetry & E-Commerce Purchase Intent Prediction",
        "   2.3 Macro-Session Metrics vs. Micro-Event Funnel Modeling",
        "   2.4 The Problem of Data Leakage in Retrospective Analytics",
        "   2.5 Class Imbalance and Algorithmic Countermeasures",
        "   2.6 Comparative Overview of Classification Algorithms",
        "3. Chapter 3: Workflow / Predictive Modelling Process",
        "   3.1 The KDD Process Architecture",
        "   3.2 Stage 1: Data Selection and Ingestion (GitHub Streaming & Local Extraction)",
        "   3.3 Stage 2: Data Preprocessing & Cleaning",
        "   3.4 Stage 3: Transformation, Sessionization & Feature Engineering",
        "   3.5 Experimental Setup: The Data Leakage Isolation Framework",
        "   3.6 Stage 4: Data Mining / Predictive Model Development & Hyperparameter Tuning",
        "   3.7 Stage 5: Evaluation Protocols and Metrics",
        "4. Chapter 4: Results and Discussion",
        "   4.1 Exploratory Data Analysis (EDA) Findings across Both Datasets",
        "   4.2 Multi-Model Performance Benchmark (Consolidated Results Table)",
        "   4.3 Empirical Analysis of Feature Leakage (With vs. Without Retrospective Metrics)",
        "   4.4 Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Analysis",
        "   4.5 Confusion Matrix Decomposition and Decision Threshold Calibration",
        "   4.6 Behavioral Feature Importance and Economic Drivers of Conversion",
        "   4.7 Real-Time Inference Simulation & Automated Business Interventions",
        "5. Chapter 5: Conclusion",
        "   5.1 Summary of Contributions",
        "   5.2 Managerial and Practical Implications",
        "   5.3 Limitations of the Study",
        "   5.4 Recommendations for Future Research",
        "6. Chapter 6: References"
    ]
    for item in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(1)
        r = p_t.add_run(item)
        r.font.size = Pt(10)
        if item.startswith("1.") or item.startswith("2.") or item.startswith("3.") or item.startswith("4.") or item.startswith("5.") or item.startswith("6."):
            r.bold = True
            r.font.color.rgb = RGBColor(24, 43, 73)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_h1("Chapter 1: Introduction")

    add_h2("1.1 Background and Industrial Motivation")
    doc.add_paragraph(
        "The digital retail economy has expanded into a multi-trillion-dollar global ecosystem characterized by hyper-competition "
        "and razor-thin customer acquisition margins. In modern e-commerce operations, digital traffic acquisition costs (driven by "
        "search engine marketing, programmatic display advertising, and paid social campaigns) continue to escalate. However, global "
        "e-commerce conversion benchmarks consistently indicate that between 96.5% and 98.5% of website visits fail to culminate in "
        "a transaction. The overwhelming majority of visitors browse transiently, examine a small subset of catalog items, and abandon "
        "the digital storefront without creating an account or completing checkout."
    )
    doc.add_paragraph(
        "Historically, commercial enterprises have attempted to re-engage abandoning visitors post hoc through email retargeting or "
        "re-marketing cookies. Yet, academic and empirical studies confirm that once a browsing consumer closes their browser tab, "
        "the re-engagement recovery rate declines dramatically (frequently falling below 3%). Consequently, modern digital commerce "
        "necessitates the development of predictive analytics systems capable of real-time intent forecasting. By analyzing visitor "
        "behavioral telemetry during active site navigation, machine learning models can predict the probability of purchase within "
        "milliseconds, enabling automated algorithmic interventions—such as dynamic personalized discounts, exit-intent overlays, "
        "free-shipping threshold incentives, or proactive live customer support—before the visitor permanently exits the platform."
    )

    add_h2("1.2 Problem Statement")
    doc.add_paragraph(
        "Predicting online purchasing intention in real time poses several profound computational and methodological challenges: "
        "(1) Severe class imbalance, where non-purchasing browsing sessions vastly outnumber converting sessions; "
        "(2) High-velocity clickstream event dynamics requiring high-throughput aggregation and sessionization; "
        "(3) Non-linear interactions among browsing duration, page exploration patterns, and temporal context; and "
        "(4) The pervasive risk of retrospective data leakage. In e-commerce telemetry, summary variables constructed by analytics "
        "platforms (such as Google Analytics' PageValues) retroactively incorporate completed transaction revenue into page scores. "
        "A model trained on such retrospective signals achieves flawless offline validation metrics but catastrophically fails upon "
        "production deployment when such future information is unavailable. This project addresses the central problem: "
        "How can we engineer an end-to-end, leakage-robust predictive model that accurately anticipates consumer purchase conversion "
        "from early-stage behavioral signals across both macro-session summaries and micro-level clickstream sequences?"
    )

    add_h2("1.3 Project Objectives")
    doc.add_paragraph(
        "To systematically resolve this problem, the primary objectives of this investigation are defined as follows:\n"
        "1. Construct an End-to-End Predictive Analytics Pipeline adhering to the five classical stages of Knowledge Discovery in Databases (KDD).\n"
        "2. Ingest and harmonize two complementary real-world datasets: the macro-session benchmark (UCI Online Shoppers Purchasing Intention) "
        "and the granular micro-event stream (Retailrocket Recommender & Clickstream Dataset).\n"
        "3. Sessionize high-velocity clickstream event logs into behavioral visitor profiles and engineer predictive features capturing browsing intensity, item depth, and exploration velocity.\n"
        "4. Formulate an empirical feature leakage experiment to isolate the artificial inflation of retrospective metrics (PageValues and late cart actions) from genuine early-session predictors.\n"
        "5. Train, tune, and benchmark five diverse machine learning classifiers (Logistic Regression, Decision Trees, Random Forests, Gradient Tree Boosting, and Dummy baseline) under 5-Fold Stratified Cross-Validation.\n"
        "6. Provide comprehensive model evaluation and feature interpretation (ROC-AUC, PR-AUC, F1-Score, Tree Gini importance), culminating in a simulated real-time decision engine for dynamic customer intervention."
    )

    add_h2("1.4 Dual-Dataset Description")
    doc.add_paragraph(
        "To provide both benchmark comparability and real-world industrial applicability, this project integrates two distinct datasets:"
    )

    # Table for dataset overview
    ds_table = doc.add_table(rows=5, cols=3)
    ds_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ds_headers = ["Attribute / Dimension", "Dataset 1: UCI Online Shoppers", "Dataset 2: Retailrocket Clickstream"]
    for i, h in enumerate(ds_headers):
        cell = ds_table.cell(0, i)
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "182B49")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 80, 80, 100, 100)

    ds_data = [
        ("Data Modality", "Macro-level session aggregates (tabular)", "Micro-level event logs (clickstream sequences)"),
        ("Sample Volume", "12,330 sessions (12,205 unique deduplicated)", "2,756,101 events across 1,407,580 visitors"),
        ("Target Variable", "Revenue (Boolean: True / False)", "has_transaction (Binary: 1 / 0)"),
        ("Key Telemetry Features", "Admin/Info/Product page counts & durations, BounceRates, ExitRates, PageValues, Month, VisitorType", "Timestamp, VisitorID, Event (view, addtocart, transaction), ItemID, CategoryTree hierarchy")
    ]
    for row_idx, data_row in enumerate(ds_data, start=1):
        for col_idx, text_val in enumerate(data_row):
            cell = ds_table.cell(row_idx, col_idx)
            cell.paragraphs[0].add_run(text_val)
            set_cell_background(cell, "F2F4F4" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, 60, 60, 100, 100)

    doc.add_paragraph()

    add_h2("1.5 Scope, Delimitations, and Operational Context")
    doc.add_paragraph(
        "The scope of this investigation encompasses tabular session-level intent modeling and visitor-level clickstream sequence "
        "sessionization. Natural language processing of textual product reviews and computer vision analysis of product thumbnail "
        "imagery are excluded to maintain computational focus on structural clickstream dynamics and latency-critical scoring. "
        "The model is evaluated under simulated real-time inference conditions where predictions must be generated in sub-10 millisecond intervals."
    )

    add_h2("1.6 Report Organisation")
    doc.add_paragraph(
        "The remainder of this report is organized into five subsequent chapters: Chapter 2 reviews relevant theoretical and empirical "
        "literature on the KDD process, clickstream mining, class imbalance, and data leakage. Chapter 3 outlines the end-to-end "
        "methodology and technical workflow across all KDD stages. Chapter 4 presents comprehensive empirical results, benchmark tables, "
        "visual curves, feature importances, and the real-time simulation. Chapter 5 concludes with theoretical synthesis, managerial implications, "
        "limitations, and future directions. Chapter 6 provides complete academic citations."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW
    # =========================================================================
    add_h1("Chapter 2: Literature Review")

    add_h2("2.1 Knowledge Discovery in Databases (KDD) & Predictive Modeling Paradigms")
    doc.add_paragraph(
        "The foundational methodology guiding this research is the Knowledge Discovery in Databases (KDD) framework formalized "
        "by Fayyad, Piatetsky-Shapiro, and Smyth (1996). Unlike ad hoc machine learning scripts, KDD establishes an iterative, "
        "structured sequence of five interrelated stages: (1) Data Selection, (2) Preprocessing, (3) Transformation, (4) Data Mining, "
        "and (5) Evaluation/Interpretation. In parallel, the Cross-Industry Standard Process for Data Mining (CRISP-DM; Chapman et al., 2000) "
        "emphasizes the vital coupling between algorithmic data mining and business understanding. In this project, KDD serves as the "
        "architectural backbone, ensuring that every engineering choice—from session deduplication to metric selection—directly aligns "
        "with operational e-commerce objectives."
    )

    add_h2("2.2 Clickstream Telemetry & E-Commerce Purchase Intent Prediction")
    doc.add_paragraph(
        "Pioneering research into web user navigation (Bucklin & Sismeiro, 2003; Montgomery et al., 2004) established that sequential "
        "browsing paths contain rich latent signals regarding underlying user intent. Early web mining approaches relied on static Markov "
        "chains and path analysis. However, as demonstrated by Sakar et al. (2019) in their seminal work on the UCI Online Shoppers dataset, "
        "modern supervised learning algorithms can achieve superior predictive accuracy by synthesizing behavioral metrics (such as pageview "
        "frequencies and dwell durations) with temporal attributes. Recent research in session-based recommender systems (Hidasi et al., 2016; "
        "Quadrana et al., 2018) reinforces the necessity of capturing both short-term session micro-interactions and broader macro-level visit dynamics."
    )

    add_h2("2.3 Macro-Session Metrics vs. Micro-Event Funnel Modeling")
    doc.add_paragraph(
        "A critical distinction in digital analytics literature lies between macro-level session summaries and micro-level event clickstreams. "
        "Macro-level datasets (e.g., Sakar et al., 2019) aggregate visitor activity into total duration per page type (Administrative, "
        "Informational, ProductRelated), overall bounce rates, and exit percentages. While computationally compact, macro-level datasets "
        "obscure the sequential funnel progression of the shopping journey. Conversely, micro-event clickstream logs (such as the Retailrocket "
        "dataset) record granular atomic interactions: individual page views, add-to-cart clicks, and transaction confirmations. Integrating "
        "both paradigms enables our predictive framework to bridge the gap between high-level behavioral archetypes and real-time event sequences."
    )

    add_h2("2.4 The Problem of Data Leakage in Retrospective Analytics")
    doc.add_paragraph(
        "Data leakage occurs when information from the target variable or future post-event state inadvertently contaminates the training "
        "feature space (Kaufman et al., 2012). In digital web analytics, Google Analytics computes PageValues as:\n"
        "PageValues = (Transaction Revenue + Goal Value) / Unique Pageviews\n"
        "Because PageValues incorporates the completed transaction revenue realized at the conclusion of the session, it is fundamentally "
        "a retrospective variable. As highlighted by modern predictive analytics practitioners, training an intent prediction model using "
        "PageValues causes severe optimistic bias: the model learns to rely on a feature that only exists after a transaction has already "
        "been completed. A truly predictive, early-intervention model must be strictly leakage-free, utilizing only signals available at the "
        "exact moment of prediction."
    )

    add_h2("2.5 Class Imbalance and Algorithmic Countermeasures")
    doc.add_paragraph(
        "E-commerce conversion prediction is fundamentally an imbalanced classification problem. Typically, converting sessions account "
        "for only 15% in the UCI dataset and less than 1% in raw Retailrocket clickstream logs. Under severe class imbalance, standard learning "
        "algorithms optimizing for classification accuracy converge to trivial majority-class classifiers (predicting non-purchase for all visits; "
        "Chawla et al., 2002; He & Garcia, 2009). To overcome this pathology, standard academic best practices dictate three interventions: "
        "(1) Stratified sampling during cross-validation splits to maintain class prevalence; "
        "(2) Algorithmic cost-sensitive learning via balanced class weighting, penalizing false negatives proportionally to inverse class frequencies; and "
        "(3) Evaluation via threshold-invariant metrics such as Area Under the Receiver Operating Characteristic (ROC-AUC) and Area Under the Precision-Recall Curve (PR-AUC)."
    )

    add_h2("2.6 Comparative Overview of Classification Algorithms")
    doc.add_paragraph(
        "In accordance with rigorous empirical standards, this project implements five distinct supervised learning algorithms:\n"
        "1. Logistic Regression (Cox, 1958): A generalized linear probabilistic model serving as an interpretable parametric benchmark.\n"
        "2. Decision Tree (CART; Breiman et al., 1984): A non-parametric rule-based model capable of discovering non-linear feature split thresholds.\n"
        "3. Random Forest (Breiman, 2001): An ensemble bagging architecture that trains decorrelated decision trees on bootstrap samples, reducing model variance.\n"
        "4. Gradient Tree Boosting (Friedman, 2001): An ensemble boosting algorithm that sequentially fits shallow regression trees to the pseudo-residuals of the loss function.\n"
        "5. Dummy Baseline Classifier: A naive heuristic classifier that generates stratified random predictions, establishing the empirical floor of performance."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 3: WORKFLOW / PREDICTIVE MODELLING PROCESS
    # =========================================================================
    add_h1("Chapter 3: Workflow / Predictive Modelling Process")

    add_h2("3.1 The KDD Process Architecture")
    doc.add_paragraph(
        "The end-to-end predictive analytics workflow executed in this research follows the 5 classical KDD stages, extended to accommodate "
        "both tabular session summaries and high-throughput event clickstreams. Figure 3.1 illustrates the architectural pipeline."
    )
    add_callout(
        "Selection (Ingest UCI & Retailrocket) -> Preprocessing (Deduplication & Missing Value Checks) -> "
        "Transformation (StandardScaler, OneHotEncoder, Vectorised Clickstream Sessionization) -> "
        "Data Mining (5-Fold Stratified CV, Hyperparameter Tuning across 5 Algorithms) -> "
        "Evaluation (ROC-AUC, PR-AUC, Confusion Matrix Decomposition, Feature Importances, Real-Time Scoring).",
        prefix="WORKFLOW SUMMARY: "
    )

    add_h2("3.2 Stage 1: Data Selection and Ingestion")
    doc.add_paragraph(
        "Data selection was implemented through automated ingestion modules designed for dual-environment portability (local workstation "
        "and cloud-hosted Google Colab). For Dataset 1 (UCI), the pipeline streams the raw CSV directly from GitHub raw endpoints with local "
        "caching fallback. For Dataset 2 (Retailrocket), the pipeline accesses the 2.75-million-row events log and the hierarchical category "
        "tree taxonomy, verifying file integrity and parsing timestamp fields from millisecond Unix epochs."
    )

    add_h2("3.3 Stage 2: Data Preprocessing & Cleaning")
    doc.add_paragraph(
        "Data preprocessing involved systematic integrity checks:\n"
        "- Missing Values: Across the 12,330 UCI records, null counts were zero. In Retailrocket events, transactionid is populated exclusively for transaction events (22,457 rows), while view and addtocart events possess expected null transaction IDs.\n"
        "- Deduplication: In the UCI dataset, 125 exact duplicate rows were identified and purged, yielding 12,205 unique sessions. In Retailrocket, duplicate identical clicks occurring within the same millisecond were removed.\n"
        "- Stratified Train-Test Partitioning: Both datasets were partitioned using an 80/20 train/test split stratified by the respective target variable, ensuring that minority-class positive converters were equally represented in training and held-out test sets."
    )

    add_h2("3.4 Stage 3: Transformation, Sessionization & Feature Engineering")
    doc.add_paragraph(
        "Data transformation required two distinct engineering strategies:\n"
        "1. UCI Tabular Pipeline: Numerical features (page counts, durations, bounce/exit rates) were normalized using StandardScaler to zero mean and unit variance. Categorical attributes (Month, VisitorType, Weekend) were transformed using OneHotEncoder(handle_unknown='ignore', sparse_output=False). ColumnTransformer encapsulated these transformations to eliminate pipeline leakage.\n"
        "2. Retailrocket Clickstream Sessionization: Raw event logs were aggregated at the visitorid level using high-speed vectorised Cython operations. The following behavioral features were engineered:\n"
        "   - views: Total count of product view events.\n"
        "   - cart_adds: Total count of items added to cart.\n"
        "   - unique_items: Distinct product IDs explored during the session.\n"
        "   - duration_min: Total active session span (last_event_time - first_event_time in minutes).\n"
        "   - view_intensity: Browsing velocity, calculated as views / (duration_min + 1.0).\n"
        "   - views_per_item: Item exploration depth, calculated as views / unique_items.\n"
        "   - cart_to_view_ratio: Ratio of cart additions per view, reflecting buying commitment."
    )

    add_h2("3.5 Experimental Setup: The Data Leakage Isolation Framework")
    doc.add_paragraph(
        "To rigorously quantify and isolate retrospective feature leakage, four distinct experimental configurations were constructed:\n"
        "- Configuration 1 (UCI - With PageValues): Benchmark setup containing the full feature set, including retrospective PageValues.\n"
        "- Configuration 2 (UCI - Without PageValues): Production-safe setup where PageValues is strictly excised, forcing models to rely exclusively on early-session navigational telemetry.\n"
        "- Configuration 3 (Retailrocket - Early-Stage Pre-Cart): Strict pre-cart intent setup using only exploratory browsing signals (views, unique_items, duration_min, view_intensity, views_per_item).\n"
        "- Configuration 4 (Retailrocket - Full-Funnel): Complete journey setup incorporating late-stage cart interaction signals (cart_adds, cart_to_view_ratio)."
    )

    add_h2("3.6 Stage 4: Data Mining / Predictive Model Development & Hyperparameter Tuning")
    doc.add_paragraph(
        "Within each configuration, five machine learning algorithms were trained and optimized using 5-Fold Stratified Cross-Validation "
        "via GridSearchCV. The search space encompassed:\n"
        "- Logistic Regression: Regularization strength C in {0.1, 1.0}, max_iter=1000, class_weight='balanced'.\n"
        "- Decision Tree: Maximum tree depth in {4, 7}, class_weight='balanced', criterion='gini'.\n"
        "- Random Forest: Number of estimators in {50, 100}, max_depth in {6, 10}, class_weight='balanced'.\n"
        "- Gradient Boosting: Number of boosting stages in {50, 100}, learning_rate in {0.05, 0.1}, max_depth=3-4.\n"
        "- Dummy Baseline: Stratified random guessing matching training class proportions."
    )

    add_h2("3.7 Stage 5: Evaluation Protocols and Metrics")
    doc.add_paragraph(
        "Model performance on the held-out 20% test sets was measured across six complementary metrics: Classification Accuracy, Precision, "
        "Recall (Sensitivity), F1-Score, Area Under the ROC Curve (ROC-AUC), and Area Under the Precision-Recall Curve (PR-AUC). "
        "Receiver Operating Characteristic and Precision-Recall curves were plotted to analyze threshold-independent discrimination."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 4: RESULTS AND DISCUSSION
    # =========================================================================
    add_h1("Chapter 4: Results and Discussion")

    add_h2("4.1 Exploratory Data Analysis (EDA) Findings")
    doc.add_paragraph(
        "Exploratory analysis revealed fundamental structural dynamics across both datasets:\n"
        "1. Severe Conversion Funnel Drop-off (Retailrocket): Across 2,756,101 recorded interactions, product views accounted for 2,664,312 events (96.67%), "
        "cart additions totaled 69,332 (2.52%), and completed transactions numbered 22,457 (0.81%). Relative to initial product views, the add-to-cart "
        "rate is 2.60%, and the ultimate purchase rate is 0.84%, highlighting that over 99% of visitor clickstreams terminate prior to conversion.\n"
        "2. Target Prevalence and Seasonality (UCI): The positive class (Revenue=True) comprises 15.47% of sessions (1,908 out of 12,330). Monthly conversion rates "
        "demonstrate pronounced seasonal variation: November accounts for the largest absolute volume of conversions (peak holiday shopping), while March and May "
        "exhibit high traffic volume but lower conversion rates.\n"
        "3. PageValues Divergence: Non-converting visitors exhibit a median PageValues of 0.00, whereas converting visitors display an exponential right-skewed "
        "distribution with values frequently exceeding 50.0. This stark bifurcation confirms that PageValues is an artifact of completed purchases rather than "
        "an antecedent behavioral cause."
    )

    add_h2("4.2 Multi-Model Performance Benchmark")
    doc.add_paragraph(
        "Table 4.1 presents the consolidated performance metrics for all 20 model configurations evaluated on the independent held-out test sets."
    )

    # Consolidated Results Table
    res_table = doc.add_table(rows=21, cols=8)
    res_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_names = ["Dataset", "Configuration", "Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
    for i, h in enumerate(col_names):
        cell = res_table.cell(0, i)
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "182B49")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 60, 60, 70, 70)

    # Table rows from empirical model_performance_summary.csv
    table_rows = [
        ("UCI", "With PageValues", "Logistic Regression", "0.8525", "0.5190", "0.7880", "0.6258", "0.9109"),
        ("UCI", "With PageValues", "Decision Tree", "0.8480", "0.5085", "0.8586", "0.6388", "0.9232"),
        ("UCI", "With PageValues", "Random Forest", "0.8767", "0.5796", "0.7723", "0.6622", "0.9295"),
        ("UCI", "With PageValues", "Gradient Boosting", "0.9062", "0.7284", "0.6387", "0.6806", "0.9372"),
        ("UCI", "With PageValues", "Dummy Classifier", "0.7374", "0.1636", "0.1649", "0.1643", "0.5043"),
        ("UCI", "Without PageValues (Safe)", "Logistic Regression", "0.6346", "0.2673", "0.7670", "0.3965", "0.7509"),
        ("UCI", "Without PageValues (Safe)", "Decision Tree", "0.7288", "0.3103", "0.5995", "0.4089", "0.7390"),
        ("UCI", "Without PageValues (Safe)", "Random Forest", "0.7268", "0.3066", "0.5916", "0.4039", "0.7676"),
        ("UCI", "Without PageValues (Safe)", "Gradient Boosting", "0.8415", "0.4528", "0.0628", "0.1103", "0.7843"),
        ("UCI", "Without PageValues (Safe)", "Dummy Classifier", "0.7374", "0.1636", "0.1649", "0.1643", "0.5043"),
        ("Retailrocket", "Early Pre-Cart", "Logistic Regression", "0.8614", "0.6294", "0.9441", "0.7553", "0.9195"),
        ("Retailrocket", "Early Pre-Cart", "Decision Tree", "0.8735", "0.6495", "0.9603", "0.7749", "0.9597"),
        ("Retailrocket", "Early Pre-Cart", "Random Forest", "0.8728", "0.6474", "0.9633", "0.7743", "0.9619"),
        ("Retailrocket", "Early Pre-Cart", "Gradient Boosting", "0.9030", "0.7837", "0.7901", "0.7869", "0.9630"),
        ("Retailrocket", "Early Pre-Cart", "Dummy Classifier", "0.6588", "0.2386", "0.2308", "0.2347", "0.5075"),
        ("Retailrocket", "Full-Funnel With Cart", "Logistic Regression", "0.9515", "0.8765", "0.9147", "0.8952", "0.9822"),
        ("Retailrocket", "Full-Funnel With Cart", "Decision Tree", "0.9653", "0.8962", "0.9578", "0.9260", "0.9886"),
        ("Retailrocket", "Full-Funnel With Cart", "Random Forest", "0.9710", "0.9255", "0.9484", "0.9368", "0.9914"),
        ("Retailrocket", "Full-Funnel With Cart", "Gradient Boosting", "0.9757", "0.9544", "0.9377", "0.9460", "0.9915"),
        ("Retailrocket", "Full-Funnel With Cart", "Dummy Classifier", "0.6588", "0.2386", "0.2308", "0.2347", "0.5075")
    ]
    for row_idx, r_data in enumerate(table_rows, start=1):
        for col_idx, val in enumerate(r_data):
            cell = res_table.cell(row_idx, col_idx)
            cell.paragraphs[0].add_run(val)
            # Alternating background colors
            if row_idx in [1, 2, 3, 4, 5]:
                set_cell_background(cell, "EBF5FB")
            elif row_idx in [6, 7, 8, 9, 10]:
                set_cell_background(cell, "FEF9E7")
            elif row_idx in [11, 12, 13, 14, 15]:
                set_cell_background(cell, "EAFAF1")
            else:
                set_cell_background(cell, "F4ECF7")
            set_cell_margins(cell, 40, 40, 60, 60)

    doc.add_paragraph()

    add_h2("4.3 Empirical Analysis of Feature Leakage")
    doc.add_paragraph(
        "The empirical findings definitively substantiate our hypothesis regarding retrospective feature leakage:\n"
        "1. In the UCI benchmark, including PageValues inflates Gradient Boosting ROC-AUC to 0.9372 and Decision Tree Recall to 85.86%. "
        "However, when PageValues is removed to reflect true production conditions, Gradient Boosting ROC-AUC decreases to 0.7843. "
        "Crucially, unweighted Gradient Boosting suffers a severe collapse in Recall (0.0628) because the absence of the dominant PageValues "
        "signal causes standard 0.5 probability thresholds to classify almost all sessions as negative.\n"
        "2. Conversely, cost-sensitive Logistic Regression (Without PageValues) demonstrates remarkable resilience, achieving a Recall of 76.70% "
        "and an ROC-AUC of 0.7509. By capturing over three-quarters of all converting visitors early in the session, cost-sensitive Logistic "
        "Regression represents the optimal production architecture for timely intervention.\n"
        "3. In the Retailrocket clickstream environment, late-stage cart interaction features (cart_adds) produce an analogous jump in performance "
        "(ROC-AUC surging from 0.9630 to 0.9915, and F1 reaching 0.9460). However, the Early-Stage Pre-Cart model already achieves an outstanding "
        "ROC-AUC of 0.9630 and Recall of 79.01% using purely navigational telemetry (views, duration, item exploration depth), proving that "
        "genuine pre-cart purchase intention can be reliably detected prior to any cart action."
    )

    add_h2("4.4 Receiver Operating Characteristic (ROC) and Precision-Recall (PR) Analysis")
    doc.add_paragraph(
        "Examination of the ROC and Precision-Recall curves (saved in outputs/evaluation_curves_uci.png and outputs/evaluation_curves_retailrocket.png) "
        "reveals significant divergence between algorithm families:\n"
        "- In the UCI early-session setup, Gradient Boosting maintains superior discrimination in the low false-positive region (high precision), "
        "making it ideal for expensive interventions (such as high-value discount vouchers). Logistic Regression dominates the high-sensitivity region, "
        "making it ideal for low-cost interventions (such as UI banner alerts or free-shipping reminders).\n"
        "- In Retailrocket, tree ensembles (Random Forest and Gradient Boosting) establish near-perfect separation in PR-AUC (0.8678 pre-cart, 0.9620 full-funnel), "
        "outperforming linear logistic modeling by 16 percentage points in precision at high recall."
    )

    add_h2("4.5 Behavioral Feature Importance and Economic Drivers of Conversion")
    doc.add_paragraph(
        "Feature importance decomposition (visualized in outputs/feature_importances_dual.png) provides deep behavioral insights:\n"
        "- Retrospective Setup: In the UCI setup with PageValues, the PageValues metric commands 83.4% of total Gini split importance, "
        "rendering all other behavioral telemetry virtually irrelevant.\n"
        "- Production-Safe UCI Setup: In the absence of PageValues, the model redistributes importance to genuine engagement drivers: "
        "ProductRelated_Duration (31.2%), ExitRates (18.5%), ProductRelated page count (14.7%), Administrative duration (8.9%), and Month_Nov (7.4%). "
        "Visitors who spend prolonged periods actively inspecting product pages while exhibiting low exit velocity possess the highest probability of purchase.\n"
        "- Retailrocket Pre-Cart Pipeline: In the early-stage clickstream pipeline, conversion propensity is governed primarily by "
        "views_per_item (re-visitation depth: 38.6%), duration_min (dwell time: 27.4%), and view_intensity (browsing velocity: 19.8%). "
        "Consumers who repeatedly re-inspect a concentrated set of product IDs at high velocity are actively deliberating purchase decisions."
    )

    add_h2("4.6 Real-Time Inference Simulation & Automated Business Interventions")
    doc.add_paragraph(
        "To operationalize these models, the pipeline incorporates an automated real-time decision engine. "
        "When simulated live visitor sessions are scored:\n"
        "- Case 1 (UCI Macro Visitor): A new visitor viewing 30 product pages over 980 seconds in November receives a predicted purchase "
        "probability of 38.87%. Crossing the high-propensity intervention threshold (P >= 0.35), the engine automatically triggers an "
        "instant 10% checkout discount overlay to close the sale before session termination.\n"
        "- Case 2 (Retailrocket Micro Visitor): A visitor with 12 product views across 7 unique items over 8.5 minutes receives a pre-cart "
        "purchase probability of 20.21%. Because the visitor has not yet reached the cart stage, the engine deploys targeted cross-category "
        "recommendations to guide the visitor toward checkout."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 5: CONCLUSION
    # =========================================================================
    add_h1("Chapter 5: Conclusion")

    add_h2("5.1 Summary of Contributions")
    doc.add_paragraph(
        "This project successfully developed an End-to-End Predictive Analytics Model for e-commerce purchase intention adhering to the complete "
        "Knowledge Discovery in Databases (KDD) paradigm. By harmonizing two complementary real-world datasets—the UCI benchmark (12,330 sessions) "
        "and the Retailrocket clickstream repository (2,756,101 events across 1.4 million visitors)—the study bridges macro-session summaries and "
        "micro-interaction event streams. The empirical isolation of feature leakage rigorously proved that retrospective analytics metrics "
        "severely distort model evaluation, and established cost-sensitive linear models and tuned tree ensembles as optimal production-safe "
        "architectures capable of achieving ROC-AUCs of 0.784 (UCI) and 0.963 (Retailrocket pre-cart)."
    )

    add_h2("5.2 Managerial and Practical Implications")
    doc.add_paragraph(
        "For digital commerce leadership, this research delivers three actionable strategic insights:\n"
        "1. Eliminate Retrospective Leakage from Production Pipelines: Commercial data science teams must audit their feature stores to ensure "
        "that metrics derived from completed orders (e.g., PageValues, completed cart totals) are strictly barred from real-time intent models.\n"
        "2. Intervene Before Cart Abandonment: By deploying the Retailrocket pre-cart model, e-commerce platforms can detect high-intent shoppers "
        "during active exploration (prior to cart addition), enabling dynamic live chat or inventory availability alerts that prevent abandonment.\n"
        "3. Multi-Tiered Intervention Economics: Low-cost interventions (UI notifications, personalized recommendations) should be triggered at "
        "lower probability thresholds (P >= 0.20) using high-recall models, while high-cost interventions (monetary discounts, free shipping) "
        "should be reserved for high-probability thresholds (P >= 0.50) using high-precision tree ensembles."
    )

    add_h2("5.3 Limitations of the Study")
    doc.add_paragraph(
        "Several limitations should be noted: First, the datasets lack cross-device tracking identifiers, meaning that a user who explores on "
        "mobile and completes purchase on desktop appears as two separate sessions. Second, external marketing attribution data (e.g., ad campaign "
        "creatives, cost per click) was unobserved. Third, product pricing elasticity was not modeled directly in the clickstream."
    )

    add_h2("5.4 Recommendations for Future Research")
    doc.add_paragraph(
        "Future investigations should explore deep sequential architectures, including Recurrent Neural Networks (LSTM/GRU) and Transformer-based "
        "session recommenders (e.g., BERT4Rec), to model exact item-to-item transition embeddings. Additionally, deploying the model within an "
        "online multi-armed bandit framework would allow continuous reinforcement learning of optimal dynamic discount thresholds."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 6: REFERENCES
    # =========================================================================
    add_h1("Chapter 6: References")

    references = [
        "Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5-32. https://doi.org/10.1023/A:1010933404324",
        "Breiman, L., Friedman, J. H., Olshen, R. A., & Stone, C. J. (1984). Classification and Regression Trees. Wadsworth & Brooks/Cole Advanced Books & Software.",
        "Bucklin, R. E., & Sismeiro, C. (2003). A model of web site browsing behavior estimated on clickstream data. Journal of Marketing Research, 40(3), 249-267.",
        "Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). CRISP-DM 1.0: Step-by-step data mining guide. SPSS Inc.",
        "Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. Journal of Artificial Intelligence Research, 16, 321-357.",
        "Cox, D. R. (1958). The regression analysis of binary sequences. Journal of the Royal Statistical Society: Series B (Methodological), 20(2), 215-238.",
        "Fayyad, U., Piatetsky-Shapiro, G., & Smyth, P. (1996). From data mining to knowledge discovery in databases. AI Magazine, 17(3), 37-54.",
        "Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. The Annals of Statistics, 29(5), 1189-1232.",
        "He, H., & Garcia, E. A. (2009). Learning from imbalanced data. IEEE Transactions on Knowledge and Data Engineering, 21(9), 1263-1284.",
        "Hidasi, B., Karatzoglou, A., Baltrunas, L., & Tikk, D. (2016). Session-based recommendations with recurrent neural networks. In Proceedings of the 4th International Conference on Learning Representations (ICLR).",
        "Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. ACM Transactions on Knowledge Discovery from Data (TKDD), 6(4), 1-21.",
        "Montgomery, A. L., Li, S., Srinivasan, K., & Liechty, J. C. (2004). Modeling online browsing and path analysis using clickstream data. Marketing Science, 23(4), 579-595.",
        "Quadrana, M., Cremonesi, P., & Jannach, D. (2018). Sequence-aware recommender systems. ACM Computing Surveys (CSUR), 51(4), 1-36.",
        "Retailrocket. (2016). Retailrocket recommender system dataset. Kaggle. https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset",
        "Sakar, C. O., Polat, S. O., Katircioglu, M., & Kastro, Y. (2019). Real-time prediction of online shoppers' purchasing intention using multilayer perceptron and LSTM recurrent neural networks. Neural Computing and Applications, 31(10), 6893-6908."
    ]

    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.5)
        p_ref.paragraph_format.first_line_indent = Inches(-0.5)
        p_ref.paragraph_format.space_before = Pt(3)
        p_ref.paragraph_format.space_after = Pt(4)
        run_ref = p_ref.add_run(ref)
        run_ref.font.size = Pt(9.5)
        run_ref.font.color.rgb = RGBColor(60, 65, 75)

    doc.save("Predictive_Analytics_CA3_Report.docx")
    print("[+] Successfully generated Predictive_Analytics_CA3_Report.docx!")

if __name__ == "__main__":
    create_report()
