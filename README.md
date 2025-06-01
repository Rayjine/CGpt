# CGpt - Interactive Genome Visualizer and Ensembl Query Engine

CGpt is a multifaceted bioinformatics project designed for interactive genome visualization and natural language querying of genomic data from the Ensembl database. It combines a powerful backend for data retrieval and processing with a user-friendly web interface for visualization.

## Overview

The project is primarily composed of two main components:

1.  **`ensembl-mcp`**: This component serves as a bridge to the Ensembl database. It utilizes the Model Context Protocol (MCP) to facilitate communication and allows users to query genomic data using natural language. It runs its own servers to handle these requests.
2.  **`visualizer`**: This is a web-based application that provides an interactive platform for visualizing gene data mapped across chromosomes. It supports customization and can integrate external data, such as predicted gene functions, to offer enhanced genomic insights and annotations.

A `shared` directory contains common resources, particularly data and scripts related to gene functions, used by both main components.

## Project Structure

The repository is organized as follows:

-   `README.md`: This file.
-   `launch_all.sh`: The main script to launch all services.
-   `ensembl-mcp/`:
    -   Handles Ensembl database queries via MCP.
    -   Contains servers (`run_server.py`, `ensembl_client_server.py`) and MCP implementation (`mcp_implementation.py`).
    -   Includes its own `launch.sh` script.
    -   Dependencies are managed by `requirements.txt`.
-   `visualizer/`:
    -   The genome visualization web application.
    -   Contains server logic (`server.py`, `search_routes.py`) and the website code (`cgpt-visualizer-website/`).
    -   Includes a script for fetching gene family information (`Fetch_gene_family_information_from_HGNC_website.py`).
    -   Includes its own `launch.sh` script.
    -   Dependencies are managed by `pyproject.toml` and `uv.lock`.
-   `shared/`:
    -   `gene-function/`: Contains tools and data for gene function analysis (e.g., `RNA_GO.py`). Manages its own Python environment and dependencies (`requirements.txt`, `pyproject.toml`).
    -   `utils/`: Intended for shared utility scripts (currently contains `.gitkeep`).

## Getting Started

### Prerequisites

-   Python (versions may be specified in `.python-version` files within `visualizer` and `shared/gene-function`).
-   Bash (for running launch scripts).
-   It is recommended to use Python virtual environments for each component (`ensembl-mcp`, `visualizer`, `shared/gene-function`) to manage dependencies.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd CGpt-perso
    ```

2.  **Set up `ensembl-mcp`:**
    ```bash
    cd ensembl-mcp
    python -m venv .venv  # Or your preferred virtual environment tool
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
    ```

3.  **Set up `visualizer`:**
    (The `visualizer` uses `uv` and `pyproject.toml`. You might need to install `uv` first: `pip install uv`)
    ```bash
    cd visualizer
    # Create and activate a virtual environment if desired
    # python -m venv .venv
    # source .venv/bin/activate
    uv pip install -r requirements.txt # Or based on pyproject.toml if a specific command is preferred
    cd ..
    ```

4.  **Set up `shared/gene-function`:**
    ```bash
    cd shared/gene-function
    python -m venv .venv # Or your preferred virtual environment tool
    source .venv/bin/activate
    pip install -r requirements.txt
    # Potentially also: uv pip install -r requirements.txt (if uv is used here too)
    cd ../..
    ```

## Running the Application

The primary way to launch the entire application suite is by using the `launch_all.sh` script located in the root directory.

```bash
./launch_all.sh
```

This script performs the following actions:

1.  **Clears Ports**: It first attempts to kill any processes running on ports 5001, 8000, and 8010, which are used by the application components.
    ```bash
    for p in 5001 8000 8010; do
      lsof -ti tcp:$p | xargs -r kill -9
    done
    ```

2.  **Launches `ensembl-mcp`**: It navigates into the `ensembl-mcp` directory and executes its local `launch.sh` script in the background.
    ```bash
    (cd ensembl-mcp && ./launch.sh) &
    ```
    The `ensembl-mcp/launch.sh` script activates its Python virtual environment and starts two Python servers:
    ```bash
    source .venv/bin/activate
    python run_server.py & python ensembl_client_server.py
    ```

3.  **Launches `visualizer`**: It navigates into the `visualizer` directory and executes its local `launch.sh` script.
    ```bash
    (cd visualizer  && ./launch.sh)
    ```
    The `visualizer/launch.sh` script will typically start the web server for the visualization interface.

After running `launch_all.sh`, the `ensembl-mcp` services and the `visualizer` web application should be running. You can typically access the visualizer via a web browser (e.g., `http://localhost:8000` or `http://localhost:8010`, depending on its configuration).

## Usage

Once the application is running:

-   Open the visualizer URL in your web browser to interact with the genome visualization tools.
-   The `ensembl-mcp` component provides a backend for natural language queries, which is likely integrated into the visualizer or accessible via an API endpoint (e.g., port 5001).

Refer to the individual `README.md` files in the `ensembl-mcp` and `visualizer` directories for more detailed information on their specific functionalities and usage.

## Contributing

(Details on how to contribute to the project, if applicable)

## License

(Information about the project's license, if applicable)
