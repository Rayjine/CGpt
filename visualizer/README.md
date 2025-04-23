# Genomics Visualization Web App

## Overview
This project is an interactive, web-based 2D genome browser built with **React** and **D3.js**. It enables users to explore chromosome data, gene tracks, and genomic annotations with intuitive navigation and visual overlays. The application is designed for researchers, educators, and anyone interested in genomics data visualization.

## Key Features
- **Chromosome Track Visualization**: Chromosomes are rendered as horizontal bars or ideograms, scaled to real genomic lengths.
- **Gene & Annotation Overlays**: Gene models, exons, introns, and regulatory features are overlaid based on GFF files. Strand orientation and feature types are visually coded.
- **Navigation & Zoom**: Users can zoom in/out (chromosome to gene/exon level) and pan along chromosomes via mouse drag or navigation controls.
- **Interactivity**: Mouse-hover tooltips show feature metadata (gene name, function, coordinates, etc.). Click or hover for details. Basic search enables jumping to genes or coordinates.
- **AI Insight Button**: Proof-of-concept button provides an “AI summary” of the visible region (e.g., interesting genes, stats, or simulated LLM output).

## Technical Stack
- **React**: UI structure, state management, and modular components.
- **D3.js**: SVG-based rendering for chromosome bars, annotation tracks, and interactive features (zoom, pan, hover).
- **Python & UV**: Python is used for data pre-processing and package management (via [uv](https://github.com/astral-sh/uv)).
- **Data Inputs**: Pre-processed FASTA for reference, GFF for annotations.

## Example User Flow
1. **Select Chromosome**: User chooses a chromosome to view.
2. **Visualize**: Chromosome is drawn to scale, with gene annotations overlaid.
3. **Navigate**: Zoom in/out, drag to pan, or search for a gene/locus.
4. **Explore**: Hover/click on genes to view details.
5. **AI Insights**: Click the “AI Insights” button for a summary of the displayed region.

## Getting Started
1. **Initialize the Python environment** (using [uv](https://github.com/astral-sh/uv)):
   ```bash
   uv init
   ```
   This will create a `pyproject.toml` for dependency management and a `.venv` for your virtual environment.
2. **Add Python dependencies** as needed:
   ```bash
   uv add <package-name>
   ```
   For example, to add numpy: `uv add numpy`
3. **Run Python scripts** (for preprocessing or data handling):
   ```bash
   uv run <your_script.py>
   ```
4. **Run the development server** (for the React frontend):
   ```bash
   cd visualizer
   npm install
   npm start
   ```
5. **Load Data**: Place your reference and annotation files in the appropriate data directory.
6. **Open in Browser**: Navigate to `http://localhost:3000` (or the port shown in your terminal).

## Directory Structure
```
visualizer/
  ├── public/           # Static files
  ├── src/              # React components & D3 logic
  ├── data/             # Genomic data (FASTA, GFF)
  ├── pyproject.toml    # Python dependencies (for preprocessing)
  └── README.md         # Project overview (this file)
```

## Data Preparation
- **Reference Genome**: Pre-process FASTA files as needed.
- **Annotations**: Supported formats: GFF.
