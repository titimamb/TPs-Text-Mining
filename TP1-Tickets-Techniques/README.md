# TP1 — Tickets techniques : contacts, codes et versions

## Objectif
Masquer les informations de contact ciblées sans supprimer les codes techniques, versions, heures et nombres utiles.

## Fichiers
- `tickets.json` : les 12 tickets de départ.
- `tp1_text_mining.py` : script de traitement.
- `requirements.txt` : bibliothèques Python.
- `resultats/` : résultats exportés en CSV et, si les dépendances sont installées, en Excel.

## Étapes réalisées
1. Inspection des 12 tickets : contacts, codes, versions, montants, doublon potentiel et chaîne vide.
2. Masquage des e-mails par `EMAILTOKEN`, des URL par `URLTOKEN`, et des téléphones par `PHONETOKEN` uniquement lorsqu'ils suivent `tel :` et contiennent 10 chiffres.
3. Tokenisation métier avec une expression régulière préservant marqueurs, codes `E404`/`E403`, versions comme `3.11`/`2.1`, heures comme `08:30` et nombres comme `150`.
4. Stemming et lemmatisation des mots ordinaires seulement.
5. Création d'une clé de doublon avant le masquage et export des résultats.

## Installation et exécution
Depuis le dossier `TP1-Tickets-Techniques` :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
python tp1_text_mining.py
```

Sur macOS/Linux, activer l'environnement avec `source .venv/bin/activate`.

Si le modèle français spaCy n'est pas installé, le script utilise un petit dictionnaire de secours pour la lemmatisation. Pour des lemmes français plus fiables, installer `fr_core_news_sm`.

## Résultat attendu
Le CSV se trouve dans `resultats/resultats_tickets.csv`. Le fichier Excel est `resultats/resultats_tickets.xlsx` si `pandas` et `openpyxl` sont disponibles.

Le doublon potentiel principal est B01/B08 : même message après normalisation de la casse, des espaces et de la ponctuation. B09 est une chaîne vide.
