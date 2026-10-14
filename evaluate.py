
from datetime import date, timedelta

from main import Category, classify_message


def next_weekday(weekday: int) -> date:
    """Return the next occurrence of a weekday, including today."""
    today = date.today()
    days_ahead = (weekday - today.weekday()) % 7
    return today + timedelta(days=days_ahead)


TEST_CASES = [
    {
        "message": "J'ai un examen de deep learning vendredi à 14 h.",
        "category": Category.CALENDAR,
        "clarification": False,
        "event_date": next_weekday(4),
        "event_time": "14:00",
    },
    {
        "message": (
            "Je voudrais réserver un restaurant italien "
            "samedi soir près de chez moi."
        ),
        "category": Category.RESTAURANT,
        "clarification": True,
    },
    {
        "message": "Pense à revoir le chapitre 3 avant mon contrôle.",
        "category": Category.TODO,
        "clarification": True,
    },
    {
        "message": "Mon rendez-vous chez le dentiste est mardi à 10 h.",
        "category": Category.CALENDAR,
        "clarification": False,
        "event_date": next_weekday(1),
        "event_time": "10:00",
    },
    {
        "message": "Achète du pain en rentrant ce soir.",
        "category": Category.TODO,
        "clarification": False,
    },
    {
        "message": "Garde cette adresse : 12 rue Victor Hugo, Paris.",
        "category": Category.NOTE,
        "clarification": False,
    },
    {
        "message": "Je veux comprendre la descente de gradient.",
        "category": Category.STUDY,
        "clarification": False,
    },
    {
        "message": (
            "Réserve une table samedi à 19 h "
            "pour 2 personnes au restaurant Le Petit Italien."
        ),
        "category": Category.RESTAURANT,
        "clarification": False,
        "event_date": next_weekday(5),
        "event_time": "19:00",
    },
    {
        "message": "Rappelle-moi d'envoyer mon rapport demain.",
        "category": Category.TODO,
        "clarification": False,
    },
    {
        "message": "Il faut que je fasse quelque chose pour ce problème.",
        "category": Category.OTHER,
        "clarification": True,
    },
]


def main():
    category_correct = 0
    clarification_correct = 0
    date_checked = 0
    date_correct = 0
    time_checked = 0
    time_correct = 0

    for i, test in enumerate(TEST_CASES, start=1):
        result = classify_message(test["message"])

        category_ok = result.category == test["category"]
        clarification_ok = (
            result.needs_clarification == test["clarification"]
        )

        category_correct += category_ok
        clarification_correct += clarification_ok

        print(f"\n--- Test {i} ---")
        print(f"Message : {test['message']}")
        print(f"Catégorie attendue : {test['category'].value}")
        print(f"Catégorie prédite :  {result.category.value}")
        print(f"Catégorie correcte : {category_ok}")
        print(f"Clarification attendue : {test['clarification']}")
        print(f"Clarification prédite :  {result.needs_clarification}")
        print(f"Clarification correcte : {clarification_ok}")

        if "event_date" in test:
            date_checked += 1
            date_ok = result.event_date == test["event_date"]
            date_correct += date_ok
            print(f"Date attendue : {test['event_date']}")
            print(f"Date prédite :  {result.event_date}")
            print(f"Date correcte : {date_ok}")

        if "event_time" in test:
            time_checked += 1
            time_ok = result.event_time == test["event_time"]
            time_correct += time_ok
            print(f"Heure attendue : {test['event_time']}")
            print(f"Heure prédite :  {result.event_time}")
            print(f"Heure correcte : {time_ok}")

    n = len(TEST_CASES)

    print("\n========== RÉSUMÉ ==========")
    print(f"Classification : {category_correct}/{n} ({category_correct / n:.0%})")
    print(
        f"Clarification : {clarification_correct}/{n} "
        f"({clarification_correct / n:.0%})"
    )

    if date_checked:
        print(
            f"Dates : {date_correct}/{date_checked} "
            f"({date_correct / date_checked:.0%})"
        )

    if time_checked:
        print(
            f"Heures : {time_correct}/{time_checked} "
            f"({time_correct / time_checked:.0%})"
        )


if __name__ == "__main__":
    main()
