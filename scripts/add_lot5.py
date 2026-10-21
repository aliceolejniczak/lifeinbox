
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

DATA_PATH = Path("data/raw/train.jsonl")
TODAY = date.today()


def day(n):
    return (TODAY + timedelta(days=n)).isoformat()


def add(
    category,
    message,
    *,
    event_date=None,
    event_time=None,
    location=None,
    deadline=None,
    needs_clarification=False,
):
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


# 60 nouveaux exemples : 10 par catégorie.
examples = [
    # CALENDAR (10)
    add("calendar", "Mets dans mon agenda mon rendez-vous d'optique dans 4 jours à 16 h.",
        event_date=day(4), event_time="16:00", location="opticien"),
    add("calendar", "Le webinaire commence dans 7 jours à 10 h 30.",
        event_date=day(7), event_time="10:30"),
    add("calendar", "J'ai promis de passer voir Mamie dans 3 jours après le déjeuner.",
        event_date=day(3), needs_clarification=True),
    add("calendar", "Ajoute le point projet dans 5 jours à 9 h, en visio.",
        event_date=day(5), event_time="09:00", location="visio"),
    add("calendar", "Mon rendez-vous chez le garagiste est dans 11 jours à 8 h 45.",
        event_date=day(11), event_time="08:45", location="garagiste"),
    add("calendar", "La conférence est prévue dans 14 jours à 18 h à l'auditorium.",
        event_date=day(14), event_time="18:00", location="auditorium"),
    add("calendar", "Prévois un créneau pour appeler Julie dans 2 jours à 12 h.",
        event_date=day(2), event_time="12:00", location="appel avec Julie"),
    add("calendar", "J'ai une consultation dans 6 jours, mais je ne retrouve plus l'adresse.",
        event_date=day(6), location="consultation", needs_clarification=True),
    add("calendar", "Le spectacle commence le 24 décembre 2026 à 19 h 30.",
        event_date="2026-12-24", event_time="19:30"),
    add("calendar", "On avait dit qu'on se retrouverait quelque part la semaine prochaine.",
        needs_clarification=True),

    # RESTAURANT (10)
    add("restaurant", "Une adresse pour manger des ramen à Paris, tu as ça ?",
        location="Paris"),
    add("restaurant", "Réserve une table pour deux chez Bouillon Pigalle dans 4 jours à 19 h 30.",
        event_date=day(4), event_time="19:30", location="Bouillon Pigalle"),
    add("restaurant", "Tu sais si le restaurant accepte les chiens en terrasse ?",
        needs_clarification=True),
    add("restaurant", "Trouve un restaurant près de la place Bellecour à Lyon.",
        location="place Bellecour, Lyon"),
    add("restaurant", "J'aimerais commander un plat indien, mais je ne sais pas lequel choisir.",
        needs_clarification=True),
    add("restaurant", "Quels restaurants servent encore après 22 h à Toulouse ?",
        location="Toulouse"),
    add("restaurant", "Réserve pour quatre personnes dans 6 jours à 20 h au restaurant Le Train Bleu.",
        event_date=day(6), event_time="20:00", location="Le Train Bleu"),
    add("restaurant", "Tu peux vérifier si le menu du jour est disponible chez cette adresse ?",
        needs_clarification=True),
    add("restaurant", "Je voudrais un café où travailler avec mon ordinateur à Montpellier.",
        location="Montpellier"),
    add("restaurant", "Annule ma table de demain à 12 h 30 au restaurant Le Petit Cler.",
        event_date=day(1), event_time="12:30", location="Le Petit Cler"),

    # STUDY (10)
    add("study", "Explique-moi les embeddings comme si je découvrais le NLP."),
    add("study", "Je bloque sur le calcul du gradient d'une fonction composée."),
    add("study", "Fais une comparaison entre k-means et DBSCAN avec leurs limites."),
    add("study", "Pourquoi sépare-t-on les données en train, validation et test ?"),
    add("study", "Aide-moi à lire une matrice de confusion pour un problème multiclasses."),
    add("study", "Je voudrais un exemple concret de programmation linéaire en nombres entiers."),
    add("study", "Résume les différences entre RNN, LSTM et GRU."),
    add("study", "Comment choisir le seuil de décision d'un classifieur binaire ?"),
    add("study", "Propose un exercice corrigé sur la loi normale et la loi exponentielle."),
    add("study", "Je n'arrive pas à comprendre le principe de la régularisation L1 et L2."),

    # TODO (10)
    add("todo", "Il faut que je dépose le formulaire avant le 10 décembre.",
        deadline="2026-12-10"),
    add("todo", "Pense à répondre au mail de la responsable du master."),
    add("todo", "Je dois faire les courses au plus tard dans 2 jours.",
        deadline=day(2)),
    add("todo", "À faire : nettoyer les données et documenter les colonnes."),
    add("todo", "Il faut que je récupère mon ordonnance à la pharmacie.",
        needs_clarification=False),
    add("todo", "N'oublie pas de confirmer ta présence avant demain.",
        deadline=day(1)),
    add("todo", "Il faudrait que je prenne le temps de mettre mon CV à jour."),
    add("todo", "Envoie les justificatifs dans 8 jours au plus tard.",
        deadline=day(8)),
    add("todo", "Pense à vérifier que le paiement du loyer est bien parti."),
    add("todo", "Je dois rendre les livres empruntés avant la fin du mois.",
        deadline=(date(TODAY.year + (TODAY.month == 12),
                       TODAY.month % 12 + 1, 1) - timedelta(days=1)).isoformat()),

    # NOTE (10)
    add("note", "Le nom de la branche utilisée pour la démonstration est demo-final."),
    add("note", "La salle informatique dispose de prises réseau sur les tables du fond."),
    add("note", "Le contact pour le logement est joignable uniquement par e-mail."),
    add("note", "Les exports de résultats doivent garder les identifiants d'origine."),
    add("note", "La référence du dossier est LIF-308."),
    add("note", "Le mot de passe du Wi-Fi n'est pas affiché à l'accueil."),
    add("note", "Pour la présentation, le public sera principalement composé de non-spécialistes."),
    add("note", "Le format des dates attendu par le service est AAAA-MM-JJ."),
    add("note", "La prochaine version du document doit inclure un glossaire."),
    add("note", "La salle réservée pour les oraux est la salle B214."),

    # OTHER (10)
    add("other", "Tu es dispo deux minutes ?"),
    add("other", "J'ai complètement oublié ce que je voulais te dire."),
    add("other", "Le trajet était interminable aujourd'hui."),
    add("other", "Ah oui, vu comme ça, je comprends mieux."),
    add("other", "Je viens de me faire un thé, petite pause bien méritée."),
    add("other", "Tu as écouté le nouvel album qui vient de sortir ?"),
    add("other", "Franchement, cette photo est magnifique."),
    add("other", "Je te redis ça quand j'en sais plus."),
    add("other", "Oh non, c'est vraiment pas de chance."),
    add("other", "Ça marche, à tout à l'heure !"),
]


