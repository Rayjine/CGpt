# search_routes.py
# Flask blueprint for gene ID and description keyword autocomplete search

import os
import sqlite3
from collections import defaultdict

from flask import Blueprint, jsonify, request
from fuzzy import fuzzy_top_matches

DB_BASE_DIR = os.path.join(
    os.path.dirname(__file__),
    "data",
    "ncbi_dataset",
    "ncbi_dataset",
    "data",
    "GCF_014441545.1",
    "chromosomes_db",
)

# --- CONFIG ---
GENE_DB_PATH = os.path.join(DB_BASE_DIR, "NC_051805.1.db")
ANNOT_DB_PATH = os.path.join(DB_BASE_DIR, "annotations.db")

search_bp = Blueprint("search", __name__)

desc_keyword_index = defaultdict(set)  # keyword -> set of gene ids


def build_desc_keyword_index():
    """Build in-memory reverse index: keyword -> set of gene ids."""
    global desc_keyword_index
    desc_keyword_index.clear()
    conn = sqlite3.connect(ANNOT_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, desc FROM annotations")
        for gene_id, desc in cursor.fetchall():
            if desc:
                for word in desc.lower().split():
                    desc_keyword_index[word].add(gene_id)
    finally:
        conn.close()


# Build the index at import time (server startup)
build_desc_keyword_index()


@search_bp.route("/api/v1/search/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"gene_ids": [], "descriptions": []})

    # --- Gene ID fuzzy search ---
    try:
        conn = sqlite3.connect(GENE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM features", ())
        all_gene_ids = [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()
    top_gene_ids = fuzzy_top_matches(query, all_gene_ids, limit=10, min_score=60)

    # --- Description keywords fuzzy search ---
    all_keywords = list(desc_keyword_index.keys())
    top_keywords = fuzzy_top_matches(query, all_keywords, limit=10, min_score=60)
    desc_matches = [
        {"keyword": keyword, "genes": list(desc_keyword_index[keyword])}
        for keyword in top_keywords
    ]

    return jsonify({"gene_ids": top_gene_ids, "descriptions": desc_matches})
