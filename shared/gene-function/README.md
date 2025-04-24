# Build gene function out of nucleotide sequence

1. Clone the repo, then `cd shared/gene-function`.

2. Setup the environment using uv package and activate environment
```
uv sync
source .venv/bin/activate
```

## 1. Map protein id to gene names

/!\ Warning : computationally intensive.
Results saved under `res/dog_genome_dict.csv`.

1. Download genome file `.fna` from NCBI database [here](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_014441545.1/) and protein peptide sequences file `.pep.all.fna` and gff file `.gff3` from Ensembl database [there](https://ftp.ensembl.org/pub/release-113/gff3/canis_lupus_familiaris/).

2. Launch the script. Example with genome from Canis Lupus Familiaris
```
cd utils
python build_lookuptable.py --dna_file path/to/your/file/GCF_014441545.1_ROS_Cfam_1.0_genomic.fna --gff_file path/to/file/Canis_lupus_familiaris.ROS_Cfam_1.0.113.chr.gff3 --protein_file path/to/file/Canis_lupus_familiaris.ROS_Cfam_1.0.pep.all.fa --protein_file path/to/output
```

## 2. Retrieve gene function in GO terms

Find most probable gene functions for each protein coding gene based on peptide fasta file for a given chromosome. 

## Acknowledgments

I followed this [tutorial](http://ekhidna2.biocenter.helsinki.fi/sanspanz/).
Toronen P, Holm L (2022) PANNZER - a practical tool for protein function prediction. Protein Science 31, 118– 128

## Use PANNZER

Example run `python main.py -i test/test_data/test_pept.fasta -o results`
Write your result in `results/annotations_filtered.out`. 
It might lead to some not identified errors as some proteins might not be processed by the PANNZER tool. 

# TODO

- [] add tests
- [] handle missing values
- [] extend to several chromosomes

