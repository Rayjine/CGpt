import os
import sqlite3
from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import json

# --- Configuration ---
# Adjust this path if your DB files are located elsewhere relative to server.py
DB_BASE_DIR = os.path.join(
    os.path.dirname(__file__),
    "data",
    "ncbi_dataset",
    "ncbi_dataset",
    "data",
    "GCF_014441545.1",
    "chromosomes_db",
)
# --- End Configuration ---

app = Flask(__name__)
CORS(app)  # Allow requests from other origins (like your React dev server)


def parse_attributes(attributes_str):
    """
    Parses attributes which may be a JSON string (from NCBI GFF/JSON) or already a dict.
    Returns a dict with only 'gbkey' and 'gene_biotype' keys if present.
    """
    if not attributes_str:
        return {}

    # Parse to dict
    if isinstance(attributes_str, dict):
        attrs = attributes_str
    else:
        try:
            attrs = json.loads(attributes_str)
        except Exception:
            attrs = {}

    # Flatten single-element lists to values
    for k, v in list(attrs.items()):
        if isinstance(v, list) and len(v) == 1:
            attrs[k] = v[0]

    # Only keep 'gbkey' and 'gene_biotype'
    return {key: attrs[key] for key in ("gbkey", "gene_biotype") if key in attrs}


# Helper function to get DB connection or abort
def get_db_connection(chromosome_id):
    """Gets DB path and checks existence, aborts on failure."""
    db_filename = f"{chromosome_id}.db"
    db_path = os.path.join(DB_BASE_DIR, db_filename)

    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        abort(404, description=f"Database for chromosome '{chromosome_id}' not found.")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
        return conn, db_path
    except sqlite3.Error as e:
        print(f"SQLite error connecting to {db_path}: {e}")
        abort(500, description="Database connection error.")


@app.route("/api/v1/genes/", methods=["GET"])
def get_all_genes_for_chromosome():
    """API endpoint to fetch all genes for a specific chromosome via query param."""
    chromosome_id = request.args.get("chromosome")
    if not chromosome_id:
        abort(400, description="Missing 'chromosome' query parameter.")

    conn, db_path = get_db_connection(chromosome_id)
    genes = []
    try:
        cursor = conn.cursor()
        # Query features table for genes matching the chromosome
        cursor.execute(
            """SELECT id, start, end, strand, attributes
               FROM features
               WHERE featuretype = 'gene' ORDER BY start"""
        )

        for row in cursor.fetchall():
            attributes = parse_attributes(row["attributes"])
            genes.append(
                {
                    "id": row["id"],  # Include the feature ID
                    "start": row["start"],
                    "end": row["end"],
                    "strand": row["strand"],
                    "attributes": attributes,
                }
            )
        conn.close()
        print(f"Found {len(genes)} genes for {chromosome_id} in {db_path}")
        return jsonify(genes)

    except sqlite3.Error as e:
        print(f"SQLite error querying {db_path}: {e}")
        if conn:
            conn.close()
        abort(500, description="Database query error.")
    except Exception as e:
        print(f"An unexpected error occurred processing {db_path}: {e}")
        if conn:
            conn.close()
        abort(500, description="Internal server error.")


@app.route("/api/v1/genes/<string:feature_id>", methods=["GET"])
def get_specific_gene(feature_id):
    """API endpoint to fetch a specific gene by its feature ID (primary key).
    Requires 'chromosome' query parameter.
    """
    chromosome_id = request.args.get("chromosome")
    if not chromosome_id:
        abort(400, description="Missing 'chromosome' query parameter.")

    conn, db_path = get_db_connection(chromosome_id)
    try:
        cursor = conn.cursor()
        # Query features table for the specific feature ID
        cursor.execute(
            """SELECT id, start, end, strand, attributes
               FROM features
               WHERE id = ? AND featuretype = 'gene'""",
            (feature_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            attributes = parse_attributes(row["attributes"])
            gene_data = {
                "id": row["id"],
                "start": row["start"],
                "end": row["end"],
                "strand": row["strand"],
                "attributes": attributes,
            }
            print(f"Found gene {feature_id} for {chromosome_id} in {db_path}")
            return jsonify(gene_data)
        else:
            print(f"Gene {feature_id} not found for {chromosome_id} in {db_path}")
            abort(
                404,
                description=f"Gene with ID '{feature_id}' not found for chromosome '{chromosome_id}'.",
            )

    except sqlite3.Error as e:
        print(f"SQLite error querying {db_path} for {feature_id}: {e}")
        if conn:
            conn.close()
        abort(500, description="Database query error.")
    except Exception as e:
        print(
            f"An unexpected error occurred processing {db_path} for {feature_id}: {e}"
        )
        if conn:
            conn.close()
        abort(500, description="Internal server error.")


if __name__ == "__main__":
    # Runs the Flask development server
    # Make sure the host is accessible if running React in a container/VM
    app.run(debug=True, host="0.0.0.0", port=5001)
