import json
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path("data/raw/train.jsonl")
REFERENCE_DATE = date.today()


def date_iso(days=0):
    return (REFERENCE_DATE + timedelta(days=days)).isoformat()


def date_fr(days=0):
    return (REFERENCE_DATE + timedelta(days=days)).strftime("%d/%m/%Y")


EXAMPLES = []


def add(
    message,
    category,
    event_date=None,
    event_time=None,
    location=None,
    deadline=None,
    needs_clarification=False,
):
    EXAMPLES.append({
        "message": message,
        "reference_date": REFERENCE_DATE.isoformat(),
        "category": category,
        "event_date": event_date,
        "event_time": event_time,
        "location": location,
        "deadline": deadline,
        "needs_clarification": needs_clarification,
    })


# 1. CALENDAR — 10 exemples
add("J’ai rendez-vous chez le dentiste demain à 9 h.",
    "calendar", event_date=date_iso(1), event_time="09:00")
add("Le cours commence après-demain à 10 h.",
    "calendar", event_date=date_iso(2), event_time="10:00")
add("Réunion dans 3 jours à 14 h 30.",
    "calendar", event_date=date_iso(3), event_time="14:30")
add("Mon train part dans 7 jours à 8 h.",
    "calendar", event_date=date_iso(7), event_time="08:00")
add("J’ai un dîner ce soir à 20 h.",
    "calendar", event_date=date_iso(), event_time="20:00")
add(f"Mon rendez-vous est prévu le {date_fr(20)} à 11 h.",
    "calendar", event_date=date_iso(20), event_time="11:00")
add("Mon entretien est demain à 16 h.",
    "calendar", event_date=date_iso(1), event_time="16:00")
add("Mon examen est dans 5 jours à 8 h 30.",
    "calendar", event_date=date_iso(5), event_time="08:30")
add("J’ai une visioconférence dans 2 jours à 18 h.",
    "calendar", event_date=date_iso(2), event_time="18:00")
add(f"Le webinaire est prévu le {date_fr(12)} à 17 h.",
    "calendar", event_date=date_iso(12), event_time="17:00")


# 2. RESTAURANT — 10 exemples
add("Réserve une table pour deux demain à 20 h chez Big Mamma.",
    "restaurant", event_date=date_iso(1), event_time="20:00",
    location="Big Mamma")
add("Je cherche un restaurant italien à Paris.",
    "restaurant", location="Paris")
add("On mange chez Big Mamma dans 3 jours à 19 h ?",
    "restaurant", event_date=date_iso(3), event_time="19:00",
    location="Big Mamma")
add("Peux-tu réserver une table pour 4 personnes demain à 19 h ?",
    "restaurant", event_date=date_iso(1), event_time="19:00",
    needs_clarification=True)
add(f"J’ai réservé chez Septime le {date_fr(25)} à 19 h 30.",
    "restaurant", event_date=date_iso(25), event_time="19:30",
    location="Septime")
add("Annule la réservation du restaurant pour ce soir.",
    "restaurant", event_date=date_iso(), needs_clarification=True)
add("Trouve-moi un restaurant de sushi près de mon bureau.",
    "restaurant", needs_clarification=True)
add("Je veux commander des pizzas pour ce soir.",
    "restaurant", event_date=date_iso())
add("Est-ce que le restaurant italien est ouvert demain ?",
    "restaurant", event_date=date_iso(1), needs_clarification=True)
add("Table pour 3 au Bouillon Pigalle dans 5 jours à 20 h.",
    "restaurant", event_date=date_iso(5), event_time="20:00",
    location="Bouillon Pigalle")


# 3. STUDY — 10 exemples
add("Explique-moi la différence entre BCE et cross-entropy.", "study")
add("Je dois réviser les chaînes de Markov.", "study")
add("Fais-moi un quiz sur les lois de probabilité.", "study")
add("Peux-tu m’expliquer le fonctionnement des LSTM ?", "study")
add("Je ne comprends pas la dualité en optimisation.", "study")
add("Aide-moi à corriger mon exercice de statistiques.", "study")
add("Résume-moi ce chapitre sur les réseaux de neurones.", "study")
add("Comment fonctionne la génération de colonnes ?", "study")
add("Je veux m’entraîner sur les intégrales.", "study")
add("Explique-moi la différence entre précision et rappel en machine learning.", "study")


# 4. TODO — 10 exemples
add("Rendre le TP de probabilités avant demain.",
    "todo", deadline=date_iso(1))
add(f"Envoyer mon CV avant le {date_fr(3)}.",
    "todo", deadline=date_iso(3))
add("Acheter des cartouches d’encre.", "todo")
add("Appeler le service client demain.",
    "todo", deadline=date_iso(1))
add(f"Déposer le dossier avant le {date_fr(10)}.",
    "todo", deadline=date_iso(10))
add("Penser à répondre au mail de Thomas.", "todo")
add("Payer la facture avant après-demain.",
    "todo", deadline=date_iso(2))
add("Prendre rendez-vous chez le coiffeur.", "todo")
add(f"Envoyer le rapport avant le {date_fr(7)}.",
    "todo", deadline=date_iso(7))
add("N’oublie pas de renouveler mon abonnement dans 5 jours.",
    "todo", deadline=date_iso(5))


# 5. NOTE — 10 exemples
add("Le code du portail est 4821.", "note")
add("Mon idée pour le projet : ajouter une recherche par mots-clés.", "note")
add("Le livre recommandé par Julie s’appelle Atomic Habits.", "note")
add("Pour le gâteau, il faut 200 g de farine et 100 g de beurre.", "note")
add("Le numéro de dossier est AB-2749.", "note")
add("Penser à utiliser une validation croisée pour le modèle.", "note")
add("Le café que j’ai aimé s’appelle Café Kitsuné.", "note")
add("Ma liste de lecture contient trois articles sur les LLM.", "note")
add("La salle de réunion habituelle est au deuxième étage.", "note")
add("Idée de cadeau : un livre de photographie.", "note")


# 6. OTHER — 10 exemples
add("Salut, ça va ?", "other")
add("Merci beaucoup pour ton aide !", "other")
add("Tu fais quoi ce week-end ?", "other")
add("J’adore cette chanson.", "other")
add("Tu as vu la météo aujourd’hui ?", "other")
add("Haha, c’est trop drôle.", "other")
add("Je suis complètement fatiguée aujourd’hui.", "other")
add("Tu préfères le thé ou le café ?", "other")
add("J’aime bien ta veste.", "other")
add("À plus tard, bonne soirée !", "other")


def main():
    if OUTPUT.exists():
        raise SystemExit(
            f"Le fichier {OUTPUT} existe déjà. "
            "Je ne l’écrase pas : vérifie son contenu avant toute action."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        for example in EXAMPLES:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    counts = {}
    for example in EXAMPLES:
        category = example["category"]
        counts[category] = counts.get(category, 0) + 1

    print(f"Dataset créé : {OUTPUT}")
    print(f"Date de référence : {REFERENCE_DATE.isoformat()}")
    print(f"Nombre d'exemples : {len(EXAMPLES)}")
    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")
    print("\nImportant : relis et corrige les annotations avant l'entraînement.")


if __name__ == "__main__":
    main()
