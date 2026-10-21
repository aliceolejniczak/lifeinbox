# LifeInbox

## Objectif

LifeInbox est un système local de compréhension de messages qui transforme
des messages libres en informations structurées : calendrier, restaurant,
études, tâches, notes ou conversation générale.

Le projet vise à comparer deux approches :
1. Un modèle NLP classique entraîné sur des exemples annotés.
2. Un LLM local fine-tuné sur les mêmes données d'entraînement.

L'objectif est de comparer leur qualité de classification, leur capacité
à extraire des informations et leur robustesse aux formulations ambiguës.

## Environnement

- Machine : Mac Apple Silicon
- Mémoire : 16 Go de RAM
- Python : 3.12
- Environnement virtuel : .venv
- LLM local : Ollama, qwen2.5:3b

## Architecture

- `main.py` : application et logique actuelle de LifeInbox
- `baseline_v1.py` : baseline existante
- `evaluate.py` : jeu d'évaluation initial de 50 exemples
- `evaluate_test.py` : jeu de test enrichi de 101 exemples distincts
- `audit.py` : audit des prédictions et des annotations
- `audit_results/` : résultats d'audit existants
- `data/raw/` : données sources annotées
- `data/processed/` : données préparées
- `data/splits/` : séparations train/validation
- `src/classical_nlp/` : modèle NLP classique
- `src/llm_finetuning/` : fine-tuning du LLM
- `src/common/` : composants partagés
- `scripts/` : scripts reproductibles
- `configs/` : configurations des expériences
- `artifacts/` : modèles entraînés et checkpoints

## Catégories

- `calendar`
- `restaurant`
- `study`
- `todo`
- `note`
- `other`

## Schéma cible

Chaque élément peut contenir :
- `category`
- `summary`
- `event_date`
- `event_time`
- `location`
- `deadline`
- `confidence`
- `needs_clarification`

Le schéma exact et les règles d'annotation doivent rester cohérents
avec l'implémentation de référence.

## Protocole expérimental

- Conserver les jeux d'évaluation existants sans les modifier.
- Ne pas utiliser les exemples de test pour entraîner les modèles.
- Séparer les données d'entraînement et de validation.
- Comparer les modèles sur des exemples jamais vus à l'entraînement.
- Documenter les paramètres, les métriques et les résultats de chaque essai.
