import argparse
import json
from pathlib import Path

from Bio import SeqIO


def main(args):
    """Reads FASTA, finds target chromosome, and writes data to JSON."""
    chromosome_data = None
    print(f"Reading FASTA file: {args.fasta}")
    try:
        for seq_record in SeqIO.parse(args.fasta, "fasta"):
            # print(f"Checking: {seq_record.id}") # Optional: uncomment to see progress
            if seq_record.id == args.chromosome:
                print(f"Found target chromosome: {args.chromosome}")
                chromosome_data = {
                    "name": seq_record.id,
                    "length": len(seq_record),
                    "sequence": str(seq_record.seq),
                }
                break

        if chromosome_data:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(chromosome_data, f, indent=2)  # Use indent for readability
            print("JSON file created successfully.")
            print(f"Chromosome Length: {chromosome_data['length']}")
        else:
            print(
                f"Error: Target chromosome ID '{args.chromosome}' not found in {args.fasta}"
            )

    except FileNotFoundError:
        print(f"Error: FASTA file not found at {args.fasta}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract a chromosome sequence and save it as JSON."
    )
    parser.add_argument("--fasta", required=True, help="Path to the input FASTA file.")
    parser.add_argument(
        "--chromosome",
        required=True,
        help="ID of the target chromosome/sequence in the FASTA file.",
    )
    parser.add_argument("--output", required=True, help="Path to the output JSON file.")
    args = parser.parse_args()
    main(args)  # Call the main function
