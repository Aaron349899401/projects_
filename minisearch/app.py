import re
from flask import Flask, request, jsonify, render_template
from markupsafe import Markup, escape
from indexer import load_index, search

app = Flask(__name__)

index, doc_info = load_index("search.db")

# ── Jinja filter: highlight query terms in text ────────────────────────────
def highlight(text, query):
    if not text or not query:
        return escape(text)
    safe_text = str(escape(text))
    tokens = re.findall(r"[a-z]{2,}", query.lower())
    for token in set(tokens):
        pattern = re.compile(re.escape(token), re.IGNORECASE)
        safe_text = pattern.sub(
            lambda m: f"<mark>{m.group(0)}</mark>",
            safe_text
        )
    return Markup(safe_text)

app.jinja_env.filters['highlight'] = highlight

# ── Routes ─────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search_route():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("index.html")
    results = search(query, index, doc_info, top_k=10)
    return render_template("results.html", query=query, results=results)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "no query provided"}), 400
    results = search(query, index, doc_info, top_k=5)
    return jsonify({"query": query, "results": results})

@app.route("/stats")
def stats():
    total_docs  = len(doc_info)
    total_terms = len(index)

    # total postings = sum of all doc lists across all terms
    total_postings = sum(len(postings) for postings in index.values())

    # average document length
    lengths = [info["length"] for info in doc_info.values()]
    avg_doc_length = round(sum(lengths) / len(lengths)) if lengths else 0

    # top 30 terms by how many docs they appear in
    top_terms = sorted(
        ((term, len(postings)) for term, postings in index.items()),
        key=lambda x: x[1],
        reverse=True
    )[:30]

    return render_template("stats.html",
        total_docs=total_docs,
        total_terms=total_terms,
        total_postings=total_postings,
        avg_doc_length=avg_doc_length,
        top_terms=top_terms
    )

if __name__ == "__main__":
    app.run(debug=True)