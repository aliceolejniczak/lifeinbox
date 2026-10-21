
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
    # ==================================================
    # CALENDAR — 10 tests
    # ==================================================
    make_test(
        "La soutenance de mon projet aura lieu mercredi à 15h.",
        Category.CALENDAR, False, next_weekday(2), "15:00"
    ),
    make_test(
        "J'ai un rendez-vous chez l'ophtalmo demain à 8h45.",
        Category.CALENDAR, False, tomorrow(), "08:45"
    ),
    make_test(
        "Le vol pour Rome décolle le 22 octobre à 7h10.",
        Category.CALENDAR, False, date(date.today().year, 10, 22), "07:10"
    ),
    make_test(
        "Mon prochain entretien est prévu le 3 novembre.",
        Category.CALENDAR, False, date(date.today().year, 11, 3)
    ),
    make_test(
        "Le cours de statistiques commence jeudi à 13h30.",
        Category.CALENDAR, False, next_weekday(3), "13:30"
    ),
    make_test(
        "Je dois être à la gare à 6h demain.",
        Category.CALENDAR, False, tomorrow(), "06:00"
    ),
    make_test(
        "Le rendez-vous avec le notaire est lundi ou mardi.",
        Category.CALENDAR, True
    ),
    make_test(
        "La conférence aura lieu le 18 décembre à 17h.",
        Category.CALENDAR, False, date(date.today().year, 12, 18), "17:00"
    ),
    make_test(
        "J'ai un contrôle de probabilités la semaine prochaine.",
        Category.CALENDAR, True
    ),
    make_test(
        "Le dîner d'anniversaire de Paul est samedi à 20h.",
        Category.CALENDAR, False, next_weekday(5), "20:00"
    ),

    # ==================================================
    # RESTAURANT — 10 tests
    # ==================================================
    make_test(
        "Quels restaurants végétariens me conseilles-tu à Bordeaux ?",
        Category.RESTAURANT, False
    ),
    make_test(
        "J'aimerais tester un restaurant coréen ce week-end.",
        Category.RESTAURANT, False
    ),
    make_test(
        "Peux-tu réserver une table chez La Piazza demain à 20h pour 5 ?",
        Category.RESTAURANT, False, tomorrow(), "20:00"
    ),
    make_test(
        "Trouve une bonne adresse pour manger des ramen.",
        Category.RESTAURANT, False
    ),
    make_test(
        "Il faudrait réserver une table pour six vendredi soir.",
        Category.RESTAURANT, True, next_weekday(4)
    ),
    make_test(
        "Quel était le café que Léa m'avait recommandé la semaine dernière ?",
        Category.RESTAURANT, True
    ),
    make_test(
        "J'ai envie de retourner au restaurant où nous sommes allés à Lyon.",
        Category.RESTAURANT, True
    ),
    make_test(
        "Réserve pour deux personnes demain soir chez Le Bistrot Vert.",
        Category.RESTAURANT, True, tomorrow()
    ),
    make_test(
        "Tu connais un bon restaurant de poissons à Marseille ?",
        Category.RESTAURANT, False
    ),
    make_test(
        "Garde en tête que je voudrais essayer le nouveau restaurant grec.",
        Category.RESTAURANT, False
    ),

    # ==================================================
    # STUDY — 10 tests
    # ==================================================
    make_test(
        "Peux-tu m'expliquer intuitivement le théorème de Bayes ?",
        Category.STUDY, False
    ),
    make_test(
        "Quelle est la différence entre un RNN et un Transformer ?",
        Category.STUDY, False
    ),
    make_test(
        "Aide-moi à comprendre le fonctionnement d'un filtre de Kalman.",
        Category.STUDY, False
    ),
    make_test(
        "Je voudrais apprendre les bases de SQL.",
        Category.STUDY, False
    ),
    make_test(
        "Prépare-moi une fiche sur les conditions KKT.",
        Category.STUDY, False
    ),
    make_test(
        "Pourquoi utilise-t-on une fonction de perte dans un réseau de neurones ?",
        Category.STUDY, False
    ),
    make_test(
        "Je dois apprendre les propriétés des variables gaussiennes.",
        Category.STUDY, False
    ),
    make_test(
        "Donne-moi un exemple détaillé de descente de gradient.",
        Category.STUDY, False
    ),
    make_test(
        "J'aimerais mieux comprendre la programmation dynamique.",
        Category.STUDY, False
    ),
    make_test(
        "Comment fonctionne la régularisation L1 par rapport à L2 ?",
        Category.STUDY, False
    ),

    # ==================================================
    # TODO — 10 tests
    # ==================================================
    make_test(
        "N'oublie pas de récupérer mon colis au point relais.",
        Category.TODO, False
    ),
    make_test(
        "Il faut que je renouvelle mon passeport.",
        Category.TODO, False
    ),
    make_test(
        "Envoie la facture à Thomas avant vendredi.",
        Category.TODO, False, deadline=next_weekday(4)
    ),
    make_test(
        "Pense à prendre rendez-vous chez le coiffeur.",
        Category.TODO, False
    ),
    make_test(
        "Je dois terminer la présentation pour lundi.",
        Category.TODO, False, deadline=next_weekday(0)
    ),
    make_test(
        "Acheter de la lessive et du dentifrice.",
        Category.TODO, False
    ),
    make_test(
        "N'oublie pas de sauvegarder les fichiers du projet.",
        Category.TODO, False
    ),
    make_test(
        "Il faut que je dépose le formulaire avant le 25 octobre.",
        Category.TODO, False, deadline=date(date.today().year, 10, 25)
    ),
    make_test(
        "Appelle l'assurance pour vérifier mon contrat.",
        Category.TODO, False
    ),
    make_test(
        "Je dois finir le compte rendu avant demain.",
        Category.TODO, False, deadline=tomorrow()
    ),

    # ==================================================
    # NOTE — 10 tests
    # ==================================================
    make_test(
        "À retenir : le numéro du local informatique est B204.",
        Category.NOTE, False
    ),
    make_test(
        "Note cette référence de livre : ISBN 978-0134685991.",
        Category.NOTE, False
    ),
    make_test(
        "Le code de l'immeuble est 7352, garde-le pour plus tard.",
        Category.NOTE, False
    ),
    make_test(
        "Idée pour le projet : ajouter un système de recherche sémantique.",
        Category.NOTE, False
    ),
    make_test(
        "Le nom du contact RH est Sophie Martin, retiens-le.",
        Category.NOTE, False
    ),
    make_test(
        "Mon numéro de dossier est FR-82416, conserve cette information.",
        Category.NOTE, False
    ),
    make_test(
        "J'ai repéré un livre intéressant sur les modèles de langage.",
        Category.NOTE, False
    ),
    make_test(
        "La salle de réunion habituelle est au troisième étage.",
        Category.NOTE, False
    ),
    make_test(
        "Souviens-toi que je préfère les réunions le matin.",
        Category.NOTE, False
    ),
    make_test(
        "Pour plus tard : l'idée d'organiser un week-end à Lisbonne.",
        Category.NOTE, False
    ),

    # ==================================================
    # OTHER — 10 tests
    # ==================================================
    make_test(
        "Je suis épuisée aujourd'hui.",
        Category.OTHER, False
    ),
    make_test(
        "Tu as passé un bon week-end ?",
        Category.OTHER, False
    ),
    make_test(
        "Cette série est vraiment incroyable.",
        Category.OTHER, False
    ),
    make_test(
        "Je ne sais plus par où commencer.",
        Category.OTHER, True
    ),
    make_test(
        "J'hésite beaucoup en ce moment.",
        Category.OTHER, True
    ),
    make_test(
        "Il faudrait que ma vie soit un peu moins chaotique.",
        Category.OTHER, True
    ),
    make_test(
        "Ce morceau me rappelle les vacances.",
        Category.OTHER, False
    ),
    make_test(
        "Tu crois que ça va s'arranger ?",
        Category.OTHER, True
    ),
    make_test(
        "Franchement, quelle journée interminable !",
        Category.OTHER, False
    ),
    make_test(
        "Je suis contente, j'ai enfin un peu de temps libre.",
        Category.OTHER, False
    ),
]


