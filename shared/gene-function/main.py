import os
import subprocess
import pandas as pd
from argparse import ArgumentParser
from typing import List
from warnings import filterwarnings
from tqdm import tqdm
from logging import log

filterwarnings("ignore", category=UserWarning)

from utils.genes_annotations import*


def select_chromosome_chunks(input_file, output_dir, chr_id, chunk_size=800):
    """
    Splits genes from a specific chromosome in a FASTA file into smaller chunks and saves them as separate files.
    Args:
        input_file (str): Path to the input FASTA file containing gene sequences.
        output_dir (str): Directory where the output chunk files will be saved.
        chr_id (int): Chromosome ID to filter genes by.
        chunk_size (int, optional): Number of genes per chunk file. Defaults to 1000.
    Returns:
        None
    Side Effects:
        - Creates the output directory if it does not exist.
        - Writes chunked gene sequences to files in the specified output directory.
        - Prints the total number of genes detected for the specified chromosome.
    Notes:
        - The function assumes the input FASTA file uses headers starting with ">" and that chromosome IDs
          are formatted as "ROS_Cfam_1.0:<chr_id>:" in the header lines.
        - Each chunk file is named using the format: `chunk<file_idx>_chr<chr_id>_<original_filename>`.
    Example:
        select_chromosome_chunks(
            input_file="genes.fasta",
            output_dir="output_chunks",
            chr_id=5,
            chunk_size=500
        )
    """

    os.makedirs(output_dir, exist_ok=True)

    gene_count = 0
    file_count = 0
    chunk = []

    def save_chunk(chunk_data, file_idx):
        output_path = os.path.join(output_dir,\
                                   f"chunk{file_idx}_chr{chr_id}_" + input_file.split("/")[-1])
        with open(output_path, "w") as f:
            for line in chunk_data:
                f.write(line + "\n")

    with open(input_file, "r") as f:
        keep = False
        for line in tqdm(f):
            # Causing errors
            if 'ENSCAFP00845004848.1' in line or 'ENSCAFP00845004853.1' in line:
                continue
            elif line.startswith(">") and not f"ROS_Cfam_1.0:{int(chr_id)}:" in line:
                keep = False
            # Gene from chr of interest
            elif line.startswith(">") and f"ROS_Cfam_1.0:{int(chr_id)}:" in line:
                # New gene starts — flush to chunk if needed
                if gene_count > 0 and gene_count % chunk_size == 0:
                    save_chunk(chunk, file_count)
                    file_count += 1
                    chunk = []

                keep = True
                gene_count += 1
                chunk.append(line.strip())
            elif keep and not line.startswith(">"):
                chunk.append(line.strip())

    # Save remaining chunk
    if chunk:
        save_chunk(chunk, file_count)
    print(f"{gene_count} genes detected in chromosome {chr_id}.")

if __name__ == "__main__":

    parser = ArgumentParser(description="Gene function prediction")
    parser.add_argument(
        "-i", "--input_file", type=str, required=True,
        help="Input file with gene sequences"
    )
    parser.add_argument(
        "-o", "--output_dir", type=str, required=True,
        help="Output directory for results"
    )
    parser.add_argument(
        "-f", "--output_file", type=str, default="annotations",
        help="Output file name for results"
    )
    parser.add_argument(
        "-s", "--specie", type=str, default=None,
        help="Specie for gene function prediction"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Verbose mode"
    )

    parser.add_argument(
        "-c", "--chromosome", type=int, default=1,
        help="Chromosome to process"
    )

    args = parser.parse_args()

    
    if args.verbose :
        print("Parsing pept fasta file")
    chunks_paths = os.path.join(args.output_dir, "chunks")
    select_chromosome_chunks(args.input_file, chunks_paths, args.chromosome, chunk_size=3)

    if args.verbose :
        print("Computing gene functions")
    all_entries = os.listdir(chunks_paths)
    files = [os.path.join(chunks_paths,f) for f in all_entries if os.path.isfile(os.path.join(chunks_paths, f))]
    compute_genes_functions(files, args.output_dir, args.output_file, args.specie)



