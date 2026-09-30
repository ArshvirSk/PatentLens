import os
import sys
import json
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.indexer.index_builder import InvertedIndex
from src.retrieval.scorer import Scorer
from src.evaluation.metrics import precision_at_k, recall_at_k, f1_at_k, average_precision, mean_average_precision

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui'))
app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

# Load index on startup
indexer = InvertedIndex()
INDEX_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'inverted_index.json')
RAW_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'patents.json')
QUERIES_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'queries', 'evaluation_queries.json')

if os.path.exists(INDEX_PATH):
    print(f"Loading inverted index from {INDEX_PATH}...")
    indexer.load(INDEX_PATH)
    print(f"Index loaded: {indexer.doc_count} documents.")
else:
    print(f"Warning: Index file not found at {INDEX_PATH}. Please run build_index.py first.")

scorer = Scorer(indexer)


# ─── Static File Routes ───────────────────────────────────────────

@app.route('/')
def index():
    print("Serving from:", STATIC_DIR)
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)


# ─── Search API ────────────────────────────────────────────────────

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "Query is required"}), 400

    weights = data.get('weights')
    top_k = data.get('top_k', 20)
    cpc_filter = data.get('cpc_filter')
    date_from = data.get('date_from')
    date_to = data.get('date_to')

    start_time = time.time()
    results = scorer.score_query(query, weights=weights, top_k=top_k)
    elapsed = round(time.time() - start_time, 4)

    # Boolean post-filtering (FR4)
    if cpc_filter:
        results = [r for r in results if r['cpc'] == cpc_filter]
    if date_from:
        results = [r for r in results if r['date'] >= date_from]
    if date_to:
        results = [r for r in results if r['date'] <= date_to]

    # Enrich with abstract
    for r in results:
        meta = indexer.metadata.get(r['id'], {})
        r['abstract'] = meta.get('abstract', '')
        r['assignee'] = meta.get('assignee', '')
        r['citations'] = meta.get('citations', [])

    return jsonify({
        "query": query,
        "results": results,
        "total": len(results),
        "time_ms": round(elapsed * 1000, 1),
    })


# ─── Index Stats ───────────────────────────────────────────────────

@app.route('/api/stats')
def stats():
    zones = ['title', 'abstract', 'claims', 'description']
    vocab_sizes = {}
    for z in zones:
        vocab_sizes[z] = len(indexer.index.get(z, {}))

    # CPC distribution
    cpc_dist = {}
    for doc_id, meta in indexer.metadata.items():
        cpc = meta.get('cpc', 'Unknown')
        cpc_dist[cpc] = cpc_dist.get(cpc, 0) + 1

    return jsonify({
        "doc_count": indexer.doc_count,
        "vocabulary_sizes": vocab_sizes,
        "cpc_distribution": cpc_dist,
        "zones": zones,
    })


# ─── Evaluation API ───────────────────────────────────────────────

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """Run the full evaluation harness against the labeled query set."""
    data = request.json or {}
    weights = data.get('weights')
    top_k_values = data.get('top_k_values', [5, 10, 20])

    # Load evaluation queries
    if not os.path.exists(QUERIES_PATH):
        return jsonify({"error": "No evaluation queries found. Run generate_dummy_patents.py first."}), 404

    with open(QUERIES_PATH, 'r', encoding='utf-8') as f:
        eval_queries = json.load(f)

    per_query_results = []
    all_query_results = []  # for MAP

    for eq in eval_queries:
        qid = eq['query_id']
        query_text = eq['query_text']
        relevant_set = set(eq['relevant_patents'])

        results = scorer.score_query(query_text, weights=weights, top_k=max(top_k_values))
        retrieved_ids = [r['id'] for r in results]

        all_query_results.append((retrieved_ids, relevant_set))

        metrics_per_k = {}
        for k in top_k_values:
            p = precision_at_k(retrieved_ids, relevant_set, k)
            r = recall_at_k(retrieved_ids, relevant_set, k)
            f1 = f1_at_k(retrieved_ids, relevant_set, k)
            metrics_per_k[str(k)] = {
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1": round(f1, 4),
            }

        ap = average_precision(retrieved_ids, relevant_set)

        per_query_results.append({
            "query_id": qid,
            "query_text": query_text[:80] + "..." if len(query_text) > 80 else query_text,
            "num_relevant": len(relevant_set),
            "num_retrieved": len(retrieved_ids),
            "average_precision": round(ap, 4),
            "metrics": metrics_per_k,
        })

    map_score = mean_average_precision(all_query_results)

    # Aggregate averages
    agg = {}
    for k in top_k_values:
        ps = [q["metrics"][str(k)]["precision"] for q in per_query_results]
        rs = [q["metrics"][str(k)]["recall"] for q in per_query_results]
        f1s = [q["metrics"][str(k)]["f1"] for q in per_query_results]
        agg[str(k)] = {
            "avg_precision": round(sum(ps) / len(ps), 4) if ps else 0,
            "avg_recall": round(sum(rs) / len(rs), 4) if rs else 0,
            "avg_f1": round(sum(f1s) / len(f1s), 4) if f1s else 0,
        }

    return jsonify({
        "map": round(map_score, 4),
        "aggregate": agg,
        "per_query": per_query_results,
        "num_queries": len(eval_queries),
    })


# ─── Patent Detail ─────────────────────────────────────────────────

@app.route('/api/patent/<patent_id>')
def patent_detail(patent_id):
    meta = indexer.metadata.get(patent_id)
    if not meta:
        return jsonify({"error": "Patent not found"}), 404

    # Load full text from raw data
    full = {}
    if os.path.exists(RAW_PATH):
        with open(RAW_PATH, 'r', encoding='utf-8') as f:
            patents = json.load(f)
        for p in patents:
            if p['id'] == patent_id:
                full = p
                break

    return jsonify({
        "id": patent_id,
        "title": meta.get('title', ''),
        "date": meta.get('date', ''),
        "cpc": meta.get('cpc', ''),
        "assignee": meta.get('assignee', ''),
        "abstract": full.get('abstract', meta.get('abstract', '')),
        "claims": full.get('claims', ''),
        "description": full.get('description', ''),
        "citations": meta.get('citations', []),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
