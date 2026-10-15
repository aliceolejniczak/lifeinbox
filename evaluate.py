
from collections import defaultdict
from datetime import date, timedelta

from main import Category, classify_message


def next_weekday(weekday: int) -> date:
    """Retourne la prochaine occurrence du jour, aujourd'hui inclus."""
    today = date.today()
    days_ahead = (weekday - today.weekday()) % 7
    return today + timedelta(days=days_ahead)

def today():
    return date.today()

def tomorrow() -> date:
    return date.today() + timedelta(days=1)


def make_test(
    message,
    category,
    clarification,
    event_date=None,
    event_time=None,
    deadline=None,
):
    """Construit un test avec des champs attendus optionnels."""
    test = {
        "message": message,
        "category": category,
        "clarification": clarification,
    }

    if event_date is not None:
        test["event_date"] = event_date

    if event_time is not None:
        test["event_time"] = event_time

    if deadline is not None:
        test["deadline"] = deadline

    return test


TEST_CASES = [
    # --------------------------------------------------
    # 1. Les 10 tests initiaux : conserver la référence
    # --------------------------------------------------
    make_test(
        "J'ai un examen de deep learning vendredi à 14 h.",
        Category.CALENDAR, False, next_weekday(4), "14:00"
    ),
    make_test(
        "Je voudrais réserver un restaurant italien samedi soir près de chez moi.",
        Category.RESTAURANT, True, next_weekday(5)
    ),
    make_test(
        "Pense à revoir le chapitre 3 avant mon contrôle.",
        Category.TODO, True
    ),
    make_test(
        "Mon rendez-vous chez le dentiste est mardi à 10 h.",
        Category.CALENDAR, False, next_weekday(1), "10:00"
    ),
    # Test 5 : une tâche prévue pour ce soir.
    # On ne teste pas encore sa date : le schéma actuel
    # ne distingue pas une date d'exécution d'une échéance.
    make_test(
        "Achète du pain en rentrant ce soir.",
        Category.TODO,
        False,
    ),
        
    make_test(
        "Garde cette adresse : 12 rue Victor Hugo, Paris.",
        Category.NOTE, False
    ),
    make_test(
        "Je veux comprendre la descente de gradient.",
        Category.STUDY, False
    ),
    make_test(
        "Réserve une table samedi à 19 h pour 2 personnes "
        "au restaurant Le Petit Italien.",
        Category.RESTAURANT, False, next_weekday(5), "19:00"
    ),
    # Test 9 : tâche à terminer demain.
    make_test(
        "Rappelle-moi d'envoyer mon rapport demain.",
        Category.TODO,
        False,
        deadline=tomorrow(),
    ),
    make_test(
        "Il faut que je fasse quelque chose pour ce problème.",
        Category.OTHER, True
    ),

    # --------------------------------------------------
    # 2. Calendrier : tests 11 à 17
    # --------------------------------------------------
    make_test(
        "J'ai un entretien demain à 11 h.",
        Category.CALENDAR, False, tomorrow(), "11:00"
    ),
    make_test(
        "Réunion avec mon équipe lundi à 9h30.",
        Category.CALENDAR, False, next_weekday(0), "09:30"
    ),
    make_test(
        "Mon train pour Lyon part vendredi à 18h42.",
        Category.CALENDAR, False, next_weekday(4), "18:42"
    ),
    make_test(
        "Mon rendez-vous chez le médecin est la semaine prochaine.",
        Category.CALENDAR, True
    ),
    make_test(
        "Le mariage de Julie est le 12 décembre.",
        Category.CALENDAR, False, date(date.today().year, 12, 12)
    ),
    make_test(
        "Tu peux me rappeler que j'ai un rendez-vous jeudi ?",
        Category.CALENDAR, False, next_weekday(3)
    ),
    make_test(
        "Je crois que mon examen est mardi ou mercredi.",
        Category.CALENDAR, True
    ),

    # --------------------------------------------------
    # 3. Restaurants : tests 18 à 23
    # --------------------------------------------------
    make_test(
        "Réserve une table pour deux samedi à 20 h chez un italien.",
        Category.RESTAURANT, False, next_weekday(5), "20:00"
    ),
    make_test(
        "Je veux réserver chez Le Petit Italien demain à 19 h "
        "pour 3 personnes.",
        Category.RESTAURANT, False, tomorrow(), "19:00"
    ),
    make_test(
        "Trouve-moi un restaurant japonais sympa près de chez moi.",
        Category.RESTAURANT, True
    ),
    make_test(
        "On pourrait tester ce restaurant libanais dont Emma m'a parlé.",
        Category.RESTAURANT, False
    ),
    make_test(
        "Réserve pour 4 personnes vendredi soir au restaurant Le Jardin.",
        Category.RESTAURANT, True, next_weekday(4)
    ),
    make_test(
        "C'était quoi déjà le nom du restaurant que je voulais essayer ?",
        Category.RESTAURANT, True
    ),

    # --------------------------------------------------
    # 4. Études : tests 24 à 29
    # --------------------------------------------------
    make_test(
        "Explique-moi la différence entre la BCE et la cross entropy.",
        Category.STUDY, False
    ),
    make_test(
        "Je veux revoir les chaînes de Markov ce week-end.",
        Category.STUDY, False
    ),
    make_test(
        "Aide-moi à comprendre les LSTM, je n'ai rien compris au cours.",
        Category.STUDY, False
    ),
    make_test(
        "Il faut que je progresse en optimisation.",
        Category.STUDY, False
    ),
    make_test(
        "Fais-moi une fiche de révision sur les méthodes de Monte-Carlo.",
        Category.STUDY, False
    ),
    make_test(
    "J'ai un TP de machine learning à rendre vendredi.",
    Category.TODO,
    False,
    deadline=next_weekday(4),
    ),

    # --------------------------------------------------
    # 5. Tâches : tests 30 à 37
    # --------------------------------------------------
    make_test(
        "Pense à acheter des œufs et des tomates.",
        Category.TODO, False
    ),
    make_test(
        "Je dois envoyer mon CV à Mistral avant lundi.",
        Category.TODO,
        False,
        deadline=next_weekday(0),
    ),
    make_test(
        "Rappelle-moi d'appeler le dentiste demain matin.",
        Category.TODO, False, deadline=tomorrow()
    ),
    make_test(
        "Il faut que je fasse ma déclaration d'impôts.",
        Category.TODO, False
    ),
    make_test(
        "Acheter le cadeau d'anniversaire de maman.",
        Category.TODO, False
    ),
    make_test(
        "Je dois rendre ce dossier bientôt.",
        Category.TODO, True
    ),
    make_test(
        "Penser à réserver mes billets de train.",
        Category.TODO, False
    ),
    make_test(
        "Fais quelque chose pour m'aider à m'organiser.",
        Category.OTHER, True
    ),

    # --------------------------------------------------
    # 6. Notes : tests 38 à 43
    # --------------------------------------------------
    make_test(
        "Conserve cette adresse pour plus tard : "
        "8 avenue de la République, Lille.",
        Category.NOTE, False
    ),
    make_test(
        "Mon numéro de réservation est ABC123, note-le.",
        Category.NOTE, False
    ),
    make_test(
        "Le Wi-Fi de l'appartement s'appelle Maison_42.",
        Category.NOTE, False
    ),
    make_test(
        "Mon idée : créer une application qui trie automatiquement "
        "mes messages.",
        Category.NOTE, False
    ),
    make_test(
        "J'ai trouvé une bonne recette de curry de lentilles, "
        "garde cette idée.",
        Category.NOTE, False
    ),
    make_test(
        "Garde en mémoire le code de mon casier à la salle : 4821.",
        Category.NOTE, False
    ),

    # --------------------------------------------------
    # 7. Hors sujet / conversation : tests 44 à 50
    # --------------------------------------------------
    make_test("Ça va ?", Category.OTHER, False),
    make_test(
        "Tu vas au sport ce soir ?",
        Category.OTHER,
        False,
    ),
    make_test("J'aime bien ta veste !", Category.OTHER, False),
    make_test(
        "Il fait vraiment beau aujourd'hui.",
        Category.OTHER,
        False,
    ),

    make_test("Tu connais cette chanson ?", Category.OTHER, False),
    make_test("Haha, n'importe quoi 😂", Category.OTHER, False),
    make_test(
        "Je ne sais pas quoi faire de ce problème, ça me prend la tête.",
        Category.OTHER, True
    ),
]


