"""
TP1 - Tickets techniques : contacts, codes et versions
Lancer : python tp1_text_mining.py
Sorties : resultats/resultats_tickets.csv et resultats_tickets.xlsx (si openpyxl est installé)
"""
import json
import re
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "tickets.json"
OUTPUT_DIR = BASE_DIR / "resultats"
OUTPUT_DIR.mkdir(exist_ok=True)

# Tokenizer métier : les marqueurs, codes, versions, heures et nombres sont conservés.
TOKEN_PATTERN = re.compile(
    r"EMAILTOKEN|PHONETOKEN|URLTOKEN|"
    r"E\d+|\d+\.\d+|\d{1,2}:\d{2}|\d+|"
    r"[a-zA-ZÀ-ÿ]+",
    re.IGNORECASE
)

PROTECTED = {"EMAILTOKEN", "PHONETOKEN", "URLTOKEN"}

# Lemmatisation : on essaie d'utiliser spaCy + son modèle français.
# Si le modèle n'est pas installé, on utilise un petit dictionnaire de secours.
LEMMA_FALLBACK = {
    "erreurs": "erreur", "connexions": "connexion", "échouent": "échouer",
    "échoué": "échouer", "paiements": "paiement", "fichiers": "fichier",
    "supprimés": "supprimer", "supprimées": "supprimer",
    "fonctionne": "fonctionner", "fonctionnent": "fonctionner",
    "sont": "être", "est": "être", "les": "le", "des": "de",
    "après": "après", "depuis": "depuis", "mise": "mettre",
    "documentation": "documentation", "message": "message",
    "version": "version", "contact": "contact", "paiement": "paiement",
    "passe": "passer", "plus": "plus", "service": "service",
    "erreur": "erreur", "sur": "sur", "python": "python",
    "le": "le", "de": "de", "ne": "ne", "pas": "pas",
    "à": "à", "l": "le", "application": "application",
    "fermeture": "fermeture", "après": "après", "tel": "tel",
    "dh": "dh", "aide": "aide", "sur": "sur"
}

def mask_contacts(text):
    """Masque les e-mails et URL. Masque uniquement 10 chiffres après 'tel :'."""
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "EMAILTOKEN", text)
    text = re.sub(r"https?://\S+", "URLTOKEN", text)
    # Important : les autres nombres ne sont pas masqués.
    text = re.sub(r"(?i)(\btel\s*:\s*)\d{10}\b", r"\1PHONETOKEN", text)
    return text

def duplicate_key(text):
    """Clé calculée AVANT le masquage : minuscules, espaces normalisés, ponctuation ignorée."""
    text = text.casefold().strip()
    text = re.sub(r"[^\wÀ-ÿ.]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text):
    return TOKEN_PATTERN.findall(text)

def get_stemmer():
    try:
        from nltk.stem.snowball import FrenchStemmer
        return FrenchStemmer()
    except ImportError:
        return None

def simple_stem(word):
    """Solution de secours simple si NLTK n'est pas installé (moins précise que Snowball)."""
    w = word.lower()
    for suffix in ("issements", "issement", "atrices", "ateurs", "ations", "ements",
                   "ement", "ations", "ation", "ments", "ment", "ées", "es", "s", "e"):
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w

def lemmatize_words(words):
    """Lemmatise uniquement les mots ordinaires, sans modifier les tokens métier."""
    try:
        import spacy
        nlp = spacy.load("fr_core_news_sm")
        doc = nlp(" ".join(words))
        return [tok.lemma_.lower() if tok.lemma_ else tok.text.lower() for tok in doc]
    except (ImportError, OSError):
        return [LEMMA_FALLBACK.get(w.lower(), w.lower()) for w in words]

def process_ticket(ticket, stemmer):
    raw = ticket.get("text_raw", "")
    masked = mask_contacts(raw)
    tokens = tokenize(masked)

    stems, lemmas = [], []
    for token in tokens:
        upper = token.upper()
        # Les marqueurs, codes, versions, heures et nombres sont protégés.
        is_marker = upper in PROTECTED
        is_code = re.fullmatch(r"E\d+", token, re.IGNORECASE) is not None
        is_version = re.fullmatch(r"\d+\.\d+", token) is not None
        is_time = re.fullmatch(r"\d{1,2}:\d{2}", token) is not None
        is_number = token.isdigit()
        if is_marker or is_code or is_version or is_time or is_number:
            stems.append(token)
            lemmas.append(token)
        else:
            stems.append(stemmer.stem(token.lower()) if stemmer else simple_stem(token))
            lemmas.append(token.lower())  # remplacé ci-dessous par la vraie lemmatisation
    ordinary_positions = [
        i for i, token in enumerate(tokens)
        if token.upper() not in PROTECTED
        and not re.fullmatch(r"E\d+|\d+\.\d+|\d{1,2}:\d{2}|\d+", token, re.IGNORECASE)
    ]
    ordinary_words = [tokens[i] for i in ordinary_positions]
    ordinary_lemmas = lemmatize_words(ordinary_words)
    for i, lemma in zip(ordinary_positions, ordinary_lemmas):
        lemmas[i] = lemma

    return {
        "id": ticket["id"],
        "texte_brut": raw,
        "texte_masque": masked,
        "tokens": " | ".join(tokens),
        "stems": " | ".join(stems),
        "lemmes": " | ".join(lemmas),
        "cle_doublon_avant_masquage": duplicate_key(raw),
    }

def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        tickets = json.load(f)

    stemmer = get_stemmer()
    rows = [process_ticket(ticket, stemmer) for ticket in tickets]

    # Grouper les doublons potentiels sur la clé calculée avant masquage.
    groups = {}
    for row in rows:
        key = row["cle_doublon_avant_masquage"]
        if key:
            groups.setdefault(key, []).append(row["id"])
    for row in rows:
        key = row["cle_doublon_avant_masquage"]
        ids = groups.get(key, []) if key else []
        row["groupe_doublon"] = " / ".join(ids) if len(ids) > 1 else ""

    csv_path = OUTPUT_DIR / "resultats_tickets.csv"
    fields = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    try:
        import pandas as pd
        xlsx_path = OUTPUT_DIR / "resultats_tickets.xlsx"
        pd.DataFrame(rows).to_excel(xlsx_path, index=False)
        print(f"Fichier Excel créé : {xlsx_path}")
    except ImportError:
        print("Pandas/openpyxl non installés : fichier Excel non créé. Le CSV est disponible.")

    print(f"Traitement terminé : {csv_path}")
    print("Doublons potentiels :")
    for key, ids in groups.items():
        if len(ids) > 1:
            print(f"  {', '.join(ids)} -> {key}")

if __name__ == "__main__":
    main()
