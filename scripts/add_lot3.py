
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

DATA_PATH = Path("data/raw/train.jsonl")
TODAY = date.today()

def day(n: int) -> str:
    return (TODAY + timedelta(days=n)).isoformat()

def add(category, message, *, event_date=None, event_time=None,
        location=None, deadline=None, needs_clarification=False):
    return {
        "message": message,
        "reference_date": TODAY.isoformat(),
        "category": category,
        "event_date": event_date,
        "event_time": event_time,
        "location": location,
        "deadline": deadline,
        "needs_clarification": needs_clarification,
    }

# 10 exemples par catégorie : 60 exemples au total.
examples = [
    # CALENDAR (10)
    add("calendar", "J'ai mon rendez-vous chez le dentiste dans 3 jours à 10 h.",
        event_date=day(3), event_time="10:00", location="dentiste"),
    add("calendar", "Bloque-moi une heure demain à 14 h pour mon entretien.",
        event_date=day(1), event_time="14:00", needs_clarification=False),
    add("calendar", "Déjeuner avec Clara dans 5 jours à midi, au Café de Flore.",
        event_date=day(5), event_time="12:00", location="Café de Flore"),
    add("calendar", "J'ai une visio vendredi prochain à 9 h.",
        event_date=day((4 - TODAY.weekday()) % 7 + 7),
        event_time="09:00", needs_clarification=False),
    add("calendar", "Rappelle-moi que la réunion est prévue le 20 novembre à 15 h.",
        event_date="2026-11-20", event_time="15:00"),
    add("calendar", "Le train part demain à 7 h 42 depuis la gare de Lyon.",
        event_date=day(1), event_time="07:42", location="gare de Lyon"),
    add("calendar", "J'ai un rendez-vous médical la semaine prochaine, mais je n'ai pas encore l'heure.",
        event_date=None, event_time=None, location="rendez-vous médical",
        needs_clarification=True),
    add("calendar", "Ajoute mon cours de yoga dans 2 jours à 18 h 30.",
        event_date=day(2), event_time="18:30", location="cours de yoga"),
    add("calendar", "La soutenance est le 12 décembre à 11 h, à Palaiseau.",
        event_date="2026-12-12", event_time="11:00", location="Palaiseau"),
    add("calendar", "On se voit demain ?",
        event_date=day(1), needs_clarification=True),

    # RESTAURANT (10)
    add("restaurant", "Tu peux me trouver un italien sympa à Bordeaux ?",
        location="Bordeaux"),
    add("restaurant", "Réserve une table pour deux chez Pink Mamma demain à 20 h.",
        event_date=day(1), event_time="20:00", location="Pink Mamma"),
    add("restaurant", "Est-ce que le Bouillon République prend les réservations ?",
        location="Bouillon République"),
    add("restaurant", "Je cherche un brunch avec des options végétariennes à Lyon.",
        location="Lyon"),
    add("restaurant", "Commande-moi des sushis, comme d'habitude.",
        needs_clarification=True),
    add("restaurant", "Réserve pour six personnes samedi à 19 h.",
        event_date=day((5 - TODAY.weekday()) % 7),
        event_time="19:00", needs_clarification=True),
    add("restaurant", "Le restaurant qu'on avait aimé à Marseille, tu te souviens de son nom ?",
        location="Marseille", needs_clarification=True),
    add("restaurant", "Trouve un restaurant ouvert près de la gare de Nantes.",
        location="gare de Nantes"),
    add("restaurant", "Le restaurant Le Grand Véfour sert-il un menu déjeuner ?",
        location="Le Grand Véfour"),
    add("restaurant", "Modifie ma réservation de demain : finalement, on sera quatre au lieu de deux.",
        event_date=day(1), needs_clarification=True),

    # STUDY (10)
    add("study", "Explique-moi la différence entre le gradient boosting et le random forest."),
    add("study", "Je dois réviser les chaînes de Markov pour mon examen."),
    add("study", "Tu peux me faire une fiche de révision sur les méthodes de Monte-Carlo ?"),
    add("study", "Je ne comprends pas pourquoi la cross-entropy fonctionne avec le softmax."),
    add("study", "Donne-moi trois exercices corrigés sur la dualité en optimisation."),
    add("study", "J'aimerais revoir les bases des transformers avant de passer aux LLM."),
    add("study", "Peux-tu résumer ce chapitre sur les filtres de Kalman ?"),
    add("study", "C'est quoi la différence entre une loss BCE et une cross-entropy multiclasses ?"),
    add("study", "Aide-moi à comprendre les conditions KKT avec un exemple simple."),
    add("study", "Je veux m'entraîner aux probabilités avec des questions de difficulté croissante."),

    # TODO (10)
    add("todo", "Pense à envoyer le justificatif à l'administration.",
        needs_clarification=False),
    add("todo", "Il faut que je rende le dossier avant demain soir.",
        deadline=day(1)),
    add("todo", "N'oublie pas de résilier l'abonnement avant la fin du mois.",
        deadline=(date(TODAY.year + (TODAY.month == 12),
                       TODAY.month % 12 + 1, 1) - timedelta(days=1)).isoformat()),
    add("todo", "Je dois appeler l'assurance au plus tard dans 4 jours.",
        deadline=day(4)),
    add("todo", "Achète des piles quand tu passes au supermarché."),
    add("todo", "Faudrait que je prenne rendez-vous chez le coiffeur.",
        needs_clarification=True),
    add("todo", "Envoie le compte rendu à l'équipe d'ici le 25 novembre.",
        deadline="2026-11-25"),
    add("todo", "Pense à sauvegarder le projet avant de fermer l'ordinateur."),
    add("todo", "Il faut que je renouvelle ma carte de transport cette semaine.",
        needs_clarification=True),
    add("todo", "Terminer la première version du rapport dans 6 jours.",
        deadline=day(6)),

    # NOTE (10)
    add("note", "Le code du casier de la salle de sport est 4821."),
    add("note", "Pour le projet, on a décidé de conserver PostgreSQL comme base de données."),
    add("note", "Ma pointure est du 38."),
    add("note", "Le Wi-Fi invité s'appelle Bureau-Guest."),
    add("note", "Le livre recommandé par Léa est L'Art de la simplicité."),
    add("note", "Le numéro de dossier du projet est DS-2048."),
    add("note", "Le bureau de l'association se trouve au deuxième étage."),
    add("note", "Pour les prochaines analyses, les données doivent être anonymisées."),
    add("note", "Le mot-clé du cours de demain est régularisation."),
    add("note", "Le restaurant préféré de Paul est Le Comptoir du Relais."),

    # OTHER (10)
    add("other", "Salut, tu vas bien ?"),
    add("other", "Tu as regardé le dernier épisode de la série ?"),
    add("other", "J'adore la couleur de ta veste !"),
    add("other", "Merci beaucoup pour ton aide."),
    add("other", "Haha, c'est vraiment n'importe quoi 😂"),
    add("other", "Tu as vu la météo aujourd'hui ?"),
    add("other", "Je suis dans le métro, je capte mal."),
    add("other", "Bon courage pour ta journée !"),
    add("other", "Je viens de voir une vidéo trop drôle."),
    add("other", "Oui, carrément, ça marche pour moi !"),
]

