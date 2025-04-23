#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import re
import sys
import time


def sanitize_filename(name):
    """Removes or replaces characters problematic for filenames."""
    # Remove characters that are definitely bad
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    # Replace spaces with underscores (optional, but often good practice)
    name = name.replace(" ", "_")
    # You might add more specific replacements if needed
    return name


def split_gff_by_chromosome(input_gff_path: Path, output_dir: Path):
    """
    Splits a GFF3 file into multiple files based on chromosome ID (column 1).

    Args:
        input_gff_path (Path): Path to the input GFF3 file.
        output_dir (Path): Path to the directory where output files will be saved.
    """
    if not input_gff_path.exists():
        print(f"Error: Input GFF file not found: {input_gff_path}", file=sys.stderr)
        sys.exit(1)

    output_files = {}
    header_lines = []
    line_count = 0
    data_line_count = 0
    start_time = time.time()

    try:
        print(f"Processing input file: {input_gff_path}")
        with open(input_gff_path, "r") as infile:
            for line in infile:
                line_count += 1
                if line_count % 100000 == 0:  # Progress indicator
                    elapsed = time.time() - start_time
                    print(
                        f"  Processed {line_count:,} lines [{elapsed:.1f}s]...",
                        end="\r",
                    )

                # Store header lines
                if line.startswith("#"):
                    header_lines.append(line)
                    # Also write headers immediately to any already opened files
                    # This handles cases where headers might appear mid-file (though unusual)
                    for file_handle in output_files.values():
                        file_handle.write(line)
                    continue  # Move to next line

                # Skip empty or whitespace-only lines
                if not line.strip():
                    continue

                data_line_count += 1
                try:
                    # Split GFF line (tab-delimited)
                    fields = line.split("\t")
                    if len(fields) < 1:
                        print(
                            f"\nWarning: Skipping malformed line {line_count}: {line.strip()}",
                            file=sys.stderr,
                        )
                        continue

                    chromosome_id = fields[0].strip()

                    # Check if we already have a file open for this chromosome
                    if chromosome_id not in output_files:
                        safe_filename = sanitize_filename(chromosome_id) + ".gff"
                        output_path = output_dir / safe_filename
                        print(
                            f"\n  Detected new chromosome '{chromosome_id}', creating file: {output_path}"
                        )

                        try:
                            # Open new file and write stored headers
                            new_file = open(output_path, "w")
                            for header in header_lines:
                                new_file.write(header)
                            output_files[chromosome_id] = new_file
                        except IOError as e:
                            print(
                                f"\nError opening output file '{output_path}': {e}",
                                file=sys.stderr,
                            )
                            # Decide whether to continue or exit
                            # For now, let's just skip writing to this problematic file
                            continue  # Skip writing this line if file open failed

                    # Write the current data line to the correct file
                    if chromosome_id in output_files:
                        output_files[chromosome_id].write(line)

                except IndexError:
                    print(
                        f"\nWarning: Skipping malformed line {line_count} (not enough columns): {line.strip()}",
                        file=sys.stderr,
                    )
                    continue
                except (
                    Exception
                ) as e:  # Catch other potential errors during line processing
                    print(
                        f"\nError processing line {line_count}: {line.strip()}\n  Error: {e}",
                        file=sys.stderr,
                    )
                    continue  # Skip the problematic line

        end_time = time.time()
        print(
            f"\nFinished processing {line_count:,} total lines ({data_line_count:,} data lines)."
        )
        print(f"Total time: {end_time - start_time:.2f} seconds.")
        print(
            f"Created {len(output_files)} chromosome-specific GFF files in '{output_dir}'."
        )

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
    finally:
        # Ensure all opened files are closed
        print("Closing output files...")
        closed_count = 0
        for file_handle in output_files.values():
            if file_handle:
                try:
                    file_handle.close()
                    closed_count += 1
                except Exception as e:
                    # Log error if closing fails, but continue closing others
                    print(f"Warning: Error closing file handle: {e}", file=sys.stderr)
        print(f"Closed {closed_count} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split a GFF3 file into multiple files based on chromosome ID (column 1)."
    )
    parser.add_argument("input_gff", type=Path, help="Path to the input GFF3 file.")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Path to the output directory. Defaults to a 'chromosomes' subdirectory next to the input file.",
    )
    args = parser.parse_args()

    output_directory = args.output_dir
    if not output_directory:
        output_directory = args.input_gff.parent / "chromosomes"
        output_directory.mkdir(parents=True, exist_ok=True)
        print(f"--output-dir not specified, defaulting to: {output_directory}")

    split_gff_by_chromosome(args.input_gff, output_directory)