def main():
    category_correct = 0
    clarification_correct = 0
    date_correct = date_checked = 0
    time_correct = time_checked = 0
    deadline_correct = deadline_checked = 0

    # Statistiques par catégorie
    by_category = defaultdict(lambda: {"total": 0, "correct": 0})
    errors = []

    for i, test in enumerate(TEST_CASES, start=1):
        result = classify_message(test["message"])

        category_ok = result.category == test["category"]
        clarification_ok = (
            result.needs_clarification == test["clarification"]
        )

        category_correct += category_ok
        clarification_correct += clarification_ok

        expected_category = test["category"].value
        predicted_category = result.category.value

        stats = by_category[expected_category]
        stats["total"] += 1
        stats["correct"] += category_ok

        print(f"\n--- Test {i}/ {len(TEST_CASES)} ---")
        print(f"Message : {test['message']}")
        print(f"Catégorie attendue : {expected_category}")
        print(f"Catégorie prédite  : {predicted_category}")
        print(f"Catégorie correcte : {category_ok}")
        print(f"Clarification attendue : {test['clarification']}")
        print(f"Clarification prédite  : {result.needs_clarification}")
        print(f"Clarification correcte : {clarification_ok}")

        if not category_ok or not clarification_ok:
            errors.append({
                "test": i,
                "message": test["message"],
                "expected_category": expected_category,
                "predicted_category": predicted_category,
                "expected_clarification": test["clarification"],
                "predicted_clarification": result.needs_clarification,
            })

        if "event_date" in test:
            date_checked += 1
            date_ok = result.event_date == test["event_date"]
            date_correct += date_ok
            print(f"Date attendue : {test['event_date']}")
            print(f"Date prédite  : {result.event_date}")
            print(f"Date correcte : {date_ok}")

        if "event_time" in test:
            time_checked += 1
            time_ok = result.event_time == test["event_time"]
            time_correct += time_ok
            print(f"Heure attendue : {test['event_time']}")
            print(f"Heure prédite  : {result.event_time}")
            print(f"Heure correcte : {time_ok}")

        if "deadline" in test:
            deadline_checked += 1
            deadline_ok = result.deadline == test["deadline"]
            deadline_correct += deadline_ok

            print(f"Échéance attendue : {test['deadline']}")
            print(f"Échéance prédite  : {result.deadline}")
            print(f"Échéance correcte : {deadline_ok}")

    n = len(TEST_CASES)

    print("\n" + "=" * 42)
    print("RÉSUMÉ GLOBAL")
    print("=" * 42)
    print(f"Nombre de tests : {n}")
    print(f"Classification : {category_correct}/{n} ({category_correct / n:.1%})")
    print(
        f"Clarification : {clarification_correct}/{n} "
        f"({clarification_correct / n:.1%})"
    )

    if date_checked:
        print(
            f"Dates : {date_correct}/{date_checked} "
            f"({date_correct / date_checked:.1%})"
        )

    if time_checked:
        print(
            f"Heures : {time_correct}/{time_checked} "
            f"({time_correct / time_checked:.1%})"
        )

    if deadline_checked:
        print(
            f"Échéances : {deadline_correct}/{deadline_checked} "
            f"({deadline_correct / deadline_checked:.1%})"
        )

    print("\n" + "=" * 42)
    print("CLASSIFICATION PAR CATÉGORIE")
    print("=" * 42)

    for category, stats in sorted(by_category.items()):
        total = stats["total"]
        correct = stats["correct"]
        print(f"{category:12s} : {correct}/{total} ({correct / total:.1%})")

    print("\n" + "=" * 42)
    print(f"ERREURS À ANALYSER ({len(errors)})")
    print("=" * 42)

    if not errors:
        print("Aucune erreur de catégorie ou de clarification.")
    else:
        for error in errors:
            print(f"\nTest {error['test']} : {error['message']}")
            if error["expected_category"] != error["predicted_category"]:
                print(
                    f"  Catégorie : attendue={error['expected_category']}, "
                    f"prédite={error['predicted_category']}"
                )
            if (
                error["expected_clarification"]
                != error["predicted_clarification"]
            ):
                print(
                    "  Clarification : "
                    f"attendue={error['expected_clarification']}, "
                    f"prédite={error['predicted_clarification']}"
                )


if __name__ == "__main__":
    main()
