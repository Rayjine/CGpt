import argparse
import csv
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

DEFAULT_OUTPUT_DIR = (
    "data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/chromosomes_db"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create annotation DB from annotation and gene mapping files."
    )
    parser.add_argument(
        "--annotations", required=True, help="Path to annotations_filtered.out"
    )
    parser.add_argument("--csv", required=True, help="Path to dog_genome_dict.csv")
    parser.add_argument(
        "--output_dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for SQLite DB",
    )
    return parser.parse_args()


def load_gene_mapping(csv_path):
    mapping = {}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map Protein_ensembl_id to (Gene_name, Ensemble_id)
            mapping[row["Protein_ensembl_id"]] = (row["Gene_name"], row["Ensemble_id"])
    return mapping


def parse_annotations(anno_path, gene_map):
    annotations = []
    with open(anno_path) as f:
        header = f.readline().strip().split("\t")
        for line in f:
            if not line.strip():
                continue
            fields = line.strip().split("\t")
            row = dict(zip(header, fields))
            prot_id = row["gene_id"]
            gene_name, ens_id = gene_map.get(prot_id, (None, None))
            if not gene_name or not ens_id:
                logging.warning(f"No gene mapping found for {prot_id}")
                continue
            row["Gene_name"] = gene_name if gene_name else "UNKNOWN"
            row["Ensemble_id"] = ens_id if ens_id else "UNKNOWN"
            row["Protein_ensembl_id"] = prot_id
            annotations.append(row)
    return annotations, header


def write_sqlite_db(annotations, header, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    db_path = os.path.join(output_dir, "annotations.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Define columns
    columns = ["Gene_name", "Ensemble_id", "Protein_ensembl_id"] + header[
        1:
    ]  # skip gene_id in header
    col_defs = ", ".join([f"{col} TEXT" for col in columns])
    cur.execute(f"CREATE TABLE IF NOT EXISTS annotations ({col_defs})")
    # Insert data
    for row in annotations:
        values = [row.get(col, "") for col in columns]
        placeholders = ",".join(["?"] * len(values))
        cur.execute(
            f"INSERT INTO annotations ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )
    conn.commit()
    conn.close()
    print(f"Database written to {db_path}")


def main():
    args = parse_args()
    gene_map = load_gene_mapping(args.csv)
    annotations, header = parse_annotations(args.annotations, gene_map)
    write_sqlite_db(annotations, header, args.output_dir)


if __name__ == "__main__":
    main()
