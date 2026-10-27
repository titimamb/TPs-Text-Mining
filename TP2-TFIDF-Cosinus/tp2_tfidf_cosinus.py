"""
TP2 - TF-IDF et similarité cosinus
Lancer : python tp2_tfidf_cosinus.py
Le script utilise scikit-learn pour construire un espace TF-IDF commun.
"""
import json
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "corpus.json"
OUTPUT_DIR = BASE_DIR / "resultats"
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        corpus = json.load(f)

    documents = corpus["documents"]
    query = corpus["requete_principale"]
    texts = [doc["texte"] for doc in documents]

    # Un seul vectoriseur pour documents + requête : espace TF-IDF commun.
    vectorizer = TfidfVectorizer(lowercase=True, strip_accents="unicode")
    all_vectors = vectorizer.fit_transform(texts + [query])

    document_vectors = all_vectors[:-1]
    query_vector = all_vectors[-1]

    # Similarité cosinus entre le vecteur de la requête et chaque document.
    scores = cosine_similarity(query_vector, document_vectors).flatten()
    ranked = sorted(
        zip(documents, scores),
        key=lambda item: item[1],
        reverse=True
    )

    # Export CSV des résultats classés.
    csv_path = OUTPUT_DIR / "classement_requete_principale.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["rang", "id", "similarite_cosinus", "texte"])
        for rank, (doc, score) in enumerate(ranked, start=1):
            writer.writerow([rank, doc["id"], f"{score:.6f}", doc["texte"]])

    # Export de la matrice TF-IDF pour tous les documents et la requête.
    feature_names = vectorizer.get_feature_names_out()
    matrix_path = OUTPUT_DIR / "matrice_tfidf.csv"
    with matrix_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["texte_id"] + list(feature_names))
        labels = [doc["id"] for doc in documents] + ["REQUETE"]
        for label, vector in zip(labels, all_vectors.toarray()):
            writer.writerow([label] + [f"{value:.6f}" for value in vector])

    # Test des autres requêtes avec le même espace de vocabulaire.
    # transform() est utilisé, pas fit_transform(), afin de conserver l'espace TF-IDF appris.
    extra_path = OUTPUT_DIR / "tests_autres_requetes.csv"
    with extra_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["requete", "meilleur_document", "score_cosinus", "interpretation"])
        for extra_query in corpus["autres_requetes"]:
            q_vector = vectorizer.transform([extra_query])
            extra_scores = cosine_similarity(q_vector, document_vectors).flatten()
            best_idx = extra_scores.argmax()
            best_score = float(extra_scores[best_idx])
            if best_score == 0:
                interpretation = "Aucune correspondance dans le vocabulaire du corpus"
                best_id = "AUCUN"
            else:
                interpretation = "Correspondance lexicale trouvée"
                best_id = documents[best_idx]["id"]
            writer.writerow([extra_query, best_id, f"{best_score:.6f}", interpretation])

    print("Classement de la requête :", query)
    for rank, (doc, score) in enumerate(ranked, start=1):
        print(f"{rank}. {doc['id']} — cosinus = {score:.4f}")
        print(f"   {doc['texte']}")
    print(f"\nFichiers créés dans : {OUTPUT_DIR}")
    print(f"- {csv_path.name}")
    print(f"- {matrix_path.name}")
    print(f"- {extra_path.name}")

if __name__ == "__main__":
    main()
