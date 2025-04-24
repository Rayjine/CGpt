#!/usr/bin/env python3
import argparse
import logging
import sqlite3
import sys
import time
from pathlib import Path

import gffutils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def create_single_db(
    input_gff_path: Path, output_db_path: Path, force_create: bool = False
) -> bool:
    """
    Creates a gffutils database for a single GFF file.

    Args:
        input_gff_path (Path): Path object for the input GFF file.
        output_db_path (Path): Path object for the output database file.
        force_create (bool): If True, overwrite existing database.

    Returns:
        bool: True if database creation was successful or skipped (already exists), False otherwise.
    """
    if not input_gff_path.is_file():
        # This check might be slightly redundant if input comes from glob, but good safeguard
        logging.warning(f"Input GFF file not found: {input_gff_path}, skipping.")
        return False

    logging.info(
        f"Creating database for: {input_gff_path.name} -> {output_db_path.name}"
    )
    start_time = time.time()
    try:
        # Ensure paths passed to gffutils are strings
        gffutils.create_db(
            str(input_gff_path),
            str(output_db_path),
            force=force_create,
            keep_order=True,
            merge_strategy="merge",
            sort_attribute_values=True,
            disable_infer_genes=True,
            disable_infer_transcripts=True,
        )
        # In the "feature" table, remove "gene-" prefix from the "id" column
        conn = sqlite3.connect(str(output_db_path))
        try:
            conn.execute("UPDATE features SET id = replace(id, 'gene-', '')")
            conn.commit()
        finally:
            conn.close()
        end_time = time.time()
        logging.info(
            f"  Successfully created {output_db_path.name} in {end_time - start_time:.2f} seconds."
        )
        return True
    except Exception as e:
        logging.error(
            f"  Error creating database for {input_gff_path.name}: {e}", exc_info=False
        )
        # Clean up potentially incomplete DB file if creation failed
        if output_db_path.exists():
            try:
                output_db_path.unlink()
                logging.info(f"  Cleaned up incomplete file: {output_db_path.name}")
            except OSError:
                logging.warning(
                    f"  Could not remove incomplete file: {output_db_path.name}"
                )
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create gffutils databases for chromosome-specific GFF files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing the split GFF files (output of split_gff.py).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Directory for the output databases. Defaults to 'chromosomes_db' subdirectory within the input directory.",
    )
    parser.add_argument(
        "files",
        metavar="FILE",  # Clarify help message
        nargs="*",  # Accepts zero or more arguments
        # Keep as string initially, we'll convert to Path relative to input_dir
        type=str,
        help="Optional: Specific GFF filenames (without path) within the input directory to process. "
        "If not specified, all '.gff' files in the input directory are processed.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing database (.db) files if they exist.",
    )
    args = parser.parse_args()

    # --- Validate Input Directory ---
    input_dir = args.input_dir
    if not input_dir.is_dir():
        logging.error(f"Input directory not found or is not a directory: {input_dir}")
        sys.exit(1)

    # --- Determine and Create Output Directory ---
    # Default output dir calculation fixed to use input_dir Path object
    output_dir = (
        args.output_dir if args.output_dir else input_dir.parent / "chromosomes_db"
    )
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory: {output_dir}")
    except OSError as e:
        logging.error(f"Error creating output directory '{output_dir}': {e}")
        sys.exit(1)

    all_gff_paths = set(input_dir.glob("*.gff"))
    all_gff_paths = {p for p in all_gff_paths if p.is_file()}

    if not all_gff_paths:
        logging.warning(f"No .gff files found in {input_dir}. Exiting.")
        sys.exit(0)

    requested_files_str = set(args.files)
    requested_paths = {input_dir / fname for fname in requested_files_str}

    files_to_process_paths = set()

    if requested_files_str:
        files_to_process_paths = requested_paths & all_gff_paths
        not_found_paths = requested_paths - all_gff_paths
        if not_found_paths:
            not_found_names = sorted([p.name for p in not_found_paths])
            logging.warning(
                f"Requested files not found in input directory: {', '.join(not_found_names)}"
            )
        if not files_to_process_paths:
            logging.warning(
                f"None of the requested files were found in {input_dir}. Exiting."
            )
            sys.exit(0)
    else:
        # If no specific files were listed, process all found .gff files
        files_to_process_paths = all_gff_paths

    sorted_files_to_process = sorted(list(files_to_process_paths))

    logging.info(f"Planning to process {len(sorted_files_to_process)} files:")
    for f_path in sorted_files_to_process:
        logging.info(f"  - {f_path.name}")

    success_count = 0
    fail_count = 0
    skip_count = 0

    total_start_time = time.time()

    for input_gff_path in sorted_files_to_process:
        db_filename = input_gff_path.with_suffix(".db").name
        output_db_path = output_dir / db_filename

        if not args.force and output_db_path.exists():
            logging.info(
                f"Database already exists: {output_db_path}, skipping creation."
            )
            skip_count += 1
            continue

        if create_single_db(input_gff_path, output_db_path, args.force):
            success_count += 1
        else:
            fail_count += 1

    total_end_time = time.time()

    # --- Final Summary ---
    logging.info("-" * 30)
    logging.info("Processing Summary:")
    logging.info(f"  Successfully created: {success_count}")
    logging.info(f"  Skipped (already exist): {skip_count}")
    logging.info(f"  Failed: {fail_count}")
    logging.info(
        f"  Total files processed/skipped: {success_count + skip_count + fail_count}"
    )
    logging.info(f"  Total time: {total_end_time - total_start_time:.2f} seconds.")
    logging.info("-" * 30)

    if fail_count > 0:
        sys.exit(1)  # Exit with error code if any failures occurred


if __name__ == "__main__":
    main()