def normalize(message):
    return " ".join(message.casefold().split())


if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"{DATA_PATH} introuvable. Lance le script depuis la racine de lifeinbox."
    )

with DATA_PATH.open("r", encoding="utf-8") as f:
    existing = [json.loads(line) for line in f if line.strip()]

if len(existing) != 240:
    raise ValueError(
        f"Le fichier contient {len(existing)} exemples au lieu de 240. "
        "Aucune modification effectuée."
    )

expected = Counter({
    "calendar": 10,
    "restaurant": 10,
    "study": 10,
    "todo": 10,
    "note": 10,
    "other": 10,
})
counts = Counter(x["category"] for x in examples)

if len(examples) != 60 or counts != expected:
    raise ValueError(f"Lot invalide : {len(examples)} exemples, répartition {counts}")

existing_messages = {normalize(x["message"]) for x in existing}
new_messages = [normalize(x["message"]) for x in examples]

if len(set(new_messages)) != len(new_messages):
    raise ValueError("Doublons à l'intérieur du lot 5. Aucun ajout effectué.")

duplicates = sorted(set(new_messages) & existing_messages)
if duplicates:
    raise ValueError(
        "Messages déjà présents. Aucun ajout effectué :\n"
        + "\n".join(duplicates)
    )

with DATA_PATH.open("a", encoding="utf-8") as f:
    for example in examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")

print("Lot 5 ajouté avec succès.")
print(f"Date de référence : {TODAY.isoformat()}")
print(f"Exemples ajoutés : {len(examples)}")
print(f"Total : {len(existing) + len(examples)}")
print("Répartition du lot :", dict(counts))
