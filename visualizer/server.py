import os
import sqlite3
from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

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
        logging.error(f"Database file not found: {db_path}")
        abort(404, description=f"Database for chromosome '{chromosome_id}' not found.")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
        return conn, db_path
    except sqlite3.Error as e:
        logging.error(f"SQLite error connecting to {db_path}: {e}")
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
        logging.info(f"Found {len(genes)} genes for {chromosome_id} in {db_path}")
        return jsonify(genes)

    except sqlite3.Error as e:
        logging.error(f"SQLite error querying {db_path}: {e}")
        if conn:
            conn.close()
        abort(500, description="Database query error.")
    except Exception as e:
        logging.error(f"An unexpected error occurred processing {db_path}: {e}")
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
            logging.info(f"Found gene {feature_id} for {chromosome_id} in {db_path}")
            return jsonify(gene_data)
        else:
            logging.warning(
                f"Gene {feature_id} not found for {chromosome_id} in {db_path}"
            )
            abort(
                404,
                description=f"Gene with ID '{feature_id}' not found for chromosome '{chromosome_id}'.",
            )

    except sqlite3.Error as e:
        logging.error(f"SQLite error querying {db_path} for {feature_id}: {e}")
        if conn:
            conn.close()
        abort(500, description="Database query error.")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred processing {db_path} for {feature_id}: {e}"
        )
        if conn:
            conn.close()
        abort(500, description="Internal server error.")


@app.route("/api/v1/annotations/most_probable", methods=["GET"])
def get_most_probable_annotation():
    """Return the annotation with the highest PPV for a given gene."""
    chromosome_id = request.args.get("chromosome")
    gene_name = request.args.get("gene_name")
    if not chromosome_id or not gene_name:
        logging.warning("Missing 'chromosome' or 'gene_name' query parameter.")
        abort(400, description="Missing 'chromosome' or 'gene_name' query parameter.")
    conn, db_path = get_db_connection("annotations")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM annotations
            WHERE Gene_name = ?
            ORDER BY CAST(PPV AS FLOAT) DESC
            LIMIT 1
            """,
            (gene_name,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            logging.info(f"Annotation row: {row}")
            logging.info(f"Annotation dict: {dict(row)}")
            return jsonify(dict(row))
        else:
            logging.warning(
                f"No annotation found for gene '{gene_name}' on chromosome '{chromosome_id}'."
            )
            abort(
                404,
                description=f"No annotation found for gene '{gene_name}' on chromosome '{chromosome_id}'.",
            )
    except Exception as e:
        logging.error(f"Error retrieving annotation: {e}")
        if conn:
            conn.close()
        abort(500, description=f"Error retrieving annotation: {e}")


@app.route("/api/v1/annotations/all", methods=["GET"])
def get_all_annotations_for_gene():
    """Return all annotations for a gene, ordered by PPV descending."""
    chromosome_id = request.args.get("chromosome")
    gene_name = request.args.get("gene_name")
    if not chromosome_id or not gene_name:
        abort(400, description="Missing 'chromosome' or 'gene_name' query parameter.")
    conn, db_path = get_db_connection(chromosome_id)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM annotations
            WHERE Gene_name = ?
            ORDER BY CAST(PPV AS FLOAT) DESC
            """,
            (gene_name,),
        )
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        if conn:
            conn.close()
        abort(500, description=f"Error retrieving annotations: {e}")


if __name__ == "__main__":
    # Runs the Flask development server
    # Make sure the host is accessible if running React in a container/VM
    app.run(debug=True, host="0.0.0.0", port=5001)
