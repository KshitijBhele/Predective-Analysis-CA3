"""
Online Purchase Intention Prediction Using Machine Learning
Real-Time E-Commerce Purchase Intent Prediction and Leakage-Robust Modeling

Author: Kshitij Bhele
Repository: https://github.com/KshitijBhele/Predective-Analysis-CA3
"""

import os
import urllib.request
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for terminal execution
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

# Output directory for saved visualizations
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# 1. Dataset Acquisition (Directly Connected to GitHub)
# ==============================================================================
GITHUB_USERNAME = "KshitijBhele"
REPO_NAME = "Predective-Analysis-CA3"
BRANCH = "main"

GITHUB_RAW_CSV_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/online_shoppers_intention.csv"
GITHUB_RAW_ZIP_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/online+shoppers+purchasing+intention+dataset.zip"

LOCAL_CSV_PATHS = ["online_shoppers_intention.csv", "/content/online_shoppers_intention.csv"]
LOCAL_ZIP_PATHS = ["online+shoppers+purchasing+intention+dataset.zip", "/content/online+shoppers+purchasing+intention+dataset.zip"]

def load_dataset():
    print("=" * 70)
    print("STEP 1: LOADING DATASET")
    print("=" * 70)

    # Strategy 1: Attempt to stream CSV directly from GitHub
    print(f"Connecting to dataset directly from GitHub: {GITHUB_RAW_CSV_URL}")
    try:
        df = pd.read_csv(GITHUB_RAW_CSV_URL)
        print(f"[+] Successfully streamed dataset directly from GitHub! Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[-] Direct GitHub URL fetch not yet available or offline ({e}).")

    # Strategy 2: Check for local CSV
    for path in LOCAL_CSV_PATHS:
        if os.path.exists(path):
            print(f"[+] Found local dataset CSV: {path}")
            df = pd.read_csv(path)
            print(f"Loaded dataset. Shape: {df.shape}")
            return df

    # Strategy 3: Download ZIP from GitHub or use local ZIP
    zip_target = "online+shoppers+purchasing+intention+dataset.zip"
    if not any(os.path.exists(p) for p in LOCAL_ZIP_PATHS):
        print(f"Downloading ZIP archive from GitHub: {GITHUB_RAW_ZIP_URL}")
        try:
            urllib.request.urlretrieve(GITHUB_RAW_ZIP_URL, zip_target)
            print("[+] Download complete.")
        except Exception as e:
            print(f"[-] Failed to download ZIP from GitHub: {e}")

    for zpath in [zip_target] + LOCAL_ZIP_PATHS:
        if os.path.exists(zpath):
            print(f"Extracting dataset archive: {zpath}")
            with zipfile.ZipFile(zpath, "r") as z:
                z.extractall(".")
            if os.path.exists("online_shoppers_intention.csv"):
                df = pd.read_csv("online_shoppers_intention.csv")
                print(f"[+] Loaded extracted dataset. Shape: {df.shape}")
                return df

    raise FileNotFoundError("Could not locate or download online_shoppers_intention dataset.")

