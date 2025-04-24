# setup data with python scripts
# cd visualizer
uv run scripts/split_gff.py \
    data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/genomic.gff \
    -t gene
uv run scripts/create_chromosome_dbs.py \
    data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/chromosomes \
    NC_051805.1.gff
uv run scripts/sequence.py \
    --fasta data/ncbi_dataset/ncbi_dataset/data/GCF_014441545.1/GCF_014441545.1_ROS_Cfam_1.0_genomic.fna \
    --chromosome NC_051805.1 \
    --output cgpt-visualizer-website/src/data/chromosome_data.json

# start the frontend
cd cgpt-visualizer-website
npm install
npm start
