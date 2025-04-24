import pandas as pd
import numpy as np
from goatools.obo_parser import GODag
import os
from argparse import ArgumentParser

def process_gaf(gaf_file, go_file, output_dir, output_file, verbose=False):
    # Read the GAF file
    gaf = pd.read_csv(
        gaf_file,
        sep="\t",
        comment="!",
        header=None,
        engine="python"
    )
    
    # Filter the dataframe to only include entries for "RNAcentral"
    gaf_filtered = gaf[gaf[0] == "RNAcentral"][[9, 4]]
    gaf_filtered.columns = ["RNA_description", "GO_Term"]

    # Extract Ensembl IDs from RNA description using regular expressions
    gaf_filtered['Ensemble_id'] = gaf_filtered['RNA_description'].str.extract(r"\((ENSCAF[^\)]+)\)")[0]
    
    # Filter rows where Ensemble_id starts with 'ENSCAF'
    gaf_filtered = gaf_filtered[gaf_filtered['Ensemble_id'].str.startswith("ENSCAF", na=False)][['Ensemble_id', 'GO_Term']]

    # Load the GO DAG (Gene Ontology DAG) for GO term descriptions and types
    go_dag = GODag(go_file)

    # Prepare lists for GO term type and description
    go_type = []
    go_desc = []

    # Iterate through the GO terms in the dataframe
    for term in gaf_filtered['GO_Term']:
        try:
            go_term = go_dag[term]
            go_desc.append(go_term.name)
            go_type.append(go_term.namespace)
        except KeyError:
            # If GO term is not found in the GO DAG, append None
            go_desc.append(None)
            go_type.append(None)

    # Add the GO term type and description to the dataframe
    gaf_filtered['type'] = go_type
    gaf_filtered['desc'] = go_desc

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write the filtered dataframe to an output file
    output_path = os.path.join(output_dir, f"{output_file}.out")
    gaf_filtered.to_csv(output_path, sep="\t", header=True, index=False)

    if verbose:
        print(f"Processed file saved to {output_path}")

if __name__ == "__main__":
    # Set up the argument parser
    parser = ArgumentParser(description="Gene function prediction")
    parser.add_argument(
        "-i", "--gaf_file", type=str, required=True,
        help="Input file with gene sequences (GAF file)"
    )
    parser.add_argument(
        "-g", "--go_file", type=str, required=True,
        help="GO file for GO term descriptions"
    )
    parser.add_argument(
        "-o", "--output_dir", type=str, required=True,
        help="Output directory for results"
    )
    parser.add_argument(
        "-f", "--output_file", type=str, default="annotations",
        help="Output file name for results (without extension)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Verbose mode"
    )
    args = parser.parse_args()

    # Process the GAF file and generate the output
    process_gaf(args.input_file, args.output_dir, args.output_file, args.verbose)