TEST_CASES.extend([
    # CALENDAR — fautes, langage oral, formulations imparfaites
    make_test(
        "rdv dentiste jeudi a 14h30 faut pas que joublie",
        Category.CALENDAR, False,
        event_date=next_weekday(3), event_time="14:30"
    ),
    make_test(
        "On se voit demain vers 18h chez moi",
        Category.CALENDAR, False,
        event_date=tomorrow(), event_time="18:00"
    ),
    make_test(
        "Réunion avec le groupe mardi prochain je crois",
        Category.CALENDAR, True
    ),
    make_test(
        "c'est quand deja le truc avec marie ?",
        Category.OTHER, True
    ),
    make_test(
        "ciné vendredi 20h mais jsais plus quel film",
        Category.CALENDAR, False,
        event_date=next_weekday(4), event_time="20:00"
    ),
    make_test(
        "demain jai un truc a 16h ou 17h jsp",
        Category.CALENDAR, True,
        event_date=tomorrow()
    ),
    make_test(
        "penser au rdv de la semaine derniere",
        Category.OTHER, True
    ),

    # RESTAURANT — demandes claires ou mal formulées
    make_test(
        "trouve moi un resto italien pas trop cher stp",
        Category.RESTAURANT, True
    ),
    make_test(
        "un japonais bon et pas a 50 balles par tete",
        Category.RESTAURANT, True
    ),
    make_test(
        "reservez une table pour 2 demain soir au nom de alice",
        Category.RESTAURANT, True
    ),
    make_test(
        "resto sympa vers la ou je suis la",
        Category.RESTAURANT, True
    ),
    make_test(
        "c koi le meilleur resto pour manger des ramens",
        Category.RESTAURANT, True
    ),
    make_test(
        "book un truc a manger vendredi",
        Category.RESTAURANT, True
    ),
    make_test(
        "on mange ou ce soir jsp aide moi",
        Category.RESTAURANT, True
    ),

    # STUDY — demandes scolaires avec fautes
    make_test(
        "explique moi les derivees jsuis perdu",
        Category.STUDY, False
    ),
    make_test(
        "c quoi deja la diference entre biais et variance",
        Category.STUDY, False
    ),
    make_test(
        "aide moi a reviser les proba pour le partiel",
        Category.STUDY, False
    ),
    make_test(
        "jcomprend rien au gradient descent",
        Category.STUDY, False
    ),
    make_test(
        "corrige mon exo stp mais explique les etapes",
        Category.STUDY, True
    ),
    make_test(
        "pk on utilise une loss cross entropie en classification",
        Category.STUDY, False
    ),
    make_test(
        "les matrices elles font nimp dans mon calcul",
        Category.STUDY, True
    ),

    # TODO — actions concrètes
    make_test(
        "faut que j'envoie le cv a la recruteuse ajd",
        Category.TODO, False
    ),
    make_test(
        "penser a racheter du dentifrice et des oeufs",
        Category.TODO, False
    ),
    make_test(
        "appel la banque demain matin",
        Category.TODO, True
    ),
    make_test(
        "faut que je finisse ce machin avant vendredi",
        Category.TODO, True
    ),
    make_test(
        "me rapeler de payer la facture internet",
        Category.TODO, False
    ),
    make_test(
        "organise moi tout ca stp",
        Category.OTHER, True
    ),
    make_test(
        "je dois faire le truc pour le dossier mais jsp quoi",
        Category.TODO, True
    ),

    # NOTE — informations à conserver
    make_test(
        "mon code de reservation cest ZX458 garde le qqpart",
        Category.NOTE, False
    ),
    make_test(
        "le wifi de lappart : reseau Maison_2G mdp temporaire123",
        Category.NOTE, False
    ),
    make_test(
        "note que pierre prefere les reunions le matin",
        Category.NOTE, False
    ),
    make_test(
        "le numero de suivi du colis c'est FR123456789",
        Category.NOTE, False
    ),
    make_test(
        "a retenir le prof a dit que le rendu serait en pdf",
        Category.NOTE, False
    ),
    make_test(
        "garde ca en tete pour plus tard stp",
        Category.NOTE, True
    ),

    # OTHER — ambigu, incomplet, conversationnel ou absurde
    make_test(
        "bon bah voila quoi mdr",
        Category.OTHER, True
    ),
    make_test(
        "le truc il fait pouet pouet dans la dimension bleue",
        Category.OTHER, True
    ),
    make_test(
        "j'ai une idée mais elle est partie faire des courses",
        Category.OTHER, True
    ),
    make_test(
        "fais le machin comme l'autre fois enfin tu vois",
        Category.OTHER, True
    ),
    make_test(
        "demain le fromage va calculer la racine carrée du soleil",
        Category.OTHER, True
    ),
    make_test(
        "je sais pas trop en vrai bref",
        Category.OTHER, True
    ),
    make_test(
        "est ce que le bleu peut etre plus mardi que la chaise",
        Category.OTHER, True
    ),
])


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
