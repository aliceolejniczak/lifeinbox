# LifeInbox — Données annotées

## Jeux d'évaluation existants

- `evaluate.py` : 50 exemples d'évaluation initiale.
- `evaluate_test.py` : 101 exemples de test distincts.

Ces jeux ne doivent jamais être utilisés pour entraîner les modèles.

## Dataset d'entraînement

Le fichier `train.jsonl` contiendra les nouveaux exemples annotés,
indépendants des deux jeux d'évaluation.

Format : un objet JSON par ligne.

Champs :
- message : texte original (obligatoire)
- category : calendar, restaurant, study, todo, note ou other
- summary : résumé, uniquement si annoté
- event_date : date d'événement au format YYYY-MM-DD, ou null
- event_time : heure au format HH:MM, ou null
- location : lieu, ou null
- deadline : échéance au format YYYY-MM-DD, ou null
- needs_clarification : booléen

Les champs absents doivent être annotés explicitement comme null
lorsqu'ils font partie du schéma cible.

Ne pas inventer de labels ni reprendre les prédictions du modèle
comme des annotations de référence.

Le champ confidence n'est pas une cible d'entraînement pour le moment.

## Séparation des données

- train : apprentissage des modèles
- validation : choix des hyperparamètres
- test : évaluation finale, jamais utilisé pour l'apprentissage

Les exemples doivent rester indépendants entre ces ensembles.
