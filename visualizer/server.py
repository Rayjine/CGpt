import os
import sqlite3
from flask import Flask, jsonify, abort, request
from flask_cors import CORS

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
    """Parses GFF/GTF style attributes string into a dictionary."""
    attributes = {}
    if not attributes_str:
        return attributes
    # Handle potential variations in separators and quoting
    parts = attributes_str.strip(";").split(";")
    for part in parts:
        part = part.strip()
        if "=" in part:
            try:
                key, value = part.split("=", 1)
                # Remove potential surrounding quotes and whitespace
                attributes[key.strip()] = value.strip().strip("\"'")
            except ValueError:
                # Handle cases where a part might not be a key=value pair correctly
                print(f"Warning: Could not parse attribute part: {part}")
                attributes[part] = None  # Or skip, depending on desired behavior
    return attributes


def get_gene_name(attrs):
    """Extracts gene name from parsed attributes, prioritizing 'Name', then 'gene'."""
    # Add more fallbacks if needed (e.g., 'locus_tag')
    return attrs.get("Name", attrs.get("gene", attrs.get("locus_tag", "UnknownGene")))


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
            gene_name = get_gene_name(attributes)
            genes.append(
                {
                    "id": row["id"],  # Include the feature ID
                    "name": gene_name,
                    "start": row["start"],
                    "end": row["end"],
                    "strand": row["strand"],
                    # Add 'attributes': attributes if needed by frontend
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
            gene_name = get_gene_name(attributes)
            gene_data = {
                "id": row["id"],
                "name": gene_name,
                "start": row["start"],
                "end": row["end"],
                "strand": row["strand"],
                # Add 'attributes': attributes if needed
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
