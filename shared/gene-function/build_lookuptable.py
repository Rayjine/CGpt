from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqUtils import gc_fraction
from BCBio import GFF
import re
import os
import pandas as pd
import numpy as np
from unipressed import IdMappingClient
import time

def gene_dict(dna_file,gff_file,protein_file=None):
    genome_dict = {'Gene_name':[],
                   'Ensemble_id':[],
                   "Protein_ensembl_id":[],
                   "Locus":[]} 

    # Load genome records (required by GFF.parse)
    genome_records = SeqIO.to_dict(SeqIO.parse(dna_file, "fasta"))

    # Clean up chromosome names (optional)
    cleaned_records = {}
    
    for key, record in genome_records.items():
        desc = record.name
        match = re.search(r'NC_(\w+)', desc)
        if match:
            chr_label = re.search(r'chromosome (\w+)', record.description).group(1)
            cleaned_records[chr_label] = record  # e.g., 'chr1', 'chrX'
        else:
            # Scaffold or unplaced: ignore
            continue

    # Parse GFF and extract mapping
    with open(gff_file) as gff_handle:
        for rec in GFF.parse(gff_handle, base_dict=cleaned_records):
            for feature in rec.features:
                if feature.type == "gene":
                    gene_name = feature.qualifiers.get("Name", [""])[0]
                    gene_id = feature.qualifiers.get("gene_id", [""])[0]
                    start, end, strand = feature.location.start, feature.location.end, feature.location.strand
                    chrom = re.search(r'chromosome (\w+)', rec.description).group(1)
                    
                    if gene_name:  # only store if gene name exists
                        genome_dict['Gene_name'].append(gene_name)
                        genome_dict['Ensemble_id'].append(gene_id)
                        genome_dict['Locus'].append(f'{chrom}:{start}:{end}:{strand}')
                        
    if protein_file:
        protein_ensembl_ids = [" "] * len(genome_dict['Ensemble_id'])
        for record in SeqIO.parse(protein_file, "fasta"):
            protein_gene_id = record.description.split(" ")[3].split(":")[1].split(".")[0]
            protein_id = record.id
            
            if protein_gene_id in genome_dict['Ensemble_id']:
                index = genome_dict['Ensemble_id'].index(protein_gene_id)
                protein_ensembl_ids[index] = protein_id
                
        genome_dict['Protein_ensembl_id'] = protein_ensembl_ids
        
    Uniprot_ids = [" "] * len(genome_dict['Gene_name'])
    for gene in genome_dict['Gene_name']:
        request = IdMappingClient.submit(
        source="GeneCards", dest="UniProtKB", ids=[gene]
        )
        time.sleep(1.0)
        result = pd.DataFrame(list(request.each_result()))
        
        idx = genome_dict['Gene_name'].index(gene)
        if not result.empty:
            Uniprot_ids[idx] = result['to'][0]
        else:
            Uniprot_ids[idx] = "Not Found"
    genome_dict['Uniprot_id'] = Uniprot_ids
                        
    return pd.DataFrame(genome_dict)