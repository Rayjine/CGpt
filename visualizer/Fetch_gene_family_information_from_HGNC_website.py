# Fetch selected information for gene family HLA from HGNC

import requests
import pandas as pd
import time

# Step 1: Get HGNC family members for HLA
HGNC_FAMILY_NAME = "HLA"  # Search term
hgnc_group_url = f"https://rest.genenames.org/fetch/genegroup_tag/{HGNC_FAMILY_NAME}"
headers = {'Accept': 'application/json'}

print("Fetching HLA gene family from HGNC...")
response = requests.get(hgnc_group_url, headers=headers)
if response.status_code != 200:
    raise Exception(f"HGNC family fetch failed: {response.status_code} - {response.text}")

results = response.json()["response"]["docs"]

if not results:
    raise ValueError("No results found for the HLA family. Try using a more specific tag or check spelling.")

# Step 2: Collect all approved gene symbols
gene_symbols = [gene['symbol'] for gene in results]
print(f"Found {len(gene_symbols)} genes in the HLA family.")

# Step 3: Query Ensembl for gene coordinates
ensembl_url = "https://rest.ensembl.org/lookup/symbol/homo_sapiens/{}?content-type=application/json"
gene_locations = []

for symbol in gene_symbols:
    try:
        response = requests.get(ensembl_url.format(symbol))
        if response.status_code == 200:
            data = response.json()
            gene_locations.append({
                "Gene": symbol,
                "Chromosome": data.get("seq_region_name"),
                "Start": data.get("start"),
                "End": data.get("end"),
                "Strand": data.get("strand")
            })
        else:
            print(f"Failed to fetch Ensembl data for {symbol} (status {response.status_code})")
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    time.sleep(0.2)

# Save results
df = pd.DataFrame(gene_locations)
df.to_csv("hla_gene_coordinates_full_auto.csv", index=False)
print("✅ Done! Saved to hla_gene_coordinates_full_auto.csv")
