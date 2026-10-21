
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


examples = [
    # CALENDAR (10)
    add("calendar", "Ajoute mon contrôle technique dans 9 jours à 8 h.",
        event_date=day(9), event_time="08:00", location="contrôle technique"),
    add("calendar", "Je passe chez le notaire dans 12 jours à 16 h 15.",
        event_date=day(12), event_time="16:15", location="notaire"),
    add("calendar", "Bloque le créneau de mon entretien téléphonique dans 4 jours à 11 h.",
        event_date=day(4), event_time="11:00"),
    add("calendar", "J'ai un spectacle le 18 décembre à 20 h 30 au Zénith.",
        event_date="2026-12-18", event_time="20:30", location="Zénith"),
    add("calendar", "Note le rendez-vous avec la conseillère bancaire dans 6 jours.",
        event_date=day(6), location="conseillère bancaire",
        needs_clarification=True),
    add("calendar", "Le médecin m'a donné rendez-vous le 3 novembre à 9 h 20.",
        event_date="2026-11-03", event_time="09:20", location="médecin"),
    add("calendar", "Prévois un appel avec Hugo dans 2 jours vers 17 h.",
        event_date=day(2), event_time="17:00", location="appel avec Hugo"),
    add("calendar", "Mon vol décolle le 7 janvier 2027 à 6 h 10.",
        event_date="2027-01-07", event_time="06:10"),
    add("calendar", "Il faudrait qu'on se voie bientôt pour parler du dossier.",
        needs_clarification=True),
    add("calendar", "Ajoute la réunion d'équipe dans 10 jours à 14 h, en salle Atlas.",
        event_date=day(10), event_time="14:00", location="salle Atlas"),

    # RESTAURANT (10)
    add("restaurant", "Repère-moi une bonne adresse libanaise à Strasbourg.",
        location="Strasbourg"),
    add("restaurant", "Est-ce que le restaurant Arpège a une étoile Michelin ?",
        location="Arpège"),
    add("restaurant", "Réserve une table pour trois chez Big Mamma dans 8 jours à 20 h 30.",
        event_date=day(8), event_time="20:30", location="Big Mamma"),
    add("restaurant", "Je cherche un endroit calme pour dîner à Lille, pas trop cher.",
        location="Lille"),
    add("restaurant", "Tu peux commander deux pizzas margherita chez notre pizzeria habituelle ?",
        needs_clarification=True),
    add("restaurant", "Trouve-moi un restaurant avec terrasse à proximité du Louvre.",
        location="Louvre"),
    add("restaurant", "Le restaurant a-t-il des options sans gluten ?",
        needs_clarification=True),
    add("restaurant", "Pourrais-tu réserver une table pour cinq personnes dans 3 jours à 12 h 30 au Café des Anges ?",
        event_date=day(3), event_time="12:30", location="Café des Anges"),
    add("restaurant", "Quels sont les horaires du restaurant Chez Janou ?",
        location="Chez Janou"),
    add("restaurant", "Annule la réservation au nom de Martin, je ne pourrai finalement pas venir.",
        needs_clarification=True),

    # STUDY (10)
    add("study", "Montre-moi comment calculer un intervalle de confiance pour une moyenne."),
    add("study", "Je confonds toujours précision, rappel et score F1, tu peux m'expliquer ?"),
    add("study", "Fais-moi un résumé des principales méthodes de réduction de dimension."),
    add("study", "Comment fonctionne la backpropagation dans un réseau de neurones ?"),
    add("study", "Je voudrais comprendre la différence entre MAP et maximum de vraisemblance."),
    add("study", "Prépare cinq questions pour réviser les processus de Poisson."),
    add("study", "Explique-moi la programmation dynamique avec un petit exemple numérique."),
    add("study", "Comment interpréter les coefficients d'une régression logistique ?"),
    add("study", "Aide-moi à comprendre le mécanisme d'attention multi-têtes."),
    add("study", "Je veux revoir les coupes de Gomory et leur rôle en optimisation entière."),

    # TODO (10)
    add("todo", "Transmettre les feuilles de temps à mon responsable avant le 27 novembre.",
        deadline="2026-11-27"),
    add("todo", "Pense à récupérer le colis au point relais."),
    add("todo", "Il faut que je prenne mes billets de train d'ici 5 jours.",
        deadline=day(5)),
    add("todo", "Mettre à jour les dépendances du projet avant la fin de la semaine.",
        needs_clarification=True),
    add("todo", "N'oublie pas de rapporter les clés à l'accueil."),
    add("todo", "Je dois envoyer ma candidature au plus tard dans 7 jours.",
        deadline=day(7)),
    add("todo", "Faire le tri dans les fichiers téléchargés."),
    add("todo", "Il faudrait que je demande une attestation à la scolarité.",
        needs_clarification=False),
    add("todo", "Pense à renouveler l'assurance avant le 15 décembre.",
        deadline="2026-12-15"),
    add("todo", "Préparer les slides de la présentation dans 3 jours.",
        deadline=day(3)),

    # NOTE (10)
    add("note", "La salle de réunion réservée pour le projet s'appelle Orion."),
    add("note", "Le dépôt Git principal utilise la branche develop."),
    add("note", "Pour le rapport, les figures doivent être numérotées par chapitre."),
    add("note", "Le contact RH pour les stages est Madame Bernard."),
    add("note", "Le train retour arrive à la gare de Massy-Palaiseau."),
    add("note", "La bibliothèque universitaire ferme à 20 h en semaine."),
    add("note", "La référence du chargeur compatible est ADP-65DW."),
    add("note", "Le format demandé pour les livrables est PDF."),
    add("note", "La réunion de lancement a finalement lieu dans les locaux du client."),
    add("note", "Pour le prochain rendu, il faut utiliser le modèle LaTeX fourni sur Moodle."),

    # OTHER (10)
    add("other", "Je viens de rentrer, il y avait un monde fou dans le RER."),
    add("other", "Tu connais une bonne série à regarder en ce moment ?"),
    add("other", "Ah mince, j'espère que ça va s'arranger."),
    add("other", "Je t'envoie ça dès que je peux."),
    add("other", "On a vraiment eu de la chance avec le temps aujourd'hui."),
    add("other", "Mdr je ne m'attendais pas du tout à ça."),
    add("other", "Tu préfères le café ou le thé ?"),
    add("other", "Je suis complètement fan de cette chanson."),
    add("other", "Pas de souci, merci de m'avoir prévenue !"),
    add("other", "C'est fou comme la journée est passée vite."),
]


def normalize(message):
    return " ".join(message.casefold().split())


if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"{DATA_PATH} introuvable. Lance le script depuis la racine du projet."
    )

with DATA_PATH.open("r", encoding="utf-8") as f:
    existing = [json.loads(line) for line in f if line.strip()]

if len(existing) != 180:
    raise ValueError(
        f"Le fichier contient {len(existing)} exemples au lieu de 180. "
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
    raise ValueError("Doublons dans le lot 4. Aucun ajout effectué.")

duplicates = sorted(set(new_messages) & existing_messages)
if duplicates:
    raise ValueError(
        "Messages déjà présents. Aucun ajout effectué :\n"
        + "\n".join(duplicates)
    )

with DATA_PATH.open("a", encoding="utf-8") as f:
    for example in examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")

print("Lot 4 ajouté avec succès.")
print(f"Date de référence : {TODAY.isoformat()}")
print(f"Exemples ajoutés : {len(examples)}")
print(f"Total : {len(existing) + len(examples)}")
print("Répartition du lot :", dict(counts))
