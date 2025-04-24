import os
from Bio import SeqIO
import gzip

# --- Configuration & File Paths ---
# Adjust these paths if your script is not in the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "ncbi_dataset", "data", "GCF_014441545.1")

FASTA_FILE = os.path.join(DATA_DIR, "GCF_014441545.1_ROS_Cfam_1.0_genomic.fna")
GFF_FILE = os.path.join(DATA_DIR, "genomic.gff")

# --- Target Chromosome ---
TARGET_CHROMOSOME_ID = "NC_051805.1"

# --- 1. Load Reference Sequence for the Target Chromosome ---


def load_specific_chromosome_sequence(fasta_path, target_chrom_id):
    """Loads the sequence for a single chromosome using the FASTA index."""
    fai_path = fasta_path + ".fai"
    if not os.path.exists(fasta_path):
        print(f"Error: FASTA file not found: {fasta_path}")
        return None
    if not os.path.exists(fai_path):
        print(f"Error: FASTA index file (.fai) not found: {fai_path}")
        print("Please generate the FASTA index using 'samtools faidx'.")
        return None

    try:
        print(f"Loading FASTA index for {fasta_path}...")
        genome_index = SeqIO.index(fasta_path, "fasta")
        print(f"Available sequence IDs (first 10): {list(genome_index.keys())[:10]}")

        if target_chrom_id not in genome_index:
            print(
                f"Error: Chromosome ID '{target_chrom_id}' not found in the FASTA index."
            )
            print(
                "Please check the available IDs above and update TARGET_CHROMOSOME_ID."
            )
            return None

        print(f"Extracting sequence for chromosome '{target_chrom_id}'...")
        chromosome_record = genome_index[target_chrom_id]
        print(
            f"Successfully loaded sequence for {target_chrom_id}, Length: {len(chromosome_record.seq):,} bp."
        )
        return chromosome_record.seq  # Return the Bio.Seq sequence object

    except Exception as e:
        print(f"Error loading sequence for {target_chrom_id}: {e}")
        return None
    finally:
        # Close the index file handle if SeqIO.index keeps it open (good practice)
        if "genome_index" in locals() and hasattr(genome_index, "close"):
            genome_index.close()


# --- 2. Read GFF Annotations for the Target Chromosome (No Database) ---


def load_gff_for_chromosome(gff_path, target_chrom_id):
    """Reads a GFF file line by line and extracts annotations for a specific chromosome."""
    annotations = []
    if not os.path.exists(gff_path):
        print(f"Error: GFF file not found: {gff_path}")
        return annotations

    print(f"Reading GFF file: {gff_path} (filtering for '{target_chrom_id}')...")
    line_count = 0
    found_count = 0

    # Check if file is gzipped
    is_gzipped = gff_path.endswith(".gz")
    open_func = gzip.open if is_gzipped else open
    mode = "rt"  # Read text mode

    try:
        with open_func(gff_path, mode) as gff_handle:
            for line in gff_handle:
                line_count += 1
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                parts = line.split("\t")
                if len(parts) < 8:  # GFF requires at least 8 columns
                    # print(f"Warning: Skipping malformed GFF line {line_count}: {line}")
                    continue

                # Column 1 is the sequence ID (chromosome)
                seqid = parts[0]

                if seqid == target_chrom_id:
                    found_count += 1
                    try:
                        # Extract basic info
                        feature = {
                            "seqid": seqid,
                            "source": parts[1],
                            "type": parts[2],
                            "start": int(parts[3]),
                            "end": int(parts[4]),
                            "score": parts[5],
                            "strand": parts[6],
                            "phase": parts[7],
                            # Store attributes as a raw string for simplicity here
                            "attributes_str": parts[8] if len(parts) > 8 else "",
                            # Alternatively, parse attributes into a dict (more complex)
                        }
                        annotations.append(feature)
                    except ValueError:
                        print(
                            f"Warning: Skipping GFF line {line_count} due to invalid integer conversion (start/end): {line}"
                        )
                    except Exception as e_parse:
                        print(
                            f"Warning: Error parsing GFF line {line_count}: {e_parse} - Line: {line}"
                        )

        print(f"Finished reading GFF. Processed {line_count} lines.")
        print(f"Found {found_count} annotations for chromosome '{target_chrom_id}'.")
        return annotations

    except FileNotFoundError:
        print(f"Error: GFF file not found at {gff_path}")
        return []
    except Exception as e:
        print(f"An error occurred while reading the GFF file: {e}")
        return annotations  # Return whatever was collected before the error


# --- Main Execution ---

if __name__ == "__main__":
    print("-" * 30)
    print(f"Attempting to load data for chromosome: {TARGET_CHROMOSOME_ID}")
    print("-" * 30)

    # Load Sequence
    chromosome_sequence = load_specific_chromosome_sequence(
        FASTA_FILE, TARGET_CHROMOSOME_ID
    )

    print("\n" + "-" * 30)

    # Load Annotations
    chromosome_annotations = load_gff_for_chromosome(GFF_FILE, TARGET_CHROMOSOME_ID)

    print("-" * 30)

    if chromosome_sequence:
        print(f"\nSequence loaded for {TARGET_CHROMOSOME_ID}.")
        # print(f"First 50 bases: {chromosome_sequence[:50]}") # Uncomment to see sequence start
    else:
        print(f"\nFailed to load sequence for {TARGET_CHROMOSOME_ID}.")

    if chromosome_annotations:
        print(f"\nAnnotations loaded for {TARGET_CHROMOSOME_ID}.")
        print(f"Total annotations found: {len(chromosome_annotations)}")
        if len(chromosome_annotations) > 0:
            print("\nFirst 5 annotations:")
            for i, annot in enumerate(chromosome_annotations[:5]):
                print(
                    f"  {i + 1}. Type: {annot['type']}, Start: {annot['start']}, End: {annot['end']}, Strand: {annot['strand']}"
                )
                # print(f"     Attributes: {annot['attributes_str']}") # Uncomment to see raw attributes
    else:
        print(
            f"\nNo annotations found or error loading annotations for {TARGET_CHROMOSOME_ID}."
        )

    print("\nScript finished.")
