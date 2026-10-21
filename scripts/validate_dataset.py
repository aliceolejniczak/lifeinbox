import json
import re
from datetime import date
from pathlib import Path

DATASET = Path("data/raw/train.jsonl")

EXPECTED_FIELDS = {
    "message",
    "reference_date",
    "category",
    "event_date",
    "event_time",
    "location",
    "deadline",
    "needs_clarification",
}

CATEGORIES = {
    "calendar", "restaurant", "study", "todo", "note", "other"
}


def valid_date(value, field, line_number, errors):
    if value is None:
        return
    if not isinstance(value, str):
        errors.append(f"Ligne {line_number}: {field} doit être une date ou null.")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"Ligne {line_number}: date invalide dans {field}: {value}")


def main():
    if not DATASET.exists():
        raise SystemExit(f"Fichier introuvable : {DATASET}")

    errors = []
    seen_messages = set()
    counts = {}
    total = 0

    with DATASET.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue

            total += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"Ligne {line_number}: JSON invalide ({exc})")
                continue

            if set(item) != EXPECTED_FIELDS:
                missing = EXPECTED_FIELDS - set(item)
                extra = set(item) - EXPECTED_FIELDS
                errors.append(
                    f"Ligne {line_number}: champs manquants={missing}, "
                    f"champs inattendus={extra}"
                )

            message = item.get("message")
            if not isinstance(message, str) or not message.strip():
                errors.append(f"Ligne {line_number}: message vide ou invalide.")
            else:
                normalized = " ".join(message.casefold().split())
                if normalized in seen_messages:
                    errors.append(f"Ligne {line_number}: message dupliqué.")
                seen_messages.add(normalized)

            category = item.get("category")
            if category not in CATEGORIES:
                errors.append(f"Ligne {line_number}: catégorie invalide: {category}")
            else:
                counts[category] = counts.get(category, 0) + 1

            valid_date(item.get("reference_date"), "reference_date",
                       line_number, errors)
            valid_date(item.get("event_date"), "event_date",
                       line_number, errors)
            valid_date(item.get("deadline"), "deadline",
                       line_number, errors)

            event_time = item.get("event_time")
            if event_time is not None and (
                not isinstance(event_time, str)
                or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", event_time)
            ):
                errors.append(f"Ligne {line_number}: heure invalide: {event_time}")

            location = item.get("location")
            if location is not None and not isinstance(location, str):
                errors.append(f"Ligne {line_number}: location doit être une chaîne ou null.")

            if not isinstance(item.get("needs_clarification"), bool):
                errors.append(
                    f"Ligne {line_number}: needs_clarification doit être un booléen."
                )

    print(f"Nombre d'exemples : {total}")
    print(f"Date du jour utilisée lors de la génération : vérifie reference_date dans le fichier.")
    print("Répartition par catégorie :", counts)

    if errors:
        print(f"\n{len(errors)} erreur(s) détectée(s) :")
        for error in errors:
            print("-", error)
        raise SystemExit(1)

    print("\nValidation technique réussie.")


if __name__ == "__main__":
    main()
