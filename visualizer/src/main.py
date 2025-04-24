# ./main.py

from pathlib import Path
import dash
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State  # Will be used later

import gffutils
from Bio import SeqIO
import os
import logging
import time

# --- Configuration & File Paths ---

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define base directory relative to this script file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "ncbi_dataset" / "data" / "GCF_014441545.1"

FASTA_FILE = DATA_DIR / "GCF_014441545.1_ROS_Cfam_1.0_genomic.fna"
GFF_FILE = DATA_DIR / "chromosomes" / "NC_051805.1.gff"

# Derived file paths
FASTA_INDEX_FILE = Path(str(FASTA_FILE) + ".fai")
GFF_DB_FILE = DATA_DIR / "annotations_small.db"


# --- Phase 1, Step 5: Annotation Database Creation (.gff) ---
def create_gff_database(gff_file_path, db_path, force_create=False):
    """
    Parses a GFF file and creates a gffutils SQLite database.

    Args:
        gff_file_path (str): Path to the input GFF file.
        db_path (str): Path where the SQLite database will be created.
        force_create (bool): If True, overwrite existing database. Defaults to False.

    Returns:
        str: The path to the database file if successful, None otherwise.
    """
    if not os.path.exists(gff_file_path):
        logging.error(f"GFF file not found: {gff_file_path}")
        return None

    if not force_create and os.path.exists(db_path):
        logging.info(f"Database already exists at {db_path}. Skipping creation.")
        # Optional: Check if DB is valid or needs update based on GFF timestamp
        return db_path

    try:
        logging.info(f"Creating GFF database from {gff_file_path} at {db_path}...")
        start_time = time.time()
        # Use infer_gene_extent=False if you encounter issues with GFF structure
        # It's often good practice to use standard directives like ##sequence-region
        # id_spec can be important depending on your GFF flavour
        gffutils.create_db(
            str(gff_file_path),
            str(db_path),
            force=True,  # Overwrite if exists (controlled by outer force_create logic)
            keep_order=True,
            merge_strategy="merge",
            sort_attribute_values=True,
            disable_infer_genes=True,
            disable_infer_transcripts=True,
            # Example id_spec if needed: id_spec={'gene': 'ID', 'mRNA': 'ID'}
        )
        end_time = time.time()
        logging.info(
            f"Database creation complete. Took {end_time - start_time:.2f} seconds."
        )
        return db_path
    except Exception as e:
        logging.error(f"Error creating GFF database: {e}", exc_info=True)
        # Clean up potentially incomplete DB file
        if os.path.exists(db_path):
            os.remove(db_path)
        return None


# --- Phase 1, Step 4: Reference Genome Loading (.fna + .fai) ---

# Global variable to hold the genome index (or use caching like LRU cache)
# Note: For multi-worker Dash deployments, global variables might not be suitable.
# Consider loading the index within the callback or using shared memory/cache.
genome_index = None


def load_genome_index(fasta_path, fai_path):
    """Loads or reloads the BioPython genome index."""
    global genome_index
    if not os.path.exists(fasta_path):
        logging.error(f"FASTA file not found: {fasta_path}")
        genome_index = None
        return False
    if not os.path.exists(fai_path):
        logging.error(f"FASTA index file (.fai) not found: {fai_path}")
        logging.error("Please generate the FASTA index using 'samtools faidx'.")
        genome_index = None
        return False

    try:
        logging.info(f"Loading FASTA index for {fasta_path}...")
        # Use SeqIO.index for direct .fai access. index_db creates a separate .idx file.
        genome_index = SeqIO.index(fasta_path, "fasta")
        logging.info(
            f"FASTA index loaded successfully. Contigs: {list(genome_index.keys())[:5]}..."
        )  # Show first 5
        return True
    except Exception as e:
        logging.error(f"Error loading FASTA index: {e}", exc_info=True)
        genome_index = None
        return False


