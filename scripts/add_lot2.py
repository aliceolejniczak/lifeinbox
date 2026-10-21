import json
from datetime import date, timedelta
from pathlib import Path

PATH = Path("data/raw/train.jsonl")
TODAY = date.today()


def rel(days):
    return (TODAY + timedelta(days=days)).isoformat()


def fr_date(days):
    return (TODAY + timedelta(days=days)).strftime("%d/%m/%Y")


NEW = []


def add(message, category, event_date=None, event_time=None,
        location=None, deadline=None, needs_clarification=False):
    NEW.append({
        "message": message,
        "reference_date": TODAY.isoformat(),
        "category": category,
        "event_date": event_date,
        "event_time": event_time,
        "location": location,
        "deadline": deadline,
        "needs_clarification": needs_clarification,
    })


# CALENDAR — 10 nouveaux exemples
add("Le rendez-vous avec ma tutrice est dans 4 jours à 10 h.",
    "calendar", event_date=rel(4), event_time="10:00")
add("Bloque mon agenda pour un appel demain à 11 h 15.",
    "calendar", event_date=rel(1), event_time="11:15")
add("Je passe chez le médecin après-demain à 8 h 45.",
    "calendar", event_date=rel(2), event_time="08:45")
add(f"La présentation est programmée le {fr_date(16)} à 14 h.",
    "calendar", event_date=rel(16), event_time="14:00")
add("Mon vol décolle dans 6 jours à 7 h 20.",
    "calendar", event_date=rel(6), event_time="07:20")
add("J’ai un point avec l’équipe dans 2 jours à 9 h 30.",
    "calendar", event_date=rel(2), event_time="09:30")
add("La cérémonie aura lieu dans 30 jours à 18 h.",
    "calendar", event_date=rel(30), event_time="18:00")
add("Rappelle-moi que mon entretien est dans 3 jours à 15 h.",
    "calendar", event_date=rel(3), event_time="15:00")
add("J’ai un rendez-vous vendredi à 13 h.",
    "calendar", needs_clarification=True)
add("Le spectacle est prévu le 21/12/2026 à 20 h 30.",
    "calendar", event_date="2026-12-21", event_time="20:30")


# RESTAURANT — 10 nouveaux exemples
add("Tu peux réserver une table pour deux chez Pink Mamma demain à 21 h ?",
    "restaurant", event_date=rel(1), event_time="21:00",
    location="Pink Mamma")
add("Cherche-moi un brunch sympa à Lyon pour dimanche.",
    "restaurant", needs_clarification=True)
add("Réserve pour six personnes samedi à 20 h au Bouillon République.",
    "restaurant", needs_clarification=True, location="Bouillon République")
add("J’ai une réservation chez Daroco dans 4 jours à 19 h 30.",
    "restaurant", event_date=rel(4), event_time="19:30",
    location="Daroco")
add("On commande des sushis ce soir ?",
    "restaurant", event_date=rel(0), needs_clarification=True)
add("Trouve un restaurant végétarien près de la gare de Lyon.",
    "restaurant", location="Gare de Lyon")
add("Modifie ma réservation de demain pour 19 h au lieu de 20 h.",
    "restaurant", event_date=rel(1), event_time="19:00",
    needs_clarification=True)
add("Est-ce que Septime propose un menu dégustation ?",
    "restaurant", location="Septime")
add("Réserve une table chez un bon restaurant japonais pour demain soir.",
    "restaurant", event_date=rel(1), needs_clarification=True)
add("Je cherche une pizzeria qui livre à mon domicile.",
    "restaurant", needs_clarification=True)


# STUDY — 10 nouveaux exemples
add("Fais-moi une fiche de révision sur les lois gaussiennes.", "study")
add("Je bloque sur les multiplicateurs de Lagrange.", "study")
add("Donne-moi trois exercices corrigés sur les chaînes de Markov.", "study")
add("Comment choisir le learning rate pendant l’entraînement ?", "study")
add("Explique-moi simplement ce qu’est le surapprentissage.", "study")
add("Aide-moi à comprendre la méthode du simplexe.", "study")
add("Quelle est la différence entre un gradient et un jacobien ?", "study")
add("Interroge-moi sur les bases du deep learning.", "study")
add("Peux-tu détailler le calcul de cette espérance conditionnelle ?", "study")
add("Je voudrais un résumé des principales méthodes de clustering.", "study")


