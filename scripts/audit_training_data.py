
"""
Audit non destructif du dataset d'entraînement LifeInbox.

Lit data/raw/train.jsonl et produit un rapport CSV.
Ne modifie jamais le dataset source.
"""

import argparse
import csv
import json
import re
import unicodedata

from collections import defaultdict
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT = ROOT / "data" / "raw" / "train.jsonl"
DEFAULT_OUTPUT = ROOT / "reports" / "training_data_audit.csv"

VALID_CATEGORIES = {
    "calendar",
    "restaurant",
    "study",
    "todo",
    "note",
    "other",
}

REQUIRED_FIELDS = {
    "reference_date",
    "message",
    "category",
    "needs_clarification",
}

DATE_FIELDS = {
    "reference_date",
    "event_date",
    "deadline",
}

OPTIONAL_FIELDS = {
    "event_date",
    "event_time",
    "location",
    "deadline",
    "needs_clarification",
}


def normalize_message(message):
    """Normalisation destinée à repérer les doublons."""
    message = unicodedata.normalize("NFKC", message)
    message = message.casefold()
    message = re.sub(r"\s+", " ", message)
    return message.strip()


def valid_iso_date(value):
    """Vérifie une date au format YYYY-MM-DD."""
    if value is None:
        return True

    if not isinstance(value, str):
        return False

    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def add_issue(issues, line, severity, code, message, category=""):
    issues.append({
        "line": line,
        "severity": severity,
        "code": code,
        "message": message,
        "category": category,
    })


