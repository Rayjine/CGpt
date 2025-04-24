from Bio import SeqIO

for seq_record in SeqIO.parse(
    "data/ncbi_dataset/data/GCF_014441545.1/GCF_014441545.1_ROS_Cfam_1.0_genomic.fna",
    "fasta",
):
    print(seq_record.id)
    print(repr(seq_record.seq))
    print(len(seq_record))
