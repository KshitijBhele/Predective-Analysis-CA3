"""
End-to-End Predictive Analytics: E-Commerce Consumer Conversion Modeling
A Dual-Dataset Predictive Framework Integrating Macro-Session Dynamics (UCI)
and Micro-Clickstream Event Funnels (Retailrocket) with Data Leakage Isolation

Author: Kshitij Bhele
Course: Predictive Analytics (CA3)
Date: October 2026
Repository: https://github.com/KshitijBhele/Predective-Analysis-CA3
"""

import os
import glob
import time
import urllib.request
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for reliable server execution
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, precision_recall_curve, auc, roc_curve, confusion_matrix
)

# Output directory for saved visualizations and summary artifacts
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set visual aesthetic theme
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 15
})

# ==============================================================================
# 1. Dataset Acquisition (Dataset 1: UCI, Dataset 2: Retailrocket)
# ==============================================================================
GITHUB_USERNAME = "KshitijBhele"
REPO_NAME = "Predective-Analysis-CA3"
BRANCH = "main"

UCI_GITHUB_CSV = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/online_shoppers_intention.csv"
UCI_GITHUB_ZIP = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/online+shoppers+purchasing+intention+dataset.zip"

def load_uci_dataset():
    """Load Dataset 1: UCI Online Shoppers Purchasing Intention Dataset."""
    print("=" * 80)
    print("STEP 1A: LOADING DATASET 1 (UCI ONLINE SHOPPERS INTENTION)")
    print("=" * 80)

    # Strategy 1: Local file
    for path in ["online_shoppers_intention.csv", "/content/online_shoppers_intention.csv"]:
        if os.path.exists(path):
            print(f"[+] Found local UCI dataset CSV: {path}")
            df = pd.read_csv(path)
            print(f"    Loaded UCI dataset successfully. Shape: {df.shape}")
            return df

    # Strategy 2: Extract from local zip
    for zpath in ["online+shoppers+purchasing+intention+dataset.zip", "/content/online+shoppers+purchasing+intention+dataset.zip"]:
        if os.path.exists(zpath):
            print(f"[+] Extracting local zip archive: {zpath}")
            with zipfile.ZipFile(zpath, "r") as z:
                z.extractall(".")
            if os.path.exists("online_shoppers_intention.csv"):
                df = pd.read_csv("online_shoppers_intention.csv")
                print(f"    Loaded extracted UCI dataset. Shape: {df.shape}")
                return df

    # Strategy 3: Stream from GitHub
    print(f"Connecting to UCI dataset directly from GitHub: {UCI_GITHUB_CSV}")
    try:
        df = pd.read_csv(UCI_GITHUB_CSV)
        print(f"[+] Successfully streamed UCI dataset from GitHub! Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[-] GitHub streaming failed ({e}). Attempting ZIP download...")

    try:
        urllib.request.urlretrieve(UCI_GITHUB_ZIP, "online_shoppers.zip")
        with zipfile.ZipFile("online_shoppers.zip", "r") as z:
            z.extractall(".")
        return pd.read_csv("online_shoppers_intention.csv")
    except Exception as e:
        raise FileNotFoundError(f"Could not load UCI dataset: {e}")

