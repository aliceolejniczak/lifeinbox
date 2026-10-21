
import ast
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"

PREDICTIONS_PATH = REPORT_DIR / "tfidf_tuned_predictions.csv"
CV_RESULTS_PATH = REPORT_DIR / "tfidf_tuning_cv_results.csv"

ERRORS_PATH = REPORT_DIR / "tfidf_tuning_errors.csv"
TOP_CONFIGS_PATH = REPORT_DIR / "tfidf_tuning_top_configs.csv"
COMPARISON_PATH = REPORT_DIR / "tfidf_tuning_baseline_comparison.csv"


def parse_params(value):
    """Convert the saved parameter dictionary back into a Python dict."""
    return ast.literal_eval(value) if isinstance(value, str) else value


def main():
    # 1. Analyse des erreurs de validation
    predictions = pd.read_csv(PREDICTIONS_PATH)

    errors = predictions.loc[
        predictions["correct"].astype(str).str.lower().isin(["false", "0"])
    ].copy()

    errors.to_csv(ERRORS_PATH, index=False)

    print(f"Validation examples: {len(predictions)}")
    print(f"Incorrect predictions: {len(errors)}")
    print("\nErrors by true category:")
    print(errors["true_category"].value_counts().to_string())

    print("\nErrors by true/predicted category:")
    if errors.empty:
        print("No errors.")
    else:
        print(
            errors.groupby(
                ["true_category", "predicted_category"]
            ).size().to_string()
        )

    print("\nDetailed errors:")
    if errors.empty:
        print("No errors to display.")
    else:
        print(
            errors[
                [
                    "source_id",
                    "message",
                    "true_category",
                    "predicted_category",
                ]
            ].to_string(index=False)
        )

    # 2. Classement des configurations testées
    results = pd.read_csv(CV_RESULTS_PATH)
    results = results.sort_values(
        ["rank_test_score", "mean_test_score"],
        ascending=[True, False],
    ).copy()

    results["params_dict"] = results["params"].apply(parse_params)

    display_columns = [
        "rank_test_score",
        "mean_test_score",
        "std_test_score",
        "mean_train_score",
        "params",
    ]

    top_configs = results[display_columns].head(10)
    top_configs.to_csv(TOP_CONFIGS_PATH, index=False)

    print("\nTop 10 configurations:")
    print(top_configs.to_string(index=False))

    # 3. Comparaison CV entre la baseline initiale et le meilleur modèle
    def is_baseline(params):
        return (
            params.get("tfidf__ngram_range") == (1, 2)
            and params.get("tfidf__min_df") == 1
            and params.get("classifier__C") == 1
            and params.get("classifier__class_weight") is None
        )

    baseline_rows = results[
        results["params_dict"].apply(is_baseline)
    ]

    best_row = results.iloc[0]

    comparison = [{
        "model": "tfidf_initial_hyperparameters",
        "cv_macro_f1_mean": (
            float(baseline_rows.iloc[0]["mean_test_score"])
            if not baseline_rows.empty
            else None
        ),
        "cv_macro_f1_std": (
            float(baseline_rows.iloc[0]["std_test_score"])
            if not baseline_rows.empty
            else None
        ),
        "params": (
            str(baseline_rows.iloc[0]["params"])
            if not baseline_rows.empty
            else "Baseline configuration not found"
        ),
    }, {
        "model": "tfidf_best_configuration",
        "cv_macro_f1_mean": float(best_row["mean_test_score"]),
        "cv_macro_f1_std": float(best_row["std_test_score"]),
        "params": str(best_row["params"]),
    }]

    pd.DataFrame(comparison).to_csv(COMPARISON_PATH, index=False)

    print("\nCross-validation comparison:")
    print(pd.DataFrame(comparison).to_string(index=False))

    print("\nSaved analysis files:")
    for path in [ERRORS_PATH, TOP_CONFIGS_PATH, COMPARISON_PATH]:
        print(f"- {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
