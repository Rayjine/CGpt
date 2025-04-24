import unittest
from ensembl_mcp_server.api.ensembl import EnsemblAPI

class TestEnsemblAPI(unittest.TestCase):
    def setUp(self):
        self.api = EnsemblAPI()
        
    def test_lookup_gene_by_symbol(self):
        result = self.api.lookup_gene_by_symbol("BRCA1")
        self.assertIn("id", result)
        self.assertIn("display_name", result)
        
    def test_lookup_nonexistent_gene(self):
        result = self.api.lookup_gene_by_symbol("NONEXISTENTGENE123456789")
        self.assertIn("error", result)
        
if __name__ == "__main__":
    unittest.main()