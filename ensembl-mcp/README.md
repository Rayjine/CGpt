   # Ensembl Genomics with Model Context Protocol

   This project provides an MCP server to interface between Claude and the Ensembl genomics API.

   ## Setup

   1. Clone the repository
   2. Create a virtual environment: `python -m venv venv`
   3. Activate the environment: `source venv/bin/activate` (or on Windows: `venv\Scripts\activate`)
   4. Install dependencies: `pip install -r requirements.txt`

   ## Running the MCP Server

   ```bash
   python run_server.py
   ```

   ## Using the Client

   ```bash
   export ANTHROPIC_API_KEY=your_api_key
   python demo.py
   ```

   ## Available API Methods

   - lookup_gene: Get details about a gene by Ensembl ID
   - lookup_gene_by_symbol: Get details about a gene by gene symbol (e.g., BRCA1)
   - get_gene_sequence: Get the DNA sequence of a gene
   - get_variant_info: Get information about a genetic variant
   - search_genes: Search for genes matching a query