# TODO — 10 nouveaux exemples
add("Pense à envoyer les justificatifs avant demain.",
    "todo", deadline=rel(1))
add("Je dois appeler la banque après le déjeuner.",
    "todo")
add(f"Finaliser le dossier au plus tard le {fr_date(8)}.",
    "todo", deadline=rel(8))
add("Acheter du dentifrice en rentrant.",
    "todo")
add("Il faut que je réserve un créneau chez le coiffeur.",
    "todo")
add(f"Transmettre les slides avant le {fr_date(4)}.",
    "todo", deadline=rel(4))
add("Récupérer le colis demain en sortant du travail.",
    "todo")
add("N’oublie pas de résilier l’abonnement avant la fin du mois.",
    "todo", deadline=date(TODAY.year, TODAY.month, 28).isoformat())
add("Faire les démarches pour renouveler ma carte d’identité.",
    "todo")
add("Je dois rapporter les livres à la bibliothèque d’ici 3 jours.",
    "todo", deadline=rel(3))


# NOTE — 10 nouveaux exemples
add("Le wifi de l’appartement s’appelle Maison_5G.", "note")
add("Pour le projet, la priorité est de réduire le temps d’inférence.", "note")
add("Le restaurant recommandé par Paul est Le Baratin.", "note")
add("Le format de date utilisé par l’API est AAAA-MM-JJ.", "note")
add("Le numéro de réservation de mon hôtel est HZ5832.", "note")
add("Le mot de passe temporaire du labo expire vendredi.", "note")
add("La bibliothèque universitaire ferme à 22 h en semaine.", "note")
add("Pour le prochain voyage, comparer les billets de train et d’avion.", "note")
add("Le nom de la branche Git de développement est feature/parser.", "note")
add("Le cadeau commun est organisé par Camille.", "note")


# OTHER — 10 nouveaux exemples
add("Coucou, tu es rentrée ?", "other")
add("Je suis trop contente pour toi !", "other")
add("On se tient au courant.", "other")
add("Tu as passé un bon week-end ?", "other")
add("Cette vidéo m’a fait mourir de rire.", "other")
add("Je ne sais pas quoi regarder ce soir.", "other")
add("Il fait vraiment froid aujourd’hui.", "other")
add("Merci, t’assures !", "other")
add("J’hésite entre le bleu et le vert.", "other")
add("Tu as raison, je n’avais pas vu ça comme ça.", "other")


def normalize(message):
    return " ".join(message.casefold().split())


def main():
    if not PATH.exists():
        raise SystemExit(f"Dataset introuvable : {PATH}")

    with PATH.open(encoding="utf-8") as f:
        existing = [json.loads(line) for line in f if line.strip()]

    if len(existing) != 60:
        raise SystemExit(
            f"Ajout annulé : {len(existing)} exemples présents, "
            "alors que ce script attend les 60 exemples initiaux. "
            "Aucun fichier n'a été modifié."
        )

    existing_messages = {normalize(x["message"]) for x in existing}
    new_messages = [normalize(x["message"]) for x in NEW]

    if len(NEW) != 60:
        raise SystemExit(f"Erreur interne : {len(NEW)} nouveaux exemples au lieu de 60.")

    if len(set(new_messages)) != len(new_messages):
        raise SystemExit("Ajout annulé : doublons dans le nouveau lot.")

    duplicates = existing_messages.intersection(new_messages)
    if duplicates:
        raise SystemExit(
            "Ajout annulé : certains messages existent déjà : "
            + repr(sorted(duplicates))
        )

    combined = existing + NEW
    temp = PATH.with_suffix(".jsonl.tmp")

    with temp.open("w", encoding="utf-8") as f:
        for item in combined:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    temp.replace(PATH)

    print("Lot 2 ajouté avec succès.")
    print(f"Date de référence du lot 2 : {TODAY.isoformat()}")
    print(f"Exemples ajoutés : {len(NEW)}")
    print(f"Total : {len(combined)}")

    for category in sorted({x["category"] for x in combined}):
        count = sum(x["category"] == category for x in combined)
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