def load_retailrocket_dataset():
    """Load Dataset 2: Retailrocket E-Commerce Recommender & Clickstream Dataset."""
    print("\n" + "=" * 80)
    print("STEP 1B: LOADING DATASET 2 (RETAILROCKET CLICKSTREAM & EVENTS)")
    print("=" * 80)

    possible_events_paths = [
        "archive (1)/events.csv",
        "archive/events.csv",
        "events.csv",
        "/content/archive (1)/events.csv",
        "/content/archive/events.csv",
        "/content/events.csv"
    ]
    possible_cat_paths = [
        "archive (1)/category_tree.csv",
        "archive/category_tree.csv",
        "category_tree.csv",
        "/content/archive (1)/category_tree.csv",
        "/content/archive/category_tree.csv",
        "/content/category_tree.csv"
    ]

    events_path = None
    for p in possible_events_paths:
        if os.path.exists(p):
            events_path = p
            break

    cat_path = None
    for p in possible_cat_paths:
        if os.path.exists(p):
            cat_path = p
            break

    if not events_path:
        # Check subdirectories
        matches = glob.glob("**/events.csv", recursive=True)
        if matches:
            events_path = matches[0]

    if not events_path:
        raise FileNotFoundError("Could not find Retailrocket events.csv in workspace.")

    print(f"[+] Found Retailrocket events log at: {events_path}")
    if cat_path:
        print(f"[+] Found Retailrocket category tree at: {cat_path}")
        df_cat = pd.read_csv(cat_path)
    else:
        df_cat = None

    t0 = time.time()
    df_events = pd.read_csv(events_path, usecols=['timestamp', 'visitorid', 'event', 'itemid'])
    print(f"    Loaded {len(df_events):,} clickstream events in {time.time()-t0:.2f}s!")
    return df_events, df_cat

# ==============================================================================
# 2. Exploratory Data Analysis & Visualizations
# ==============================================================================
def conduct_eda_uci(df_uci):
    """Generate EDA visualizations for Dataset 1 (UCI)."""
    print("\n" + "=" * 80)
    print("STEP 2A: GENERATING EDA VISUALIZATIONS (UCI DATASET)")
    print("=" * 80)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Target Class Distribution
    sns.countplot(x='Revenue', hue='Revenue', data=df_uci, ax=axes[0, 0], palette='Set2', legend=False)
    axes[0, 0].set_title('Target Class (Revenue) Distribution', fontweight='bold')
    axes[0, 0].set_xlabel('Completed Transaction (Revenue)')
    axes[0, 0].set_ylabel('Number of Sessions')

    # 2. Purchase Rate by Month
    month_order = ['Feb', 'Mar', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sns.barplot(x='Month', y='Revenue', hue='Month', data=df_uci, order=month_order, ax=axes[0, 1], palette='viridis', errorbar=None, legend=False)
    axes[0, 1].set_title('Purchase Conversion Rate by Month', fontweight='bold')
    axes[0, 1].set_ylabel('Conversion Rate')

    # 3. Correlation Heatmap
    num_cols = df_uci.select_dtypes(include=[np.number]).columns.tolist() + ['Revenue']
    corr = df_uci[num_cols].corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=axes[1, 0], cbar=True, square=True)
    axes[1, 0].set_title('Correlation Heatmap (Macro Session Metrics)', fontweight='bold')

    # 4. PageValues Boxplot by Revenue
    sns.boxplot(x='Revenue', y='PageValues', hue='Revenue', data=df_uci, ax=axes[1, 1], palette='Set1', legend=False)
    axes[1, 1].set_title('PageValues Distribution by Revenue (Data Leakage Source)', fontweight='bold')
    axes[1, 1].set_yscale('log')
    axes[1, 1].set_ylabel('PageValues (Log Scale)')

    plt.tight_layout()
    uci_eda_path = os.path.join(OUTPUT_DIR, "eda_analysis_uci.png")
    plt.savefig(uci_eda_path, dpi=300)
    plt.close()
    print(f"[+] Saved UCI EDA plot to: {uci_eda_path}")

