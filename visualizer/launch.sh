#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Setup Python Scripts ---
uv run scripts/split_gff.py \
    data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/genomic.gff \
    -t gene
uv run scripts/create_chromosome_dbs.py \
    data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/chromosomes \
    NC_051805.1.gff
uv run scripts/sequence.py \
    --fasta data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/GCF_014441545.1_ROS_Cfam_1.0_genomic.fna \
    --chromosome NC_051805.1 \
    --output cgpt-visualizer-website/src/data/chromosome_data.json


# --- Start Backend ---
uv run server.py &
BACKEND_PID=$! # Capture PID of background backend process

# --- Define Cleanup Function ---
# This function will be called by the trap on exit/interrupt
cleanup() {
    # Check if the PID variable is set and the process exists before killing
    # Redirect kill errors to /dev/null to avoid noise if process already gone
    if [ -n "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null || kill -9 $BACKEND_PID 2>/dev/null # Try graceful kill, then force kill
    fi
}

# --- Set up the Trap ---
# Execute the cleanup function on script exit (EXIT) or interruption (INT, TERM)
trap cleanup INT TERM EXIT


# --- Start Frontend ---
cd cgpt-visualizer-website || exit 1
npm install --silent # Use --silent flag or redirect > /dev/null if flag not available
# npm start runs in the foreground. Ctrl+C here triggers the INT trap.
npm start

# Script end is handled by the EXIT trap calling cleanup.