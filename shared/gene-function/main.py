from logging import log
from typing import List
import subprocess
from argparse import ArgumentParser
import pandas as pd



# def main():
#     print("Hello from gene-function!")

def filter_genes_annotations(input_file, output_file, threshold=0.6):
    """
    Filters gene annotations based on a given PPV threshold and formats the output.
    This function reads a tab-separated input file containing gene annotations, filters
    the data based on specific criteria, and writes the filtered and formatted data to
    an output file.
    Args:
        input_file (str): Path to the input file containing gene annotations.
        output_file (str): Path to the output file where filtered annotations will be saved.
        threshold (float, optional): The minimum PPV (Positive Predictive Value) threshold 
            for filtering annotations. Default is 0.6.
    Input File Requirements:
        - The input file must be a tab-separated file with the following columns:
          - 'type': Indicates the type of annotation (e.g., 'original_DE', 'CC_ARGOT', etc.).
          - 'desc': Contains metadata.
          - 'qpid': Gene identifier.
          - 'PPV': Positive Predictive Value for filtering.
          - 'id': GO term identifier.
    Output File Format:
        - The output file will be a tab-separated file with the following columns:
          - 'gene_id': Gene identifier (from 'qpid').
          - 'type': Annotation type ('cellular_component', 'biological_process', or 'molecular_function').
          - 'PPV': Positive Predictive Value.
          - 'id': GO term identifier prefixed with 'GO:'.
          - 'chromosome': Chromosome location of the gene.
          - 'start': Start position of the gene.
          - 'end': End position of the gene.
    Processing Steps:
        1. Reads the input file into a DataFrame.
        2. Extracts gene location metadata for rows with 'type' equal to 'original_DE'.
        3. Merges gene location metadata back into the main DataFrame.
        4. Filters rows with 'type' in ['CC_ARGOT', 'BP_ARGOT', 'MF_ARGOT'] and maps them 
           to human-readable annotation types.
        5. Filters rows based on the PPV threshold.
        6. Formats the 'id' column by prefixing it with 'GO:'.
        7. Selects and renames columns for the final output.
        8. Writes the filtered and formatted data to the output file.
    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If required columns are missing in the input file.
    Example:
        filter_genes_annotations(
            input_file="gene_annotations.out",
            output_file="gene_annotations_filtered.tsv",
            threshold=0.7
        )
    """


    df = pd.read_csv(input_file, sep="\t")
    print("Input file: ", input_file)

    # Extract gene location from file
    df_metadata = df[df['type'] == 'original_DE']
    df_metadata[['chromosome', 'start', 'end']] = (
        df_metadata['desc']
        .str.split(":", expand=True)
        .iloc[:, 2:5])

    # Add gene location to the main dataframe
    df = df.merge(df_metadata[['qpid', 'chromosome', 'start', 'end']], on='qpid')
    df = df[df['type'].isin(['CC_ARGOT', 'BP_ARGOT', 'MF_ARGOT'])]
    df['type'] = df['type'].map({
        'CC_ARGOT': 'cellular_component',
        'BP_ARGOT': 'biological_process',
        'MF_ARGOT': 'molecular_function',
    })
    df['PPV'] = df['PPV'].astype(float)
    df = df[df['PPV'] >= threshold]
    df['id'] = df['id'].apply(lambda x: 'GO:' + str(x))

    # Final formatting
    df = df[['qpid', 'type', 'PPV', 'id', 'chromosome', 'start', 'end', 'desc']].rename(columns={'qpid': 'gene_id'})
    df.to_csv(output_file, sep="\t", index=False)

    

def compute_genes_annotations(input_file, output_dir, output_file, specie=None, **kwargs):
    """
    Executes a gene annotation computation pipeline using the SANSPANZ tool and filters the results.
    Args:
        input_file (str): Path to the input file containing gene data.
        output_dir (str): Directory where the output files will be saved.
        output_file (str): Name of the main output file (without extension).
        specie (str, optional): Species identifier to be used in the analysis. Defaults to None.
        **kwargs: Additional keyword arguments for future extensions.
    Raises:
        subprocess.CalledProcessError: If the SANSPANZ command fails during execution.
    Side Effects:
        - Runs the SANSPANZ tool to compute gene annotations.
        - Generates output files in the specified output directory.
        - Filters the generated annotations and saves the filtered results.
    Note:
        The function assumes that the SANSPANZ tool is available and properly configured in the environment.
    """


    command = [
        "python", "SANSPANZ.3/runsanspanz.py",
        "-R",
        "-o", f'",{output_dir}/DE.out,{output_dir}/GO.out,{output_dir}/{output_file}.out"',
        f'-s "{specie}"' if specie else "",
        "<", input_file
    ]

    subprocess.run(" ".join(command), shell=True, check=True)

    filter_genes_annotations(f"{output_dir}/{output_file}.out", f"{output_dir}/{output_file}_filtered.out")



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
    args = parser.parse_args()


    compute_genes_annotations(args.input_file, args.output_dir, args.output_file, args.specie)