def get_reference_sequence(chromosome, start, end):
    """
    Retrieves the reference sequence for a given genomic region.

    Args:
        chromosome (str): The chromosome/contig identifier.
        start (int): The start coordinate (1-based).
        end (int): The end coordinate (1-based, inclusive).

    Returns:
        str: The DNA sequence for the region, or None if an error occurs.
    """
    global genome_index
    if genome_index is None:
        logging.warning("Genome index is not loaded. Attempting to load...")
        if not load_genome_index(FASTA_FILE, FASTA_INDEX_FILE):
            logging.error("Cannot retrieve sequence: Genome index failed to load.")
            return None

    # Adjust for 0-based indexing used by BioPython slicing
    # Ensure start is at least 1
    query_start = max(0, start - 1)
    query_end = end  # Slicing is exclusive at the end

    try:
        if chromosome not in genome_index:
            logging.error(f"Chromosome '{chromosome}' not found in FASTA index.")
            # You might want to list available chromosomes here: logging.info(f"Available contigs: {list(genome_index.keys())}")
            return None

        record = genome_index[chromosome]
        seq_len = len(record.seq)

        # Check boundaries
        if query_start >= seq_len:
            logging.warning(
                f"Start coordinate ({start}) is beyond sequence length ({seq_len}) for {chromosome}."
            )
            return ""  # Return empty string if region is entirely outside
        if query_end > seq_len:
            logging.warning(
                f"End coordinate ({end}) exceeds sequence length ({seq_len}) for {chromosome}. Truncating."
            )
            query_end = seq_len
        if query_end <= query_start:
            logging.warning(
                f"End coordinate ({end}) is not greater than start coordinate ({start})."
            )
            return ""  # Return empty if region is invalid or has zero length

        sequence = record.seq[query_start:query_end]
        return str(sequence).upper()  # Return sequence as uppercase string

    except Exception as e:
        logging.error(
            f"Error retrieving sequence for {chromosome}:{start}-{end}: {e}",
            exc_info=True,
        )
        return None


# --- Phase 1, Step 6: Annotation Querying (from .gff database) ---

# Global variable for the FeatureDB connection (similar caveats as genome_index)
gff_db_conn = None


def connect_gff_db(db_path):
    """Connects to the GFF database."""
    global gff_db_conn
    if not os.path.exists(db_path):
        logging.error(f"GFF database not found at {db_path}")
        gff_db_conn = None
        return False
    try:
        logging.info(f"Connecting to GFF database: {db_path}")
        gff_db_conn = gffutils.FeatureDB(db_path, keep_order=True)
        logging.info("Successfully connected to GFF database.")
        return True
    except Exception as e:
        logging.error(f"Error connecting to GFF database: {e}", exc_info=True)
        gff_db_conn = None
        return False


def query_gff_features(chromosome, start, end):
    """
    Queries features from the GFF database for a given genomic region.

    Args:
        chromosome (str): The chromosome/contig identifier.
        start (int): The start coordinate (1-based).
        end (int): The end coordinate (1-based, inclusive).

    Returns:
        iterator: An iterator yielding gffutils.Feature objects, or None if error.
    """
    global gff_db_conn
    if gff_db_conn is None:
        logging.warning("GFF DB connection not established. Attempting to connect...")
        if not connect_gff_db(GFF_DB_FILE):
            logging.error("Cannot query features: GFF DB connection failed.")
            return None

    try:
        # Note: gffutils uses 1-based coordinates for region queries
        # completely_within=False finds features that overlap the region
        features = gff_db_conn.region(
            seqid=chromosome,
            start=start,
            end=end,
            strand=None,  # Query both strands
            featuretype=None,  # Query all feature types initially
            completely_within=False,
        )
        return features
    except Exception as e:
        # Handle cases where the chromosome might not exist in the GFF DB
        logging.error(
            f"Error querying GFF features for {chromosome}:{start}-{end}: {e}",
            exc_info=True,
        )
        return None


# --- Phase 1, Step 2: Dash App Boilerplate & Layout ---

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Python Gene Viewer"