# Garde-fous : ne jamais écraser les données existantes.
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"{DATA_PATH} introuvable. Lance le script depuis la racine du projet."
    )

with DATA_PATH.open("r", encoding="utf-8") as f:
    existing = [json.loads(line) for line in f if line.strip()]

if len(existing) != 120:
    raise ValueError(
        f"Le fichier contient {len(existing)} exemples, pas 120. "
        "Arrêt sans modification."
    )

expected = {
    "calendar": 10,
    "restaurant": 10,
    "study": 10,
    "todo": 10,
    "note": 10,
    "other": 10,
}
counts = Counter(x["category"] for x in examples)

if len(examples) != 60 or counts != Counter(expected):
    raise ValueError(f"Lot incorrect : {len(examples)} exemples, répartition {counts}")

def normalize(message):
    return " ".join(message.casefold().split())

existing_messages = {normalize(x["message"]) for x in existing}
new_messages = [normalize(x["message"]) for x in examples]

if len(set(new_messages)) != len(new_messages):
    raise ValueError("Doublons à l'intérieur du lot 3.")

duplicates = set(new_messages) & existing_messages
if duplicates:
    raise ValueError(
        "Certains messages existent déjà. Aucun ajout effectué :\n"
        + "\n".join(sorted(duplicates))
    )

# Écriture uniquement après tous les contrôles.
with DATA_PATH.open("a", encoding="utf-8") as f:
    for example in examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")

print("Lot 3 ajouté avec succès.")
print(f"Date de référence du lot : {TODAY.isoformat()}")
print(f"Exemples ajoutés : {len(examples)}")
print(f"Total : {len(existing) + len(examples)}")
print("Répartition du lot :", dict(counts))