def audit_dataset(input_path):
    issues = []
    records = []

    if not input_path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {input_path}"
        )

    # Lecture uniquement : aucun mode d'écriture sur le dataset.
    with input_path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            if not raw_line.strip():
                add_issue(
                    issues, line_number, "error",
                    "EMPTY_LINE", "Ligne JSONL vide."
                )
                continue

            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                add_issue(
                    issues, line_number, "error",
                    "INVALID_JSON",
                    f"JSON invalide : {exc.msg}."
                )
                continue

            if not isinstance(record, dict):
                add_issue(
                    issues, line_number, "error",
                    "INVALID_RECORD",
                    "Chaque ligne doit contenir un objet JSON."
                )
                continue

            record["_line"] = line_number
            records.append(record)

            category = record.get("category", "")
            message = record.get("message", "")

            # 1. Structure
            missing = REQUIRED_FIELDS - record.keys()
            for field in sorted(missing):
                add_issue(
                    issues, line_number, "error",
                    "MISSING_FIELD",
                    f"Champ obligatoire absent : {field}.",
                    str(category),
                )

            for field in sorted(OPTIONAL_FIELDS):
                if field not in record:
                    add_issue(
                        issues, line_number, "warning",
                        "MISSING_OPTIONAL_FIELD",
                        f"Champ attendu absent : {field}.",
                        str(category),
                    )

            # 2. Message
            if not isinstance(message, str):
                add_issue(
                    issues, line_number, "error",
                    "INVALID_MESSAGE_TYPE",
                    "Le message doit être une chaîne de caractères.",
                    str(category),
                )
                continue

            if not message.strip():
                add_issue(
                    issues, line_number, "error",
                    "EMPTY_MESSAGE",
                    "Le message est vide.",
                    str(category),
                )
                continue

            if message != message.strip():
                add_issue(
                    issues, line_number, "warning",
                    "SURROUNDING_WHITESPACE",
                    "Espaces au début ou à la fin du message.",
                    str(category),
                )

            if len(message.strip()) < 4:
                add_issue(
                    issues, line_number, "warning",
                    "VERY_SHORT_MESSAGE",
                    "Message très court : vérifier son utilité.",
                    str(category),
                )

            # 3. Catégorie
            if category not in VALID_CATEGORIES:
                add_issue(
                    issues, line_number, "error",
                    "INVALID_CATEGORY",
                    f"Catégorie inconnue : {category!r}.",
                    str(category),
                )

            # 4. Besoin de clarification
            clarification = record.get("needs_clarification")
            if (
                "needs_clarification" in record
                and type(clarification) is not bool
            ):
                add_issue(
                    issues, line_number, "error",
                    "INVALID_CLARIFICATION",
                    "needs_clarification doit être true ou false.",
                    str(category),
                )

            # 5. Dates
            for field in DATE_FIELDS:
                if field not in record:
                    continue

                value = record[field]
                if value is not None and not valid_iso_date(value):
                    add_issue(
                        issues, line_number, "error",
                        "INVALID_DATE",
                        f"{field} doit être une date YYYY-MM-DD ou null.",
                        str(category),
                    )

            # 6. Heure
            event_time = record.get("event_time")
            if event_time is not None:
                if (
                    not isinstance(event_time, str)
                    or not re.fullmatch(
                        r"(?:[01]\d|2[0-3]):[0-5]\d",
                        event_time,
                    )
                ):
                    add_issue(
                        issues, line_number, "warning",
                        "UNUSUAL_TIME_FORMAT",
                        "event_time devrait être au format HH:MM ou null.",
                        str(category),
                    )

    # 7. Doublons exacts après normalisation
    by_message = defaultdict(list)

    for record in records:
        message = record.get("message")
        if isinstance(message, str) and message.strip():
            key = normalize_message(message)
            by_message[key].append(record)

    for normalized, group in by_message.items():
        if len(group) < 2:
            continue

        lines = [r["_line"] for r in group]
        categories = {
            r.get("category") for r in group
        }
        clarifications = {
            r.get("needs_clarification") for r in group
        }

        conflicting = (
            len(categories) > 1 or len(clarifications) > 1
        )

        for record in group:
            add_issue(
                issues,
                record["_line"],
                "error" if conflicting else "warning",
                "DUPLICATE_CONFLICT" if conflicting
                else "DUPLICATE_MESSAGE",
                (
                    f"Doublon aux lignes {lines} avec labels "
                    "contradictoires."
                    if conflicting
                    else f"Message dupliqué aux lignes {lines}."
                ),
                str(record.get("category", "")),
            )

    # 8. Messages quasi identiques avec labels différents
    # O(n²) : adapté aux petits datasets de quelques centaines
    # ou milliers d'exemples.
    valid_records = [
        r for r in records
        if isinstance(r.get("message"), str)
        and r["message"].strip()
    ]

    for i, first in enumerate(valid_records):
        text_a = normalize_message(first["message"])

        for second in valid_records[i + 1:]:
            text_b = normalize_message(second["message"])

            if text_a == text_b:
                continue

            # Évite de comparer les messages très différents.
            if abs(len(text_a) - len(text_b)) > 20:
                continue

            similarity = SequenceMatcher(
                None, text_a, text_b
            ).ratio()

            if similarity < 0.92:
                continue

            same_labels = (
                first.get("category") == second.get("category")
                and first.get("needs_clarification")
                == second.get("needs_clarification")
            )

            if not same_labels:
                for record, other in (
                    (first, second),
                    (second, first),
                ):
                    add_issue(
                        issues,
                        record["_line"],
                        "review",
                        "NEAR_DUPLICATE_LABEL_CONFLICT",
                        (
                            f"Message proche de la ligne "
                            f"{other['_line']} "
                            f"(similarité {similarity:.0%}), "
                            "mais labels différents."
                        ),
                        str(record.get("category", "")),
                    )

    return records, issues


def main():
    parser = argparse.ArgumentParser(
        description="Audit non destructif du dataset LifeInbox."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Chemin vers le fichier JSONL à auditer.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Chemin du rapport CSV.",
    )
    args = parser.parse_args()

    records, issues = audit_dataset(args.input)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "line", "severity", "code", "message", "category"
    ]

    with args.output.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)

    counts = defaultdict(int)
    for issue in issues:
        counts[issue["severity"]] += 1

    print(f"Dataset lu : {args.input}")
    print(f"Exemples valides en structure JSON : {len(records)}")
    print(f"Anomalies signalées : {len(issues)}")
    print(f"  Erreurs   : {counts['error']}")
    print(f"  À revoir  : {counts['review']}")
    print(f"  Alertes   : {counts['warning']}")
    print(f"Rapport : {args.output}")
    print("Le dataset source n'a pas été modifié.")


if __name__ == "__main__":
    main()
