# TP2 — TF-IDF et similarité cosinus

## Objectif
Comparer la requête « train billet réservation » à cinq documents, puis classer les documents du plus proche au moins proche. Le TP teste aussi une requête pertinente (« bus abonnement ville ») et une requête sans correspondance (« astronomie galaxie »).

## Fichiers
- `corpus.json` : documents et requêtes fournis.
- `tp2_tfidf_cosinus.py` : code Python.
- `requirements.txt` : dépendance scikit-learn.
- `resultats/classement_requete_principale.csv` : classement de la requête principale.
- `resultats/matrice_tfidf.csv` : vecteurs TF-IDF pour les cinq documents et la requête principale.
- `resultats/tests_autres_requetes.csv` : tests des requêtes supplémentaires.

## Méthode
1. Charger les cinq documents et la requête.
2. Utiliser un seul `TfidfVectorizer` sur les documents et la requête pour créer un espace vectoriel commun.
3. Calculer la similarité cosinus entre la requête et chaque document.
4. Trier les scores par ordre décroissant et exporter le classement.
5. Tester les autres requêtes avec `transform()` pour conserver le vocabulaire et les poids TF-IDF appris à l'étape précédente.

La similarité cosinus est comprise entre 0 et 1 pour ces vecteurs TF-IDF non négatifs : un score plus élevé indique une plus grande proximité lexicale. Un score nul indique qu'aucun terme de la requête n'est présent dans le vocabulaire appris.

## Installation et exécution
Depuis le dossier `TP2-TFIDF-Cosinus` :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tp2_tfidf_cosinus.py
```

Les fichiers CSV sont créés dans le dossier `resultats/`.

## Important
Le classement est basé sur le recouvrement lexical pondéré TF-IDF, pas sur une compréhension sémantique du sens des phrases. Les résultats exacts peuvent dépendre des options de vectorisation utilisées.
