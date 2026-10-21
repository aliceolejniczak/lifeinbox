
import csv
import json
from collections import Counter
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "train.jsonl"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"

MODEL_PATH = MODEL_DIR / "tfidf_classifier_tuned.joblib"
METRICS_PATH = REPORT_DIR / "tfidf_tuning_results.json"
CV_RESULTS_PATH = REPORT_DIR / "tfidf_tuning_cv_results.csv"
PREDICTIONS_PATH = REPORT_DIR / "tfidf_tuned_predictions.csv"
CONFUSION_PATH = REPORT_DIR / "tfidf_tuned_confusion_matrix.csv"

VALID_CATEGORIES = {
    "calendar",
    "restaurant",
    "study",
    "todo",
    "note",
    "other",
}


def load_dataset(path):
    """Load messages, labels and stable source IDs from JSONL."""
    messages = []
    labels = []
    source_ids = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            message = record.get("message")
            category = record.get("category")

            if not isinstance(message, str) or not message.strip():
                raise ValueError(
                    f"Message missing or invalid at line {line_number}"
                )

            if category not in VALID_CATEGORIES:
                raise ValueError(
                    f"Invalid category at line {line_number}: {category}"
                )

            messages.append(message)
            labels.append(category)
            source_ids.append(f"train_line_{line_number:04d}")

    if not messages:
        raise ValueError(f"No examples found in {path}")

    if len(set(source_ids)) != len(source_ids):
        raise ValueError("Duplicate source IDs detected.")

    return messages, labels, source_ids


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    messages, labels, source_ids = load_dataset(DATA_PATH)

    print(f"Dataset: {len(messages)} examples")
    print(f"Category distribution: {dict(Counter(labels))}")

    # Reproduce the split used by train_baseline.py.
    (
        X_train,
        X_val,
        y_train,
        y_val,
        ids_train,
        ids_val,
    ) = train_test_split(
        messages,
        labels,
        source_ids,
        test_size=0.20,
        random_state=42,
        stratify=labels,
    )

    print(f"\nTraining examples: {len(X_train)}")
    print(f"Validation examples: {len(X_val)}")

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                random_state=42,
            ),
        ),
    ])

    # 3 x 2 x 3 x 2 = 36 configurations.
    param_grid = {
        "tfidf__ngram_range": [
            (1, 1),
            (1, 2),
            (1, 3),
        ],
        "tfidf__min_df": [1, 2],
        "classifier__C": [0.1, 1, 10],
        "classifier__class_weight": [None, "balanced"],
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=True,
        verbose=1,
        error_score="raise",
    )

    print("\nStarting hyperparameter search...")
    print("36 configurations x 5 folds = 180 fits")

    search.fit(X_train, y_train)

    print("\nBest parameters:")
    print(search.best_params_)
    print(f"Best cross-validation macro F1: {search.best_score_:.3f}")

    # Save the complete CV search history, not just the winning result.
    cv_results = pd.DataFrame(search.cv_results_)
    cv_results = cv_results.sort_values(
        by=["rank_test_score", "mean_test_score"],
        ascending=[True, False],
    )

    cv_results.to_csv(CV_RESULTS_PATH, index=False)

    # Evaluate the selected model on the existing holdout set.
    best_model = search.best_estimator_
    predictions = best_model.predict(X_val)

    val_accuracy = accuracy_score(y_val, predictions)
    val_macro_f1 = f1_score(
        y_val,
        predictions,
        average="macro",
        zero_division=0,
    )

    print("\nHoldout validation results:")
    print(f"Accuracy: {val_accuracy:.3f}")
    print(f"Macro F1: {val_macro_f1:.3f}")
    print(
        classification_report(
            y_val,
            predictions,
            labels=sorted(VALID_CATEGORIES),
            zero_division=0,
        )
    )

    # Preserve the selected model separately from the original baseline.
    joblib.dump(best_model, MODEL_PATH)

    # Save every validation prediction with its original source ID.
    with PREDICTIONS_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_id",
                "message",
                "true_category",
                "predicted_category",
                "correct",
            ],
        )
        writer.writeheader()

        for source_id, message, true_label, pred in zip(
            ids_val, X_val, y_val, predictions
        ):
            writer.writerow({
                "source_id": source_id,
                "message": message,
                "true_category": true_label,
                "predicted_category": pred,
                "correct": true_label == pred,
            })

    # Save the confusion matrix with named rows and columns.
    categories = sorted(VALID_CATEGORIES)
    matrix = confusion_matrix(
        y_val,
        predictions,
        labels=categories,
    )

    with CONFUSION_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["true_category", *categories])

        for category, row in zip(categories, matrix):
            writer.writerow([category, *row.tolist()])

    best_params = {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in search.best_params_.items()
    }

    metrics = {
        "experiment": "tfidf_hyperparameter_tuning",
        "dataset_path": str(DATA_PATH.relative_to(ROOT)),
        "dataset_size": len(messages),
        "training_size": len(X_train),
        "validation_size": len(X_val),
        "split": {
            "test_size": 0.20,
            "random_state": 42,
            "stratified": True,
        },
        "cross_validation": {
            "method": "StratifiedKFold",
            "n_splits": 5,
            "shuffle": True,
            "random_state": 42,
            "scoring": "f1_macro",
            "configurations_tested": len(search.cv_results_),
            "total_fits": len(search.cv_results_) * cv.get_n_splits(),
            "best_macro_f1": float(search.best_score_),
        },
        "best_params": best_params,
        "validation": {
            "accuracy": float(val_accuracy),
            "macro_f1": float(val_macro_f1),
            "classification_report": classification_report(
                y_val,
                predictions,
                labels=categories,
                output_dict=True,
                zero_division=0,
            ),
        },
        "artifacts": {
            "model": str(MODEL_PATH.relative_to(ROOT)),
            "cv_results": str(CV_RESULTS_PATH.relative_to(ROOT)),
            "predictions": str(PREDICTIONS_PATH.relative_to(ROOT)),
            "confusion_matrix": str(CONFUSION_PATH.relative_to(ROOT)),
        },
        "note": (
            "The holdout validation set has already been inspected during "
            "baseline error analysis. Use the independent test benchmark "
            "for the final comparison, not for hyperparameter selection."
        ),
    }

    with METRICS_PATH.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, ensure_ascii=False)

    print("\nSaved artifacts:")
    for path in [
        MODEL_PATH,
        METRICS_PATH,
        CV_RESULTS_PATH,
        PREDICTIONS_PATH,
        CONFUSION_PATH,
    ]:
        print(f"- {path.relative_to(ROOT)}")

    print("\nTuning complete.")


if __name__ == "__main__":
    main()
