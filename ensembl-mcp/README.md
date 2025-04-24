# Ensembl Genomics Assistant

A powerful tool that connects Claude AI with the Ensembl genomics database, allowing you to query genomic data through natural language.

## What is this?

This application lets you:
- Ask questions about genes, variants, and genomic data
- Search for specific genes by name or ID
- Retrieve DNA sequences
- Get detailed information about genetic variants
- Access Ensembl's rich genomic database through simple text queries

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Anthropic API key (for Claude)

### Installation



1. Set up a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Anthropic API key
   ```bash
   export ANTHROPIC_API_KEY=your_api_key  # On Windows: set ANTHROPIC_API_KEY=your_api_key
   ```

## Usage

### Start the MCP Server

First, start the Model Context Protocol server that connects to Ensembl:

```bash
python run_server.py
```

### Run the Interactive Demo

In a new terminal window (with your virtual environment activated):

```bash
python demo.py
```

Then simply type your genomics questions and get answers powered by Claude and Ensembl!

### Example Questions

- "What is the function of the BRCA1 gene?"
- "Show me information about the rs1234567 variant"
- "What genes are associated with cystic fibrosis?"
- "Get the DNA sequence for the TP53 gene"

## Available API Methods

The following genomic data operations are supported:

- **lookup_gene**: Get details about a gene by Ensembl ID
- **lookup_gene_by_symbol**: Find a gene using its common symbol (e.g., BRCA1) 
- **get_gene_sequence**: Retrieve the DNA sequence of a specific gene
- **get_variant_info**: Obtain information about a genetic variant
- **search_genes**: Find genes matching your search criteria

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.