def conduct_eda_retailrocket(df_events, df_cat):
    """Generate EDA visualizations for Dataset 2 (Retailrocket)."""
    print("\n" + "=" * 80)
    print("STEP 2B: GENERATING EDA VISUALIZATIONS (RETAILROCKET DATASET)")
    print("=" * 80)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Event Type Volume (Funnel Breakdown)
    event_counts = df_events['event'].value_counts()
    sns.barplot(x=event_counts.index, y=event_counts.values, hue=event_counts.index, ax=axes[0, 0], palette='Blues_r', legend=False)
    axes[0, 0].set_title('Total Clickstream Events by Interaction Type', fontweight='bold')
    axes[0, 0].set_yscale('log')
    axes[0, 0].set_ylabel('Event Count (Log Scale)')
    for idx, (ev, val) in enumerate(event_counts.items()):
        axes[0, 0].text(idx, val * 1.15, f"{val:,}", ha='center', fontweight='bold')

    # 2. Conversion Funnel Drop-off Rate
    views = event_counts.get('view', 1)
    carts = event_counts.get('addtocart', 0)
    trans = event_counts.get('transaction', 0)
    funnel_stages = ['Product View', 'Add To Cart', 'Completed Purchase']
    funnel_pct = [100.0, (carts / views) * 100.0, (trans / views) * 100.0]
    sns.barplot(x=funnel_stages, y=funnel_pct, hue=funnel_stages, ax=axes[0, 1], palette='Purples_r', legend=False)
    axes[0, 1].set_title('E-Commerce Conversion Funnel Progression (%)', fontweight='bold')
    axes[0, 1].set_ylabel('Percentage Relative to Views (%)')
    for idx, val in enumerate(funnel_pct):
        axes[0, 1].text(idx, val + 2.0, f"{val:.2f}%", ha='center', fontweight='bold')
    axes[0, 1].set_ylim(0, 115)

    # 3. Event Velocity over Time (Day of Week Analysis)
    dt_series = pd.to_datetime(df_events['timestamp'].iloc[:200000], unit='ms')
    dow_counts = dt_series.dt.day_name().value_counts().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    sns.barplot(x=dow_counts.index, y=dow_counts.values, hue=dow_counts.index, ax=axes[1, 0], palette='crest', legend=False)
    axes[1, 0].set_title('Clickstream Event Distribution by Day of Week', fontweight='bold')
    axes[1, 0].set_ylabel('Interaction Volume')
    axes[1, 0].tick_params(axis='x', rotation=30)

    # 4. Category Tree Depth (if category table available)
    if df_cat is not None:
        root_count = df_cat['parentid'].isnull().sum()
        subcat_count = df_cat['parentid'].notnull().sum()
        cat_labels = ['Root Categories', 'Subcategories']
        cat_values = [root_count, subcat_count]
        axes[1, 1].pie(cat_values, labels=cat_labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
        axes[1, 1].set_title(f'Product Taxonomy Structure ({len(df_cat):,} Total Categories)', fontweight='bold')
    else:
        axes[1, 1].text(0.5, 0.5, "Category tree metadata not present", ha='center')

    plt.tight_layout()
    rr_eda_path = os.path.join(OUTPUT_DIR, "eda_analysis_retailrocket.png")
    plt.savefig(rr_eda_path, dpi=300)
    plt.close()
    print(f"[+] Saved Retailrocket EDA plot to: {rr_eda_path}")

# ==============================================================================
# 3. Sessionization & Preprocessing for Both Datasets
# ==============================================================================
def process_uci_data(df_uci):
    """Preprocess UCI Dataset and create Leakage-Split Pipelines."""
    print("\n" + "=" * 80)
    print("STEP 3A: PREPROCESSING & DATA LEAKAGE PIPELINES (UCI DATASET)")
    print("=" * 80)
    df_clean = df_uci.drop_duplicates().reset_index(drop=True)
    print(f"Cleaned UCI sessions (duplicates removed): {df_clean.shape[0]} rows")

    X = df_clean.drop(columns=['Revenue'])
    y = df_clean['Revenue'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    num_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num_cols_no_pv = [c for c in num_cols if c != 'PageValues']

    num_pipe = Pipeline([('scaler', StandardScaler())])
    cat_pipe = Pipeline([('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])

    # Config 1: With PageValues (Retrospective Data Leakage)
    preprocessor_with = ColumnTransformer([
        ('num', num_pipe, num_cols),
        ('cat', cat_pipe, cat_cols)
    ])
    X_train_with = preprocessor_with.fit_transform(X_train)
    X_test_with = preprocessor_with.transform(X_test)

    # Config 2: Without PageValues (Production Safe / Early Session)
    preprocessor_no = ColumnTransformer([
        ('num', num_pipe, num_cols_no_pv),
        ('cat', cat_pipe, cat_cols)
    ])
    X_train_no = preprocessor_no.fit_transform(X_train)
    X_test_no = preprocessor_no.transform(X_test)

    print(f"[+] UCI Features (With PageValues): {X_train_with.shape[1]}")
    print(f"[+] UCI Features (Without PageValues - Safe): {X_train_no.shape[1]}")

    return {
        'X_train_with': X_train_with, 'X_test_with': X_test_with,
        'X_train_no': X_train_no, 'X_test_no': X_test_no,
        'y_train': y_train, 'y_test': y_test,
        'preprocessor_with': preprocessor_with, 'preprocessor_no': preprocessor_no,
        'num_cols': num_cols, 'num_cols_no_pv': num_cols_no_pv, 'cat_cols': cat_cols
    }

def process_retailrocket_data(df_events):
    """
    Sessionize Retailrocket clickstream into behavioral visitor profiles.
    Construct Early-Stage (Pre-Cart) vs Full-Funnel feature sets.
    """
    print("\n" + "=" * 80)
    print("STEP 3B: CLICKSTREAM SESSIONIZATION & FEATURE ENGINEERING (RETAILROCKET)")
    print("=" * 80)
    t0 = time.time()

    # Fast vectorised event indicator flags
    df_events['is_view'] = (df_events['event'] == 'view').astype('int32')
    df_events['is_cart'] = (df_events['event'] == 'addtocart').astype('int32')
    df_events['is_trans'] = (df_events['event'] == 'transaction').astype('int32')

    # Session aggregation per visitor
    visitors = df_events.groupby('visitorid').agg(
        views=('is_view', 'sum'),
        cart_adds=('is_cart', 'sum'),
        transactions=('is_trans', 'sum'),
        unique_items=('itemid', 'nunique'),
        first_time=('timestamp', 'min'),
        last_time=('timestamp', 'max')
    ).reset_index()

    # Feature Engineering
    visitors['has_transaction'] = (visitors['transactions'] > 0).astype('int32')
    visitors['duration_min'] = (visitors['last_time'] - visitors['first_time']) / 60000.0
    visitors['view_intensity'] = visitors['views'] / (visitors['duration_min'] + 1.0)
    visitors['views_per_item'] = visitors['views'] / np.maximum(visitors['unique_items'], 1)
    visitors['cart_to_view_ratio'] = visitors['cart_adds'] / np.maximum(visitors['views'], 1)

    print(f"[+] Sessionized {len(visitors):,} visitors in {time.time()-t0:.2f}s!")
    print(f"    Total converting visitors (buyers): {visitors['has_transaction'].sum():,}")
    print(f"    Total non-converting visitors: {(visitors['has_transaction'] == 0).sum():,}")

    # Representative stratified modeling sample: all buyers + 40,000 non-buyers
    np.random.seed(42)
    buyers = visitors[visitors['has_transaction'] == 1]
    non_buyers = visitors[visitors['has_transaction'] == 0].sample(n=40000, random_state=42)
    sample_df = pd.concat([buyers, non_buyers]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    print(f"    Modeling sample size: {len(sample_df):,} visitors (Conversion rate: {sample_df['has_transaction'].mean():.2%})")

    # Define Funnel Configurations
    # Config 1: Early-Stage Browsing (Pre-Cart Intent)
    early_features = ['views', 'unique_items', 'duration_min', 'view_intensity', 'views_per_item']
    # Config 2: Full-Funnel Journey (includes late-stage Cart Actions)
    full_features = early_features + ['cart_adds', 'cart_to_view_ratio']

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        sample_df[full_features], sample_df['has_transaction'], test_size=0.20, random_state=42, stratify=sample_df['has_transaction']
    )

    # Standardize numerical features
    scaler_early = StandardScaler()
    X_train_early = scaler_early.fit_transform(X_train_raw[early_features])
    X_test_early = scaler_early.transform(X_test_raw[early_features])

    scaler_full = StandardScaler()
    X_train_full = scaler_full.fit_transform(X_train_raw[full_features])
    X_test_full = scaler_full.transform(X_test_raw[full_features])

    print(f"[+] Retailrocket Early-Stage Features: {len(early_features)}")
    print(f"[+] Retailrocket Full-Funnel Features: {len(full_features)}")

    return {
        'X_train_early': X_train_early, 'X_test_early': X_test_early,
        'X_train_full': X_train_full, 'X_test_full': X_test_full,
        'y_train': y_train, 'y_test': y_test,
        'early_features': early_features, 'full_features': full_features,
        'sample_df': sample_df, 'scaler_early': scaler_early, 'scaler_full': scaler_full
    }

# ==============================================================================
# 4. Multi-Model Training & Cross-Validation
# ==============================================================================
def train_model_suite(X_train, y_train, dataset_name, config_name):
    """Train and tune 5 machine learning models using Stratified 5-Fold CV."""
    print(f"\n--> Training 5-Model Suite for: [{dataset_name}] - [{config_name}]")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    model_specs = {
        'Logistic Regression': (
            LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
            {'C': [0.1, 1.0]}
        ),
        'Decision Tree': (
            DecisionTreeClassifier(class_weight='balanced', random_state=42),
            {'max_depth': [4, 7]}
        ),
        'Random Forest': (
            RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1),
            {'n_estimators': [50, 100], 'max_depth': [6, 10]}
        ),
        'Gradient Boosting': (
            GradientBoostingClassifier(random_state=42),
            {'n_estimators': [50, 100], 'learning_rate': [0.05, 0.1]}
        )
    }

    trained_models = {}
    for name, (base_clf, grid) in model_specs.items():
        t0 = time.time()
        gs = GridSearchCV(base_clf, grid, cv=cv, scoring='roc_auc', n_jobs=-1)
        gs.fit(X_train, y_train)
        trained_models[name] = {
            'best_estimator': gs.best_estimator_,
            'best_params': gs.best_params_,
            'cv_roc_auc': gs.best_score_
        }
        print(f"    [OK] {name:<20} | 5-Fold CV ROC-AUC: {gs.best_score_:.4f} | Time: {time.time()-t0:.2f}s")

    # Baseline: Dummy Classifier
    dummy = DummyClassifier(strategy='stratified', random_state=42)
    dummy.fit(X_train, y_train)
    trained_models['Dummy Classifier'] = {
        'best_estimator': dummy,
        'best_params': {'strategy': 'stratified'},
        'cv_roc_auc': 0.5000
    }
    print(f"    [OK] {'Dummy Classifier':<20} | Baseline CV ROC-AUC: 0.5000")

    return trained_models

# ==============================================================================
# 5. Comprehensive Model Evaluation & Visual Comparison
# ==============================================================================
def evaluate_models(models_dict, X_test, y_test, dataset_name, config_name):
    """Evaluate trained models on held-out test data and record all metrics."""
    rows = []
    for model_name, info in models_dict.items():
        m = info['best_estimator']
        preds = m.predict(X_test)
        probs = m.predict_proba(X_test)[:, 1] if hasattr(m, 'predict_proba') else preds.astype(float)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        roc = roc_auc_score(y_test, probs)
        p_curve, r_curve, _ = precision_recall_curve(y_test, probs)
        pr_auc = auc(r_curve, p_curve)

        rows.append({
            'Dataset': dataset_name,
            'Configuration': config_name,
            'Model': model_name,
            'Accuracy': round(acc, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'F1-Score': round(f1, 4),
            'ROC-AUC': round(roc, 4),
            'PR-AUC': round(pr_auc, 4)
        })
    return pd.DataFrame(rows)

def plot_curves(models_dict_1, models_dict_2, X_test_1, X_test_2, y_test_1, y_test_2,
                title1, title2, save_filename):
    """Plot dual-configuration ROC and PR curves."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    setups = [
        (models_dict_1, X_test_1, y_test_1, title1, axes[0, 0], axes[0, 1]),
        (models_dict_2, X_test_2, y_test_2, title2, axes[1, 0], axes[1, 1])
    ]

    for m_dict, X_t, y_t, title, ax_roc, ax_pr in setups:
        for m_name, info in m_dict.items():
            m = info['best_estimator']
            probs = m.predict_proba(X_t)[:, 1] if hasattr(m, 'predict_proba') else m.predict(X_t).astype(float)
            fpr, tpr, _ = roc_curve(y_t, probs)
            roc_val = roc_auc_score(y_t, probs)
            p_curve, r_curve, _ = precision_recall_curve(y_t, probs)
            pr_val = auc(r_curve, p_curve)

            ax_roc.plot(fpr, tpr, label=f"{m_name} ({roc_val:.3f})")
            ax_pr.plot(r_curve, p_curve, label=f"{m_name} ({pr_val:.3f})")

        ax_roc.plot([0, 1], [0, 1], 'k--', alpha=0.6)
        ax_roc.set_title(f'ROC Curves: {title}', fontweight='bold')
        ax_roc.set_xlabel('False Positive Rate')
        ax_roc.set_ylabel('True Positive Rate')
        ax_roc.legend(loc='lower right')

        ax_pr.set_title(f'Precision-Recall Curves: {title}', fontweight='bold')
        ax_pr.set_xlabel('Recall')
        ax_pr.set_ylabel('Precision')
        ax_pr.legend(loc='lower left')

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, save_filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[+] Saved curves visualization to: {save_path}")

def plot_dual_feature_importances(uci_data, uci_models_with, uci_models_no,
                                  rr_data, rr_models_early, rr_models_full):
    """Generate side-by-side feature importance comparisons for both datasets."""
    # UCI feature names
    cat_enc_with = uci_data['preprocessor_with'].named_transformers_['cat'].named_steps['onehot']
    uci_feat_with = uci_data['num_cols'] + cat_enc_with.get_feature_names_out(uci_data['cat_cols']).tolist()

    cat_enc_no = uci_data['preprocessor_no'].named_transformers_['cat'].named_steps['onehot']
    uci_feat_no = uci_data['num_cols_no_pv'] + cat_enc_no.get_feature_names_out(uci_data['cat_cols']).tolist()

    gb_uci_with = uci_models_with['Gradient Boosting']['best_estimator']
    gb_uci_no = uci_models_no['Gradient Boosting']['best_estimator']
    gb_rr_early = rr_models_early['Gradient Boosting']['best_estimator']
    gb_rr_full = rr_models_full['Gradient Boosting']['best_estimator']

    imp_uci_with = pd.DataFrame({'Feature': uci_feat_with, 'Importance': gb_uci_with.feature_importances_}).sort_values('Importance', ascending=False).head(8)
    imp_uci_no = pd.DataFrame({'Feature': uci_feat_no, 'Importance': gb_uci_no.feature_importances_}).sort_values('Importance', ascending=False).head(8)
    imp_rr_early = pd.DataFrame({'Feature': rr_data['early_features'], 'Importance': gb_rr_early.feature_importances_}).sort_values('Importance', ascending=False)
    imp_rr_full = pd.DataFrame({'Feature': rr_data['full_features'], 'Importance': gb_rr_full.feature_importances_}).sort_values('Importance', ascending=False)

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))

    sns.barplot(x='Importance', y='Feature', hue='Feature', data=imp_uci_with, ax=axes[0, 0], palette='Blues_r', legend=False)
    axes[0, 0].set_title('UCI: Top Features (With PageValues - Retrospective Leakage)', fontweight='bold')

    sns.barplot(x='Importance', y='Feature', hue='Feature', data=imp_uci_no, ax=axes[0, 1], palette='Oranges_r', legend=False)
    axes[0, 1].set_title('UCI: Top Features (Without PageValues - Safe Early Session)', fontweight='bold')

    sns.barplot(x='Importance', y='Feature', hue='Feature', data=imp_rr_early, ax=axes[1, 0], palette='Greens_r', legend=False)
    axes[1, 0].set_title('Retailrocket: Early-Stage Clickstream Features (Pre-Cart)', fontweight='bold')

    sns.barplot(x='Importance', y='Feature', hue='Feature', data=imp_rr_full, ax=axes[1, 1], palette='Purples_r', legend=False)
    axes[1, 1].set_title('Retailrocket: Full-Funnel Clickstream Features (With Cart)', fontweight='bold')

    plt.tight_layout()
    dual_imp_path = os.path.join(OUTPUT_DIR, "feature_importances_dual.png")
    plt.savefig(dual_imp_path, dpi=300)
    plt.close()
    print(f"[+] Saved Dual Feature Importance plot to: {dual_imp_path}")

# ==============================================================================
# 6. Real-Time Inference & Dynamic Intervention Simulation
# ==============================================================================
def simulate_realtime_decisions(uci_data, uci_models_no, rr_data, rr_models_early):
    """Simulate real-time visitor scoring and automated business interventions."""
    print("\n" + "=" * 80)
    print("STEP 6: REAL-TIME INFERENCE & AUTOMATED INTERVENTION SIMULATION")
    print("=" * 80)

    # 1. Macro Session Visitor (UCI Pipeline)
    mock_uci_visitor = pd.DataFrame([{
        'Administrative': 6, 'Administrative_Duration': 110.0,
        'Informational': 2, 'Informational_Duration': 45.0,
        'ProductRelated': 30, 'ProductRelated_Duration': 980.0,
        'BounceRates': 0.005, 'ExitRates': 0.02,
        'SpecialDay': 0.0, 'Month': 'Nov',
        'OperatingSystems': 2, 'Browser': 2, 'Region': 1,
        'TrafficType': 2, 'VisitorType': 'New_Visitor', 'Weekend': True
    }])
    prod_uci_clf = uci_models_no['Gradient Boosting']['best_estimator']
    proc_uci = uci_data['preprocessor_no'].transform(mock_uci_visitor)
    uci_prob = prod_uci_clf.predict_proba(proc_uci)[0, 1]

    print("\n[Case 1: Macro-Session Visitor Inference (UCI Framework)]")
    print(f"Visitor Profile: 30 Product Pages, 980s Active Time, Nov Session, New Visitor")
    print(f"Predicted Purchase Probability (Leakage-Free): {uci_prob * 100:.2f}%")
    if uci_prob >= 0.35:
        print("--> Dynamic Trigger: HIGH CONVERSION PROBABILITY -> Offer limited-time 10% instant checkout voucher.")
    else:
        print("--> Dynamic Trigger: Low conversion signal -> Standard browsing layout.")

    # 2. Micro Clickstream Visitor (Retailrocket Pipeline)
    mock_rr_visitor = pd.DataFrame([{
        'views': 12, 'unique_items': 7, 'duration_min': 8.5,
        'view_intensity': 12 / (8.5 + 1.0), 'views_per_item': 12 / 7.0
    }])
    prod_rr_clf = rr_models_early['Gradient Boosting']['best_estimator']
    proc_rr = rr_data['scaler_early'].transform(mock_rr_visitor)
    rr_prob = prod_rr_clf.predict_proba(proc_rr)[0, 1]

    print("\n[Case 2: Micro-Clickstream Visitor Inference (Retailrocket Framework)]")
    print(f"Visitor Profile: 12 Product Views, 7 Unique Items, 8.5 Min Active Duration (Pre-Cart)")
    print(f"Predicted Pre-Cart Purchase Probability: {rr_prob * 100:.2f}%")
    if rr_prob >= 0.50:
        print("--> Dynamic Trigger: STRONG PRE-CART BUYING INTENT -> Trigger proactive live assistant & free shipping badge.")
    else:
        print("--> Dynamic Trigger: Exploratory browsing -> Display related popular trending recommendations.")

# ==============================================================================
# Main Orchestration Pipeline
# ==============================================================================
def main():
    print("=" * 80)
    print("END-TO-END PREDICTIVE MODELING: DUAL-DATASET E-COMMERCE CONVERSION")
    print("=" * 80)
    total_start = time.time()

    # 1. Ingestion
    df_uci = load_uci_dataset()
    df_events, df_cat = load_retailrocket_dataset()

    # 2. EDA
    conduct_eda_uci(df_uci)
    conduct_eda_retailrocket(df_events, df_cat)

    # 3. Preprocessing & Feature Engineering
    uci_data = process_uci_data(df_uci)
    rr_data = process_retailrocket_data(df_events)

    # 4. Multi-Model Training across both datasets
    # Dataset 1: UCI
    uci_models_with = train_model_suite(
        uci_data['X_train_with'], uci_data['y_train'],
        "UCI Shoppers", "With PageValues (Leakage)"
    )
    uci_models_no = train_model_suite(
        uci_data['X_train_no'], uci_data['y_train'],
        "UCI Shoppers", "Without PageValues (Safe)"
    )

    # Dataset 2: Retailrocket
    rr_models_early = train_model_suite(
        rr_data['X_train_early'], rr_data['y_train'],
        "Retailrocket", "Early-Stage Browsing (Pre-Cart)"
    )
    rr_models_full = train_model_suite(
        rr_data['X_train_full'], rr_data['y_train'],
        "Retailrocket", "Full-Funnel Journey (With Cart)"
    )

    # 5. Model Evaluation
    print("\n" + "=" * 80)
    print("STEP 5: COMPREHENSIVE BENCHMARK EVALUATION")
    print("=" * 80)

    df_eval_uci_with = evaluate_models(uci_models_with, uci_data['X_test_with'], uci_data['y_test'], "UCI Shoppers", "With PageValues")
    df_eval_uci_no = evaluate_models(uci_models_no, uci_data['X_test_no'], uci_data['y_test'], "UCI Shoppers", "Without PageValues (Safe)")
    df_eval_rr_early = evaluate_models(rr_models_early, rr_data['X_test_early'], rr_data['y_test'], "Retailrocket", "Early-Stage Browsing (Pre-Cart)")
    df_eval_rr_full = evaluate_models(rr_models_full, rr_data['X_test_full'], rr_data['y_test'], "Retailrocket", "Full-Funnel Journey (With Cart)")

    summary_df = pd.concat([df_eval_uci_with, df_eval_uci_no, df_eval_rr_early, df_eval_rr_full], ignore_index=True)

    print("\n=== CONSOLIDATED MODEL PERFORMANCE BENCHMARK ===")
    print(summary_df.to_string(index=False))

    summary_csv_path = os.path.join(OUTPUT_DIR, "model_performance_summary.csv")
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"\n[+] Saved consolidated benchmark table to: {summary_csv_path}")

    # 6. Evaluation Curves
    plot_curves(
        uci_models_with, uci_models_no,
        uci_data['X_test_with'], uci_data['X_test_no'],
        uci_data['y_test'], uci_data['y_test'],
        "UCI: With PageValues", "UCI: Without PageValues (Safe)",
        "evaluation_curves_uci.png"
    )

    plot_curves(
        rr_models_early, rr_models_full,
        rr_data['X_test_early'], rr_data['X_test_full'],
        rr_data['y_test'], rr_data['y_test'],
        "Retailrocket: Early-Stage Browsing", "Retailrocket: Full-Funnel Journey",
        "evaluation_curves_retailrocket.png"
    )

    # 7. Dual Feature Importance Plot
    plot_dual_feature_importances(
        uci_data, uci_models_with, uci_models_no,
        rr_data, rr_models_early, rr_models_full
    )

    # 8. Real-Time Intervention Simulation
    simulate_realtime_decisions(uci_data, uci_models_no, rr_data, rr_models_early)

    print("\n" + "=" * 80)
    print(f"DUAL-DATASET PREDICTIVE PIPELINE COMPLETE IN {time.time()-total_start:.2f}s!")
    print("=" * 80)

if __name__ == "__main__":
    main()
