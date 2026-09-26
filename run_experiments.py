import os, json, joblib, time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score,
    precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.inspection import permutation_importance
import builtins

def print(*args, **kwargs):
    kwargs['flush'] = True
    builtins.print(*args, **kwargs)

from preprocessing import load_data, preprocess, split_data, get_feature_names

# Configuration matching train_domain_model.py
RANDOM_STATE = 42
N_ESTIMATORS = 200
MAX_DEPTH = 30

def run_experiment(X_train, X_test, y_train, y_test, X_full, y_full, feature_names, class_names, experiment_name):
    print(f"\n{'='*80}\nEXPERIMENT {experiment_name}\n{'='*80}")
    print(f"Features ({len(feature_names)}): {feature_names}")
    
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # Metrics
    test_acc = accuracy_score(y_test, y_pred)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec_macro = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
    f1_wtd = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    
    # Top-K
    top3_preds = np.argsort(y_proba, axis=1)[:, ::-1][:, :3]
    top3_acc = sum(1 for i in range(len(y_test)) if y_test[i] in top3_preds[i]) / len(y_test)
    top5_preds = np.argsort(y_proba, axis=1)[:, ::-1][:, :5]
    top5_acc = sum(1 for i in range(len(y_test)) if y_test[i] in top5_preds[i]) / len(y_test)
    
    # CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(model, X_full, y_full, cv=skf, scoring="accuracy", n_jobs=1)
    
    # Per-class F1
    per_class_f1 = f1_score(y_test, y_pred, average=None, zero_division=0)
    
    results = {
        'Test Accuracy': test_acc,
        'Balanced Accuracy': balanced_acc,
        'Macro Precision': prec_macro,
        'Macro Recall': rec_macro,
        'Macro F1': f1_macro,
        'Weighted F1': f1_wtd,
        'Top-3 Accuracy': top3_acc,
        'Top-5 Accuracy': top5_acc,
        'CV Mean': cv_scores.mean(),
        'CV Std': cv_scores.std(),
        'CV Scores': cv_scores.tolist(),
        'Per-Class F1': {class_names[i]: per_class_f1[i] for i in range(len(class_names))}
    }
    
    for k, v in results.items():
        if isinstance(v, float):
            print(f"{k:20s}: {v:.4f}")
        elif k == 'CV Scores':
            pass
        elif k == 'Per-Class F1':
            pass
    print(f"5-fold CV mean ± std : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    print("\nPer-Class F1 Scores:")
    for cls, val in results['Per-Class F1'].items():
        print(f"  {cls:40s}: {val:.4f}")
        
    return model, results

def main():
    df = load_data()
    X, y, encoders = preprocess(df, fit_encoders=True)
    all_feature_names = get_feature_names()
    class_names = encoders["Career_Domain"].classes_
    X_train, X_test, y_train, y_test = split_data(X, y, random_state=RANDOM_STATE)
    
    def get_indices(features_to_keep):
        return [all_feature_names.index(f) for f in features_to_keep if f in all_feature_names]

    # Feature lists
    assessment_traits = ["Logical_Score", "Analytical_Score", "Technical_Interest", "Business_Interest", "Creativity_Score", "Communication_Score", "Leadership_Score", "Research_Interest"]
    academic_pct = ["Class10_Percentage", "Class12_Percentage"]
    subject_marks = ["Physics_Marks", "Chemistry_Marks", "Mathematics_Marks", "Biology_Marks", "Computer_Science_Marks", "Statistics_Marks", "Accountancy_Marks", "Economics_Marks", "Business_Studies_Marks", "English_Marks"]
    categorical_bg = ["Class12_Stream", "Subject_Combination"]
    
    # Exp A: Current 22-feature model
    model_A, res_A = run_experiment(X_train, X_test, y_train, y_test, X, y, all_feature_names, class_names, "A (22 features)")
    
    # Feature Group Analysis on A
    print("\n" + "="*80)
    print("FEATURE GROUP ANALYSIS (Impurity-based)")
    print("="*80)
    importances = model_A.feature_importances_
    
    def group_importance(group_features):
        return sum(importances[all_feature_names.index(f)] for f in group_features if f in all_feature_names)
        
    print(f"1. Assessment traits:     {group_importance(assessment_traits):.4f}")
    print(f"2. Academic percentages:  {group_importance(academic_pct):.4f}")
    print(f"3. Subject marks:         {group_importance(subject_marks):.4f}")
    print(f"4. Categorical/background:{group_importance(categorical_bg):.4f}")
    
    print("\n" + "="*80)
    print("PERMUTATION IMPORTANCE (Test Set)")
    print("="*80)
    perm_result = permutation_importance(model_A, X_test, y_test, n_repeats=5, random_state=RANDOM_STATE, n_jobs=1)
    perm_sorted_idx = perm_result.importances_mean.argsort()[::-1]
    for i in perm_sorted_idx:
        print(f"{all_feature_names[i]:30s} : {perm_result.importances_mean[i]:.4f} ± {perm_result.importances_std[i]:.4f}")
    
    # Exp B: Remove Class12_Stream
    feats_B = [f for f in all_feature_names if f != "Class12_Stream"]
    idx_B = get_indices(feats_B)
    run_experiment(X_train[:, idx_B], X_test[:, idx_B], y_train, y_test, X[:, idx_B], y, feats_B, class_names, "B (No Class12_Stream)")

    # Exp C: Remove Business_Interest
    feats_C = [f for f in all_feature_names if f != "Business_Interest"]
    idx_C = get_indices(feats_C)
    run_experiment(X_train[:, idx_C], X_test[:, idx_C], y_train, y_test, X[:, idx_C], y, feats_C, class_names, "C (No Business_Interest)")

    # Exp D: Remove all 8 assessment traits
    feats_D = [f for f in all_feature_names if f not in assessment_traits]
    idx_D = get_indices(feats_D)
    run_experiment(X_train[:, idx_D], X_test[:, idx_D], y_train, y_test, X[:, idx_D], y, feats_D, class_names, "D (No Assessment Traits)")
    
    # Exp E: Academic/background features only
    feats_E = categorical_bg + academic_pct + subject_marks
    idx_E = get_indices(feats_E)
    run_experiment(X_train[:, idx_E], X_test[:, idx_E], y_train, y_test, X[:, idx_E], y, feats_E, class_names, "E (Academic Only)")
    
    # Exp F: Assessment traits only
    feats_F = assessment_traits
    idx_F = get_indices(feats_F)
    run_experiment(X_train[:, idx_F], X_test[:, idx_F], y_train, y_test, X[:, idx_F], y, feats_F, class_names, "F (Assessment Traits Only)")

if __name__ == '__main__':
    main()
