# Build gene function out of nucleotide sequence

## Step 1 : retrieve peptide sequence from gene seq

## Step 2 : use SANSPANZ to retrieve gene function in GO terms

* Followed [tutorial](http://ekhidna2.biocenter.helsinki.fi/sanspanz/)

* Install dependencies from `pyproject.toml`:
```
uv init
uv sync
```


* Run `ppython main.py -i test_data/test_pept.fasta -o test_results -s "Canis lupus familiaris"` as example