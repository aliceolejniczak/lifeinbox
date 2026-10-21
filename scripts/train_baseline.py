
import csv
import json
from collections import Counter
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "train.jsonl"
MODEL_PATH = ROOT / "models" / "tfidf_classifier.joblib"
REPORT_DIR = ROOT / "reports"

VALID_CATEGORIES = {
    "calendar",
    "restaurant",
    "study",
    "todo",
    "note",
    "other",
}



def load_dataset(path):
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
                    f"Message invalide à la ligne {line_number}"
                )

            if category not in VALID_CATEGORIES:
                raise ValueError(
                    f"Catégorie invalide à la ligne {line_number}: "
                    f"{category!r}"
                )

            messages.append(message.strip())
            labels.append(category)
            source_ids.append(f"train_line_{line_number:04d}")

    if not messages:
        raise ValueError("Le dataset ne contient aucun exemple.")

    return messages, labels, source_ids



def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATA_PATH}"
        )

    messages, labels, source_ids = load_dataset(DATA_PATH)

    print(f"Nombre total d'exemples : {len(messages)}")
    print("\nRépartition des catégories :")
    for category, count in sorted(Counter(labels).items()):
        print(f"  {category:12s} : {count}")

    # On garde un ensemble de validation distinct.
    # Le test final indépendant ne doit pas être utilisé ici.
    X_train, X_val, y_train, y_val, ids_train, ids_val = train_test_split(
        messages,
        labels,
        source_ids,
        test_size=0.20,
        random_state=42,
        stratify=labels,
    )

    print(f"\nEntraînement : {len(X_train)} exemples")
    print(f"Validation   : {len(X_val)} exemples")

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
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

    print("\nEntraînement du modèle...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_val)

    accuracy = accuracy_score(y_val, predictions)
    macro_f1 = f1_score(
        y_val,
        predictions,
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_val,
        predictions,
        labels=sorted(VALID_CATEGORIES),
        output_dict=True,
        zero_division=0,
    )

    print("\n--- Résultats de validation ---")
    print(f"Accuracy : {accuracy:.3f}")
    print(f"F1 macro : {macro_f1:.3f}")
    print(
        classification_report(
            y_val,
            predictions,
            labels=sorted(VALID_CATEGORIES),
            zero_division=0,
        )
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Sauvegarde du pipeline complet : TF-IDF + classifieur.
    joblib.dump(model, MODEL_PATH)

    with (REPORT_DIR / "tfidf_metrics.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            {
                "dataset": str(DATA_PATH.relative_to(ROOT)),
                "n_examples": len(messages),
                "n_train": len(X_train),
                "n_validation": len(X_val),
                "random_state": 42,
                "accuracy": accuracy,
                "macro_f1": macro_f1,
                "classification_report": report,
            },
            file,
            indent=2,
            ensure_ascii=False,
        )

    
    with (REPORT_DIR / "tfidf_predictions.csv").open(
        "w", encoding="utf-8", newline=""
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

        for source_id, message, true_label, pred_label in zip(
            ids_val, X_val, y_val, predictions
        ):
            writer.writerow({
                "source_id": source_id,
                "message": message,
                "true_category": true_label,
                "predicted_category": pred_label,
                "correct": true_label == pred_label,
            })


    categories = sorted(VALID_CATEGORIES)
    matrix = confusion_matrix(
        y_val,
        predictions,
        labels=categories,
    )

    with (REPORT_DIR / "tfidf_confusion_matrix.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["true_category"] + categories)

        for category, row in zip(categories, matrix):
            writer.writerow([category] + row.tolist())

    print(f"\nModèle sauvegardé : {MODEL_PATH}")
    print(f"Métriques : {REPORT_DIR / 'tfidf_metrics.json'}")
    print(f"Prédictions : {REPORT_DIR / 'tfidf_predictions.csv'}")
    print("Le dataset source n'a pas été modifié.")


if __name__ == "__main__":
    main()
