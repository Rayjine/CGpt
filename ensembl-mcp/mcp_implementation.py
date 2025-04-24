import requests
import json
from typing import Dict, Any, List, Optional

class EnsemblMCPServer:
    """
    An implementation of the Model Context Protocol server for Ensembl API
    """
    def __init__(self):
        self.base_url = "https://rest.ensembl.org"
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        
    def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP request and return the result"""
        handler_map = {
            # Current handlers
            "lookup_gene": self._lookup_gene,
            "lookup_gene_by_symbol": self._lookup_gene_by_symbol,
            "get_gene_sequence": self._get_gene_sequence,
            "get_variant_info": self._get_variant_info,
            "search_genes": self._search_genes,
            
            # Sequences
            "get_sequence_by_id": self._get_sequence_by_id,
            "get_sequence_by_region": self._get_sequence_by_region,
            
            # Comparative genomics
            "get_gene_tree": self._get_gene_tree,
            "get_homology": self._get_homology,
            "get_genomic_alignment": self._get_genomic_alignment,
            
            # Variants and phenotypes
            "get_variant_consequences": self._get_variant_consequences,
            "get_phenotype_by_gene": self._get_phenotype_by_gene,
            "get_phenotype_by_region": self._get_phenotype_by_region,
            
            # Cross references
            "get_xrefs_by_symbol": self._get_xrefs_by_symbol,
            "get_xrefs_by_id": self._get_xrefs_by_id,
            
            # Information
            "get_species_info": self._get_species_info,
            "get_assembly_info": self._get_assembly_info,
        }
        
        if method not in handler_map:
            return {"error": f"Unknown method: {method}"}
            
        try:
            result = handler_map[method](params)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    # Existing methods
    def _lookup_gene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        gene_id = params.get("gene_id")
        species = params.get("species", "human")
        
        if not gene_id:
            raise ValueError("Missing required parameter: gene_id")
            
        endpoint = f"{self.base_url}/lookup/id/{gene_id}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
        
    def _lookup_gene_by_symbol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        symbol = params.get("symbol")
        species = params.get("species", "human")
        
        if not symbol:
            raise ValueError("Missing required parameter: symbol")
            
        endpoint = f"{self.base_url}/lookup/symbol/{species}/{symbol}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    # Implement remaining handlers from the original list
    def _get_gene_sequence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        gene_id = params.get("gene_id")
        
        if not gene_id:
            raise ValueError("Missing required parameter: gene_id")
            
        endpoint = f"{self.base_url}/sequence/id/{gene_id}"
        response = requests.get(endpoint, headers={"Content-Type": "application/json", "Accept": "application/json"})
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_variant_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        variant_id = params.get("variant_id")
        species = params.get("species", "human")
        
        if not variant_id:
            raise ValueError("Missing required parameter: variant_id")
            
        endpoint = f"{self.base_url}/variation/{species}/{variant_id}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _search_genes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query")
        species = params.get("species", "human")
        
        if not query:
            raise ValueError("Missing required parameter: query")
            
        endpoint = f"{self.base_url}/xrefs/symbol/{species}/{query}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    # New method implementations
    
    # Sequences
    def _get_sequence_by_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        id = params.get("id")
        mask = params.get("mask", None)
        expand_3prime = params.get("expand_3prime", None)
        expand_5prime = params.get("expand_5prime", None)
        
        if not id:
            raise ValueError("Missing required parameter: id")
        
        endpoint = f"{self.base_url}/sequence/id/{id}"
        query_params = {}
        
        if mask:
            query_params["mask"] = mask
        if expand_3prime:
            query_params["expand_3prime"] = expand_3prime
        if expand_5prime:
            query_params["expand_5prime"] = expand_5prime
            
        response = requests.get(endpoint, params=query_params, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_sequence_by_region(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        region = params.get("region")
        
        if not region:
            raise ValueError("Missing required parameter: region")
            
        endpoint = f"{self.base_url}/sequence/region/{species}/{region}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    # Comparative genomics
    def _get_gene_tree(self, params: Dict[str, Any]) -> Dict[str, Any]:
        id = params.get("id")
        
        if not id:
            raise ValueError("Missing required parameter: id")
            
        endpoint = f"{self.base_url}/genetree/id/{id}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_homology(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        id = params.get("id")
        
        if not id:
            raise ValueError("Missing required parameter: id")
            
        endpoint = f"{self.base_url}/homology/id/{species}/{id}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_genomic_alignment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        region = params.get("region")
        
        if not region:
            raise ValueError("Missing required parameter: region")
            
        endpoint = f"{self.base_url}/alignment/region/{species}/{region}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    # Variants and phenotypes
    def _get_variant_consequences(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        variant_id = params.get("variant_id")
        
        if not variant_id:
            raise ValueError("Missing required parameter: variant_id")
            
        endpoint = f"{self.base_url}/vep/{species}/id/{variant_id}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_phenotype_by_gene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        gene = params.get("gene")
        
        if not gene:
            raise ValueError("Missing required parameter: gene")
            
        endpoint = f"{self.base_url}/phenotype/gene/{species}/{gene}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_phenotype_by_region(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        region = params.get("region")
        
        if not region:
            raise ValueError("Missing required parameter: region")
            
        endpoint = f"{self.base_url}/phenotype/region/{species}/{region}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    # Cross references
    def _get_xrefs_by_symbol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        symbol = params.get("symbol")
        
        if not symbol:
            raise ValueError("Missing required parameter: symbol")
            
        endpoint = f"{self.base_url}/xrefs/symbol/{species}/{symbol}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_xrefs_by_id(self, params: Dict[str, Any]) -> Dict[str, Any]:
        id = params.get("id")
        
        if not id:
            raise ValueError("Missing required parameter: id")
            
        endpoint = f"{self.base_url}/xrefs/id/{id}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    # Information
    def _get_species_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/info/species"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    def _get_assembly_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        species = params.get("species", "human")
        
        endpoint = f"{self.base_url}/info/assembly/{species}"
        response = requests.get(endpoint, headers=self.headers)
        
        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()

# MCP server factory function
def create_ensembl_mcp_server():
    return EnsemblMCPServer()