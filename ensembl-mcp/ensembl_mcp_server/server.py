from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from .api.ensembl import EnsemblAPI

app = FastAPI()
ensembl = EnsemblAPI()

class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any]

class MCPResponse(BaseModel):
    result: Any
    error: Optional[str] = None

@app.post("/mcp/ensembl")
async def handle_mcp_request(request: MCPRequest = Body(...)):
    try:
        # Validate required parameters for each method
        if request.method == "lookup_gene":
            if "gene_id" not in request.params:
                raise ValueError("Missing required parameter: gene_id")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.lookup_gene(request.params.get("gene_id"), request.params.get("species"))
            
        elif request.method == "lookup_gene_by_symbol":
            if "symbol" not in request.params:
                raise ValueError("Missing required parameter: symbol")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.lookup_gene_by_symbol(request.params.get("symbol"), request.params.get("species"))
            
        elif request.method == "get_gene_sequence":
            if "gene_id" not in request.params:
                raise ValueError("Missing required parameter: gene_id")
            result = ensembl.get_gene_sequence(request.params.get("gene_id"))
            
        elif request.method == "get_variant_info":
            if "variant_id" not in request.params:
                raise ValueError("Missing required parameter: variant_id")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_variant_info(request.params.get("variant_id"), request.params.get("species"))
            
        elif request.method == "search_genes":
            if "query" not in request.params:
                raise ValueError("Missing required parameter: query")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.search_genes(request.params.get("query"), request.params.get("species"))
            
        # Sequences
        elif request.method == "get_sequence_by_id":
            if "id" not in request.params:
                raise ValueError("Missing required parameter: id")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_sequence_by_id(
                request.params.get("id"),
                request.params.get("species"),
                request.params.get("mask"),
                request.params.get("expand_3prime"),
                request.params.get("expand_5prime")
            )
            
        elif request.method == "get_sequence_by_region":
            if "region" not in request.params:
                raise ValueError("Missing required parameter: region")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_sequence_by_region(
                request.params.get("region"),
                request.params.get("species")
            )
            
        # Comparative genomics
        elif request.method == "get_gene_tree":
            if "id" not in request.params:
                raise ValueError("Missing required parameter: id")
            result = ensembl.get_gene_tree(request.params.get("id"))
            
        elif request.method == "get_homology":
            if "id" not in request.params:
                raise ValueError("Missing required parameter: id")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_homology(
                request.params.get("id"),
                request.params.get("species")
            )
            
        elif request.method == "get_genomic_alignment":
            if "region" not in request.params:
                raise ValueError("Missing required parameter: region")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_genomic_alignment(
                request.params.get("region"),
                request.params.get("species")
            )
            
        # Variants and phenotypes
        elif request.method == "get_variant_consequences":
            if "variant_id" not in request.params:
                raise ValueError("Missing required parameter: variant_id")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_variant_consequences(
                request.params.get("variant_id"),
                request.params.get("species")
            )
            
        elif request.method == "get_phenotype_by_gene":
            if "gene" not in request.params:
                raise ValueError("Missing required parameter: gene")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_phenotype_by_gene(
                request.params.get("gene"),
                request.params.get("species")
            )
            
        elif request.method == "get_phenotype_by_region":
            if "region" not in request.params:
                raise ValueError("Missing required parameter: region")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_phenotype_by_region(
                request.params.get("region"),
                request.params.get("species")
            )
            
        # Cross references
        elif request.method == "get_xrefs_by_symbol":
            if "symbol" not in request.params:
                raise ValueError("Missing required parameter: symbol")
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_xrefs_by_symbol(
                request.params.get("symbol"),
                request.params.get("species")
            )
            
        elif request.method == "get_xrefs_by_id":
            if "id" not in request.params:
                raise ValueError("Missing required parameter: id")
            result = ensembl.get_xrefs_by_id(request.params.get("id"))
            
        # Information
        elif request.method == "get_species_info":
            result = ensembl.get_species_info()
            
        elif request.method == "get_assembly_info":
            if "species" not in request.params:
                raise ValueError("Missing required parameter: species")
            result = ensembl.get_assembly_info(request.params.get("species"))
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
            
        return MCPResponse(result=result)
    except Exception as e:
        return MCPResponse(result=None, error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)