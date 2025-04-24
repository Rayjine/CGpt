import requests
import json

class EnsemblAPI:
    def __init__(self):
        self.base_url = "https://rest.ensembl.org"
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def lookup_gene(self, gene_id, species):
        endpoint = f"{self.base_url}/lookup/id/{gene_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
        
    def lookup_gene_by_symbol(self, symbol, species):
        endpoint = f"{self.base_url}/lookup/symbol/{species}/{symbol}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
        
    def get_gene_sequence(self, gene_id):
        endpoint = f"{self.base_url}/sequence/id/{gene_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
        
    def get_variant_info(self, variant_id, species):
        endpoint = f"{self.base_url}/variation/{species}/{variant_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
        
    def search_genes(self, query, species):
        endpoint = f"{self.base_url}/xrefs/symbol/{species}/{query}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    # New methods to align with MCP implementation
    
    # Sequences
    def get_sequence_by_id(self, id, species, mask=None, expand_3prime=None, expand_5prime=None):
        endpoint = f"{self.base_url}/sequence/id/{id}"
        query_params = {}
        
        if mask:
            query_params["mask"] = mask
        if expand_3prime:
            query_params["expand_3prime"] = expand_3prime
        if expand_5prime:
            query_params["expand_5prime"] = expand_5prime
            
        response = requests.get(endpoint, params=query_params, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_sequence_by_region(self, region, species):
        endpoint = f"{self.base_url}/sequence/region/{species}/{region}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    # Comparative genomics
    def get_gene_tree(self, id):
        endpoint = f"{self.base_url}/genetree/id/{id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_homology(self, id, species):
        endpoint = f"{self.base_url}/homology/id/{species}/{id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_genomic_alignment(self, region, species):
        endpoint = f"{self.base_url}/alignment/region/{species}/{region}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    # Variants and phenotypes
    def get_variant_consequences(self, variant_id, species):
        endpoint = f"{self.base_url}/vep/{species}/id/{variant_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_phenotype_by_gene(self, gene, species):
        endpoint = f"{self.base_url}/phenotype/gene/{species}/{gene}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_phenotype_by_region(self, region, species):
        endpoint = f"{self.base_url}/phenotype/region/{species}/{region}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    # Cross references
    def get_xrefs_by_symbol(self, symbol, species):
        endpoint = f"{self.base_url}/xrefs/symbol/{species}/{symbol}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_xrefs_by_id(self, id):
        endpoint = f"{self.base_url}/xrefs/id/{id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    # Information
    def get_species_info(self):
        endpoint = f"{self.base_url}/info/species"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}
    
    def get_assembly_info(self, species):
        endpoint = f"{self.base_url}/info/assembly/{species}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json() if response.ok else {"error": response.text}