# --- Phase 1, Step 3: Genome Representation (View State Management) ---
# We will use dcc.Store components to hold the current view state.
# These will be defined in the layout and updated via callbacks later.
# Example state variables needed:
# - current_chromosome (e.g., 'NC_006583.3')
# - current_start (e.g., 1)
# - current_end (e.g., 50000)
# - available_chromosomes (List loaded from FASTA index)

app.layout = html.Div(
    [
        html.H1("Python Gene Viewer (Phase 1 Backend Setup)"),
        # Placeholder for state storage (will be populated later)
        # dcc.Store(id='genome-view-state', data={
        #     'chromosome': None, # Initialize later, e.g., first chrom from index
        #     'start': 1,
        #     'end': 10000, # Default initial view size
        #     'available_chromosomes': []
        # }),
        html.Div(id="status-messages"),  # To display loading messages or errors
        html.Hr(),
        # Placeholders for controls (will be added in later phases)
        html.Div(
            [
                html.Label("Chromosome:"),
                # dcc.Dropdown(id='chromosome-dropdown', placeholder="Select Chromosome...", style={'width': '300px'}),
                html.Label("Region:"),
                # dcc.Input(id='start-input', type='number', placeholder='Start', min=1),
                # dcc.Input(id='end-input', type='number', placeholder='End', min=1),
                # html.Button('Go', id='go-button'),
            ]
        ),
        html.Br(),
        # Placeholder for the main genome browser track area
        html.Div(id="genome-browser-container"),
        # This container will hold the dcc.Graph generated by callbacks in Phase 2
    ]
)

# --- Callbacks (will be defined in Phase 2 and later) ---
# Example structure:
# @app.callback(
#     Output('genome-browser-container', 'children'),
#     [Input('go-button', 'n_clicks')],
#     [State('chromosome-dropdown', 'value'),
#      State('start-input', 'value'),
#      State('end-input', 'value')]
# )
# def update_browser_view(n_clicks, chromosome, start, end):
#     if not all([chromosome, start, end]):
#         return dash.no_update # Or return placeholder message
#
#     # 1. Fetch reference sequence using get_reference_sequence(chromosome, start, end)
#     # 2. Fetch annotation features using query_gff_features(chromosome, start, end)
#     # 3. Generate Plotly figure with tracks for sequence and features
#     # 4. Return dcc.Graph(figure=fig)
#     pass


# --- Main Execution ---

if __name__ == "__main__":
    # --- Initial Setup ---
    # 1. Ensure FASTA index exists (BioPython needs it)
    if not os.path.exists(FASTA_INDEX_FILE):
        logging.warning(f"FASTA index {FASTA_INDEX_FILE} not found.")
        logging.warning(
            "Attempting to index using BioPython (requires samtools conceptually)..."
        )
        # NOTE: BioPython doesn't *create* the .fai itself easily.
        # It's best practice to create it *before* running the app.
        # For example: `samtools faidx data/ncbi_dataset/data/GCF_014441545.1/GCF_014441545.1_ROS_Cfam_1.0_genomic.fna`
        logging.error(
            "Please generate the .fai index file manually using 'samtools faidx' before running."
        )
        # Exit if index is missing, as it's critical
        # exit(1) # Optionally uncomment to enforce index presence

    # 2. Create GFF Database if it doesn't exist or forced
    # Set force_create=True if you modify the GFF file and need to rebuild
    gff_db_path = create_gff_database(GFF_FILE, GFF_DB_FILE, force_create=False)
    if not gff_db_path:
        logging.error(
            "Failed to create or find GFF database. Annotation track will not work."
        )
        # Optionally exit if GFF DB is critical
        # exit(1)

    # 3. Pre-load genome index and GFF connection for efficiency (optional)
    #    Doing this here avoids loading on the first callback request.
    load_genome_index(FASTA_FILE, FASTA_INDEX_FILE)
    connect_gff_db(GFF_DB_FILE)

    # --- Run Dash App ---
    logging.info("Starting Dash application server...")
    app.run(
        debug=True, host="0.0.0.0", port=8050
    )  # Use 0.0.0.0 to make accessible on network
