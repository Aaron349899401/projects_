import re
import math
import json
import sqlite3
from collections import defaultdict

# ── 1. Stopwords ──────────────────────────────────────────────────────────────
# Common words that don't really add any meaning, and can thus be ignored
# Add these to your STOPWORDS set
STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "not", "with", "this", "that", "are",
    "was", "were", "be", "been", "has", "have", "had", "do", "does",
    "by", "from", "as", "into", "its", "also", "can", "will", "more",
    "so", "if", "no", "up", "out", "we", "he", "she", "they", "you",   
    "all", "about", "after", "which", "their", "when", "there", "one" 
}

# ── 2. Tokenizer ──────────────────────────────────────────────────────────────
def tokenize(text):
    """
    Lowercase, strip punctuation, remove stopwords, short words.
    Returns a list of tokens.
    """
    text = text.lower()
    tokens = re.findall(r"[a-z]{2,}", text)   # words of 2+ letters only
    return [t for t in tokens if t not in STOPWORDS]


# ── 3. Build index ────────────────────────────────────────────────────────────
def build_index(pages):
    index = defaultdict(lambda: defaultdict(int))
    doc_info = {}

    for url, text in pages.items():
        tokens = tokenize(text)
        if not tokens:
            continue

        # Grab first real sentence as title, not raw nav text
        sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
        title   = sentences[0][:80] if sentences else url
        snippet = ". ".join(sentences[:3])[:300] if sentences else text[:300]

        doc_info[url] = {
            "title":   title,
            "snippet": snippet,
            "length":  len(tokens)
        }

        for token in tokens:
            index[token][url] += 1

    return index, doc_info


# ── 4. TF-IDF scoring ─────────────────────────────────────────────────────────
def tfidf_score(tf, doc_length, total_docs, doc_frequency):
    """
    tf            — how many times the term appears in this doc
    doc_length    — total tokens in this doc (normalises long docs)
    total_docs    — total number of documents in the corpus
    doc_frequency — how many docs contain this term
    """
    # TF: normalise by doc length so long pages don't always win
    tf_score = tf / doc_length

    # IDF: rare words across the corpus are more valuable
    idf = math.log((total_docs + 1) / (doc_frequency + 1)) + 1

    return tf_score * idf


# ── 5. Search ─────────────────────────────────────────────────────────────────
def search(query, index, doc_info, top_k=10):
    """
    Returns a ranked list of (url, score, title, snippet) tuples.
    """
    query_tokens = tokenize(query)
    total_docs = len(doc_info)
    scores = defaultdict(float)

    for token in query_tokens:
        if token not in index:
            continue

        postings = index[token]          # { url: tf }
        doc_freq = len(postings)         # how many docs have this word

        for url, tf in postings.items():
            doc_length = doc_info[url]["length"]
            scores[url] += tfidf_score(tf, doc_length, total_docs, doc_freq)

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for url, score in ranked[:top_k]:
        results.append({
            "url":     url,
            "score":   round(score, 4),
            "title":   doc_info[url]["title"],
            "snippet": doc_info[url]["snippet"],
        })
    return results


# ── 6. Persist to SQLite ──────────────────────────────────────────────────────
def save_index(index, doc_info, db_path="search.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS postings (
        term TEXT, url TEXT, tf INTEGER,
        PRIMARY KEY (term, url)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS docs (
        url TEXT PRIMARY KEY, title TEXT, snippet TEXT, length INTEGER
    )""")
    c.execute("DELETE FROM postings")
    c.execute("DELETE FROM docs")

    for term, postings in index.items():
        for url, tf in postings.items():
            c.execute("INSERT INTO postings VALUES (?,?,?)", (term, url, tf))

    for url, info in doc_info.items():
        c.execute("INSERT INTO docs VALUES (?,?,?,?)",
                  (url, info["title"], info["snippet"], info["length"]))

    conn.commit()
    conn.close()
    print(f"Index saved to {db_path}")


def load_index(db_path="search.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    index = defaultdict(lambda: defaultdict(int))
    for term, url, tf in c.execute("SELECT term, url, tf FROM postings"):
        index[term][url] = tf

    doc_info = {}
    for url, title, snippet, length in c.execute("SELECT * FROM docs"):
        doc_info[url] = {"title": title, "snippet": snippet, "length": length}

    conn.close()
    return index, doc_info