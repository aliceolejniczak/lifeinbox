
from collections import Counter
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
)

from evaluate_test import TEST_CASES
from main import classify_message, Category


OUTPUT_DIR = Path("audit_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Ordre fixe pour que la matrice soit toujours comparable
LABELS = [category.value for category in Category]


def normalize_message(message: str) -> str:
    """Normalise un message pour repérer les doublons."""
    message = message.lower().strip()
    message = re.sub(r"\s+", " ", message)
    return message


def category_value(category) -> str:
    """Convertit un enum Category en chaîne."""
    return category.value if hasattr(category, "value") else str(category)


def main():
    rows = []

    print(f"Analyse de {len(TEST_CASES)} exemples...")

    for i, test in enumerate(TEST_CASES, start=1):
        message = test["message"]

        # Inférence du modèle
        prediction = classify_message(message)

        expected_category = category_value(test["category"])
        predicted_category = category_value(prediction.category)

        expected_clarification = bool(test["clarification"])
        predicted_clarification = bool(
            prediction.needs_clarification
        )

        rows.append({
            "test_id": i,
            "message": message,
            "expected_category": expected_category,
            "predicted_category": predicted_category,
            "category_error": (
                expected_category != predicted_category
            ),
            "expected_clarification": expected_clarification,
            "predicted_clarification": predicted_clarification,
            "clarification_error": (
                expected_clarification != predicted_clarification
            ),
            "event_date_expected": str(test.get("event_date", "")),
            "event_date_predicted": str(
                prediction.event_date or ""
            ),
            "event_time_expected": str(test.get("event_time", "")),
            "event_time_predicted": str(
                prediction.event_time or ""
            ),
            "deadline_expected": str(test.get("deadline", "")),
            "deadline_predicted": str(
                prediction.deadline or ""
            ),
        })

        if i % 10 == 0:
            print(f"{i}/{len(TEST_CASES)} exemples traités")

    df = pd.DataFrame(rows)

    # --------------------------------------------------
    # 1. EXPORT COMPLET DES PRÉDICTIONS
    # --------------------------------------------------
    df.to_csv(
        OUTPUT_DIR / "predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------
    # 2. MATRICE DE CONFUSION DES CATÉGORIES
    # Lignes = catégories attendues
    # Colonnes = catégories prédites
    # --------------------------------------------------
    y_true = df["expected_category"]
    y_pred = df["predicted_category"]

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=LABELS,
        columns=LABELS,
    )

    matrix_df.index.name = "Catégorie attendue"
    matrix_df.columns.name = "Catégorie prédite"

    matrix_df.to_csv(
        OUTPUT_DIR / "confusion_matrix.csv",
        encoding="utf-8-sig",
    )

    fig, ax = plt.subplots(figsize=(9, 7))

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=LABELS,
    )

    display.plot(
        ax=ax,
        xticks_rotation=45,
        values_format="d",
        colorbar=False,
    )

    ax.set_title("Matrice de confusion — LifeInbox")
    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "confusion_matrix.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)

    # --------------------------------------------------
    # 3. RAPPORT PAR CATÉGORIE
    # --------------------------------------------------
    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )

    report_df = pd.DataFrame(report).T
    report_df.to_csv(
        OUTPUT_DIR / "classification_report.csv",
        encoding="utf-8-sig",
    )

    # --------------------------------------------------
    # 4. MATRICE DE CONFUSION DE LA CLARIFICATION
    # --------------------------------------------------
    clarification_labels = [False, True]

    clarification_matrix = confusion_matrix(
        df["expected_clarification"],
        df["predicted_clarification"],
        labels=clarification_labels,
    )

    clarification_df = pd.DataFrame(
        clarification_matrix,
        index=["Attendue : non", "Attendue : oui"],
        columns=["Prédite : non", "Prédite : oui"],
    )

    clarification_df.to_csv(
        OUTPUT_DIR / "clarification_matrix.csv",
        encoding="utf-8-sig",
    )

    # --------------------------------------------------
    # 5. AUDIT DES LABELS ET DOUBLONS
    # --------------------------------------------------
    df["normalized_message"] = df["message"].apply(
        normalize_message
    )

    counts = Counter(df["normalized_message"])

    df["duplicate_message"] = df["normalized_message"].map(
        lambda message: counts[message] > 1
    )

    # Tous les exemples sont exportés pour permettre
    # une révision humaine des annotations.
    df["label_review"] = ""

    # Une erreur de prédiction est un signal à examiner,
    # mais ne prouve pas que le label attendu est faux.
    df.loc[
        df["category_error"],
        "label_review"
    ] = "Vérifier le label ou la prédiction"

    df.loc[
        df["duplicate_message"],
        "label_review"
    ] += " | Vérifier le doublon"

    # Fichier complet pour audit manuel
    df.drop(
        columns=["normalized_message"]
    ).to_csv(
        OUTPUT_DIR / "label_audit.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Fichier plus court : erreurs et doublons uniquement
    review_df = df[
        df["category_error"]
        | df["clarification_error"]
        | df["duplicate_message"]
    ].copy()

    review_df.drop(
        columns=["normalized_message"]
    ).to_csv(
        OUTPUT_DIR / "items_to_review.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------
    # 6. RÉSUMÉ DANS LE TERMINAL
    # --------------------------------------------------
    category_accuracy = (
        df["expected_category"] == df["predicted_category"]
    ).mean()

    clarification_accuracy = (
        df["expected_clarification"]
        == df["predicted_clarification"]
    ).mean()

    print("\n========== RÉSULTATS DE L'AUDIT ==========")
    print(f"Nombre de tests : {len(df)}")
    print(f"Classification correcte : {category_accuracy:.1%}")
    print(f"Clarification correcte : {clarification_accuracy:.1%}")
    print(f"Erreurs de catégorie : {df['category_error'].sum()}")
    print(
        "Erreurs de clarification : "
        f"{df['clarification_error'].sum()}"
    )
    print(
        "Messages dupliqués : "
        f"{df.loc[df['duplicate_message'], 'normalized_message'].nunique()}"
    )

    print("\nFichiers générés dans :", OUTPUT_DIR.resolve())
    print("- predictions.csv")
    print("- confusion_matrix.csv")
    print("- confusion_matrix.png")
    print("- classification_report.csv")
    print("- clarification_matrix.csv")
    print("- label_audit.csv")
    print("- items_to_review.csv")


if __name__ == "__main__":
    main()
