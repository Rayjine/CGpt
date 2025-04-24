import os
import pandas as pd
import subprocess
from tqdm import tqdm




def filter_genes_annotations(chunk_files, output_file, threshold=0.6):
    """
    Filters and processes gene annotations from multiple input files, and writes the results to an output file.
    Args:
        chunk_files (list of str): List of file paths to input files containing gene annotations in tab-separated format.
        output_file (str): File path to save the processed and filtered gene annotations.
        threshold (float, optional): Minimum PPV (Positive Predictive Value) threshold to filter gene annotations. 
                                      Default is 0.6.
    Returns:
        None: The function writes the processed data to the specified output file.
    Notes:
        - The input files must contain the following columns: 'type', 'desc', 'qpid', 'PPV', and 'id'.
        - The 'type' column is filtered to include only 'CC_ARGOT', 'BP_ARGOT', and 'MF_ARGOT', which are mapped to 
          'cellular_component', 'biological_process', and 'molecular_function', respectively.
        - Gene location information (chromosome, start, end) is extracted from the 'desc' column for rows where 
          'type' is 'original_DE'.
        - The 'PPV' column is converted to float and filtered based on the specified threshold.
        - The 'id' column is prefixed with 'GO:'.
        - The final output includes the following columns: 'gene_id', 'type', 'PPV', 'id', 'chromosome', 'start', 
          'end', and 'desc'.
    """


    processed_files = []
    for input_file in chunk_files:
        df = pd.read_csv(input_file, sep="\t")

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
        processed_files.append(df[['qpid', 'type', 'PPV', 'id', 'chromosome', 'start', 'end', 'desc']].rename(columns={'qpid': 'gene_id'}))

    pd.concat(processed_files).to_csv(output_file, sep="\t", index=False)
    print("Annotation file saved to ", output_file)

    

def compute_genes_functions(input_files, output_dir, output_file, specie=None):
    """
    Processes a list of input gene files to compute gene functions using the SANSPANZ tool,
    and filters the resulting annotations.
    Args:
        input_files (list of str): List of file paths to the input gene files.
        output_dir (str): Directory where the output files will be saved.
        output_file (str): Base name for the output files.
        specie (str, optional): Species name to be used as a parameter for SANSPANZ. 
                                If None, the species parameter is omitted.
    Returns:
        None
    Side Effects:
        - Creates the specified output directory if it does not exist.
        - Executes the SANSPANZ tool for each input file.
        - Saves intermediate and filtered output files in the specified output directory.
    Raises:
        subprocess.CalledProcessError: If the SANSPANZ tool execution fails for any input file.
    Notes:
        - The SANSPANZ tool is invoked via a subprocess call.
        - The function assumes the presence of the SANSPANZ.3/runsanspanz.py script in the working directory.
        - The function filters the resulting annotations using the `filter_genes_annotations` function.
    """


    intermediate_dir = os.path.join(output_dir, "interm")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(intermediate_dir, exist_ok=True)
    chunks_files = []

    for file in tqdm(input_files):
        file_id = file.split("/")[-1].split("_")[0]
        command = [
            "python", "SANSPANZ.3/runsanspanz.py",
            "-R",
            "-o", f'",,,{intermediate_dir}/{file_id}_{output_file}.out"',
            f'-s "{specie}"' if specie else "",
            "<", file
        ]

        try : 
            subprocess.run(" ".join(command), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing file {file}: {e}")
            return 
        chunks_files.append(f"{intermediate_dir}/{file_id}_{output_file}.out")

    filter_genes_annotations(chunks_files,\
                            f"{output_dir}/{output_file}_filtered.out")