def main():
    df = load_dataset()

    print("\n--- Dataset Summary ---")
    print(f"Total Rows: {df.shape[0]}, Total Columns: {df.shape[1]}")
    print(f"Target 'Revenue' distribution:\n{df['Revenue'].value_counts(normalize=True)}")
    print(f"Duplicate rows identified: {df.duplicated().sum()}")

    # ==============================================================================
    # 2. Exploratory Visualizations
    # ==============================================================================
    print("\n" + "=" * 70)
    print("STEP 2: GENERATING EDA VISUALIZATIONS")
    print("=" * 70)
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    # Target Distribution
    sns.countplot(x='Revenue', hue='Revenue', data=df, ax=axes[0, 0], palette='Set2', legend=False)
    axes[0, 0].set_title('Target Class (Revenue) Distribution', fontsize=13, fontweight='bold')

    # Purchase Rate by Month
    month_order = ['Feb', 'Mar', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sns.barplot(x='Month', y='Revenue', hue='Month', data=df, order=month_order, ax=axes[0, 1], palette='viridis', errorbar=None, legend=False)
    axes[0, 1].set_title('Purchase Rate by Month', fontsize=13, fontweight='bold')

    # Correlation Heatmap
    numerical_cols_all = df.select_dtypes(include=[np.number]).columns.tolist() + ['Revenue']
    corr_matrix = df[numerical_cols_all].corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=axes[1, 0], cbar=True, square=True)
    axes[1, 0].set_title('Correlation Heatmap (Numerical Features)', fontsize=13, fontweight='bold')

    # PageValues Distribution
    sns.boxplot(x='Revenue', y='PageValues', hue='Revenue', data=df, ax=axes[1, 1], palette='Set1', legend=False)
    axes[1, 1].set_title('PageValues Distribution by Revenue', fontsize=13, fontweight='bold')

    plt.tight_layout()
    eda_path = os.path.join(OUTPUT_DIR, "eda_analysis.png")
    plt.savefig(eda_path, dpi=300)
    plt.close()
    print(f"[+] Saved EDA visualizations to: {eda_path}")

    # ==============================================================================
    # 3. Robust Preprocessing Pipeline
    # ==============================================================================
    print("\n" + "=" * 70)
    print("STEP 3: PREPROCESSING & DATA LEAKAGE ISOLATION")
    print("=" * 70)
    df_clean = df.drop_duplicates().reset_index(drop=True)
    print(f"Dataset shape after duplicate removal: {df_clean.shape}")

    X = df_clean.drop(columns=['Revenue'])
    y = df_clean['Revenue']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    numerical_cols_no_pv = [c for c in numerical_cols if c != 'PageValues']

    num_pipeline = Pipeline([('scaler', StandardScaler())])
    cat_pipeline = Pipeline([('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])

    # Pipeline A: With PageValues
    preprocessor_with = ColumnTransformer([
        ('num', num_pipeline, numerical_cols),
        ('cat', cat_pipeline, categorical_cols)
    ])
    X_train_processed = preprocessor_with.fit_transform(X_train)
    X_test_processed = preprocessor_with.transform(X_test)

    # Pipeline B: Without PageValues (Production Leakage Safe)
    preprocessor_no = ColumnTransformer([
        ('num', num_pipeline, numerical_cols_no_pv),
        ('cat', cat_pipeline, categorical_cols)
    ])
    X_train_no_pv = preprocessor_no.fit_transform(X_train)
    X_test_no_pv = preprocessor_no.transform(X_test)

    print(f"Training features (With PageValues): {X_train_processed.shape[1]}")
    print(f"Training features (Without PageValues): {X_train_no_pv.shape[1]}")

    # ==============================================================================
    # 4. Model Training & Hyperparameter Tuning
    # ==============================================================================
    print("\n" + "=" * 70)
    print("STEP 4: TRAINING & TUNING MACHINE LEARNING MODELS")
    print("=" * 70)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    param_grids = {
        'Logistic Regression': {
            'model': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
            'params': {'C': [0.1, 1.0]}
        },
        'Decision Tree': {
            'model': DecisionTreeClassifier(class_weight='balanced', random_state=42),
            'params': {'max_depth': [3, 5, 8]}
        },
        'Random Forest': {
            'model': RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1),
            'params': {'n_estimators': [50, 100], 'max_depth': [5, 10]}
        },
        'Gradient Boosting': {
            'model': GradientBoostingClassifier(random_state=42),
            'params': {'n_estimators': [50, 100], 'learning_rate': [0.05, 0.1]}
        }
    }

    results = {'with_pv': {}, 'no_pv': {}}

    for config_name, X_tr in [('with_pv', X_train_processed), ('no_pv', X_train_no_pv)]:
        label = "WITH PageValues" if config_name == 'with_pv' else "WITHOUT PageValues (Leakage-Safe)"
        print(f"\n--> Training Setup: {label}")
        for model_name, cfg in param_grids.items():
            print(f"    Tuning {model_name}...")
            gs = GridSearchCV(cfg['model'], cfg['params'], cv=cv, scoring='roc_auc', n_jobs=-1)
            gs.fit(X_tr, y_train)
            results[config_name][model_name] = {
                'best_estimator': gs.best_estimator_,
                'best_params': gs.best_params_,
                'best_score': gs.best_score_
            }
            print(f"    Best params: {gs.best_params_} | 5-Fold CV ROC-AUC: {gs.best_score_:.4f}")

        # Add Dummy Classifier baseline
        dummy = DummyClassifier(strategy='stratified', random_state=42)
        dummy.fit(X_tr, y_train)
        results[config_name]['Dummy'] = {
            'best_estimator': dummy,
            'best_params': {'strategy': 'stratified'},
            'best_score': 0.5000
        }

    # ==============================================================================
    # 5. Comprehensive Model Evaluation
    # ==============================================================================
    print("\n" + "=" * 70)
    print("STEP 5: EVALUATION ON HELD-OUT TEST SET")
    print("=" * 70)

    eval_rows = []
    configs = {
        'with_pv': {'X_test': X_test_processed, 'label': 'With PageValues'},
        'no_pv': {'X_test': X_test_no_pv, 'label': 'Without PageValues'}
    }

    for config_key, setup in configs.items():
        X_t = setup['X_test']
        label = setup['label']
        for model_name, info in results[config_key].items():
            m = info['best_estimator']
            preds = m.predict(X_t)
            probs = m.predict_proba(X_t)[:, 1] if hasattr(m, 'predict_proba') else preds.astype(float)

            acc = accuracy_score(y_test, preds)
            prec = precision_score(y_test, preds, zero_division=0)
            rec = recall_score(y_test, preds, zero_division=0)
            f1 = f1_score(y_test, preds, zero_division=0)
            roc_auc = roc_auc_score(y_test, probs)
            p_pts, r_pts, _ = precision_recall_curve(y_test, probs)
            pr_auc = auc(r_pts, p_pts)

            eval_rows.append({
                'Configuration': label,
                'Model': model_name,
                'Accuracy': round(acc, 4),
                'Precision': round(prec, 4),
                'Recall': round(rec, 4),
                'F1-Score': round(f1, 4),
                'ROC-AUC': round(roc_auc, 4),
                'PR-AUC': round(pr_auc, 4)
            })

    df_eval = pd.DataFrame(eval_rows)
    print(df_eval.to_string(index=False))

    # Save Evaluation Table CSV
    eval_csv_path = os.path.join(OUTPUT_DIR, "model_performance_summary.csv")
    df_eval.to_csv(eval_csv_path, index=False)
    print(f"\n[+] Saved evaluation metrics table to: {eval_csv_path}")

    # ==============================================================================
    # 6. Evaluation Curves Visualization
    # ==============================================================================
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    for idx, (config_key, title_suffix) in enumerate([('with_pv', 'With PageValues'), ('no_pv', 'Without PageValues')]):
        ax_roc = axes[idx, 0]
        ax_pr = axes[idx, 1]
        X_t = configs[config_key]['X_test']

        for model_name, info in results[config_key].items():
            m = info['best_estimator']
            probs = m.predict_proba(X_t)[:, 1] if hasattr(m, 'predict_proba') else m.predict(X_t).astype(float)
            fpr, tpr, _ = roc_curve(y_test, probs)
            roc_val = roc_auc_score(y_test, probs)
            p_pts, r_pts, _ = precision_recall_curve(y_test, probs)
            pr_val = auc(r_pts, p_pts)

            ax_roc.plot(fpr, tpr, label=f"{model_name} (AUC = {roc_val:.3f})")
            ax_pr.plot(r_pts, p_pts, label=f"{model_name} (AUC = {pr_val:.3f})")

        ax_roc.plot([0, 1], [0, 1], 'k--', alpha=0.7)
        ax_roc.set_title(f'ROC Curves ({title_suffix})', fontsize=13, fontweight='bold')
        ax_roc.set_xlabel('False Positive Rate')
        ax_roc.set_ylabel('True Positive Rate')
        ax_roc.legend(loc='lower right')

        ax_pr.set_title(f'Precision-Recall Curves ({title_suffix})', fontsize=13, fontweight='bold')
        ax_pr.set_xlabel('Recall')
        ax_pr.set_ylabel('Precision')
        ax_pr.legend(loc='lower left')

    plt.tight_layout()
    curves_path = os.path.join(OUTPUT_DIR, "evaluation_curves.png")
    plt.savefig(curves_path, dpi=300)
    plt.close()
    print(f"[+] Saved ROC & PR curves to: {curves_path}")

    # ==============================================================================
    # 7. Feature Importance & Interpretation
    # ==============================================================================
    cat_enc_with = preprocessor_with.named_transformers_['cat'].named_steps['onehot']
    cat_cols_with = cat_enc_with.get_feature_names_out(categorical_cols).tolist()
    feat_with = numerical_cols + cat_cols_with

    cat_enc_no = preprocessor_no.named_transformers_['cat'].named_steps['onehot']
    cat_cols_no = cat_enc_no.get_feature_names_out(categorical_cols).tolist()
    feat_no = numerical_cols_no_pv + cat_cols_no

    gb_with = results['with_pv']['Gradient Boosting']['best_estimator']
    gb_no = results['no_pv']['Gradient Boosting']['best_estimator']

    df_imp_with = pd.DataFrame({'Feature': feat_with, 'Importance': gb_with.feature_importances_}).sort_values('Importance', ascending=False).head(10)
    df_imp_no = pd.DataFrame({'Feature': feat_no, 'Importance': gb_no.feature_importances_}).sort_values('Importance', ascending=False).head(10)

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    sns.barplot(x='Importance', y='Feature', hue='Feature', data=df_imp_with, ax=axes[0], palette='Blues_r', legend=False)
    axes[0].set_title('Top 10 Features (With PageValues - Leakage Present)', fontsize=13, fontweight='bold')

    sns.barplot(x='Importance', y='Feature', hue='Feature', data=df_imp_no, ax=axes[1], palette='Oranges_r', legend=False)
    axes[1].set_title('Top 10 Features (Without PageValues - Production Safe)', fontsize=13, fontweight='bold')

    plt.tight_layout()
    imp_path = os.path.join(OUTPUT_DIR, "feature_importances.png")
    plt.savefig(imp_path, dpi=300)
    plt.close()
    print(f"[+] Saved Feature Importance comparison to: {imp_path}")

    # ==============================================================================
    # 8. Real-Time Inference Simulation
    # ==============================================================================
    print("\n" + "=" * 70)
    print("STEP 6: REAL-TIME INFERENCE SIMULATION")
    print("=" * 70)
    mock_session = pd.DataFrame([{
        'Administrative': 8, 'Administrative_Duration': 150.5,
        'Informational': 2, 'Informational_Duration': 45.0,
        'ProductRelated': 35, 'ProductRelated_Duration': 1200.0,
        'BounceRates': 0.0, 'ExitRates': 0.01,
        'SpecialDay': 0.0, 'Month': 'Nov',
        'OperatingSystems': 2, 'Browser': 2, 'Region': 1,
        'TrafficType': 2, 'VisitorType': 'New_Visitor', 'Weekend': True
    }])

    prod_model = results['no_pv']['Gradient Boosting']['best_estimator']
    processed_mock = preprocessor_no.transform(mock_session)
    pred_prob = prod_model.predict_proba(processed_mock)[0, 1]
    pred_label = prod_model.predict(processed_mock)[0]

    print(f"Simulated Session Details:\n{mock_session.iloc[0].to_dict()}")
    print(f"Predicted Purchase Intent Probability: {pred_prob * 100:.2f}%")
    print(f"Predicted Conversion Status: {'Purchasing (Revenue=True)' if pred_label else 'Abandoning (Revenue=False)'}")
    if pred_prob > 0.40:
        print("Business Action Trigger: Highly engaged customer! Deploy dynamic 10% discount pop-up to close checkout.")
    else:
        print("Business Action Trigger: Low conversion engagement; standard browsing experience.")

    print("\n" + "=" * 70)
    print("ALL PROJECT MODULES COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
