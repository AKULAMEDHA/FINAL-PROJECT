# Runs the two BLAST searches (needs NCBI BLAST+ installed)
import subprocess


def run_blast(query, database_fasta, output):
    subprocess.run(["makeblastdb", "-in", database_fasta, "-dbtype", "prot"])
    subprocess.run(["blastp", "-query", query, "-db", database_fasta,
                    "-outfmt", "6", "-evalue", "1e-5", "-out", output])


run_blast("data/species_A.fasta", "data/species_B.fasta", "data/A_vs_B.tsv")
run_blast("data/species_B.fasta", "data/species_A.fasta", "data/B_vs_A.tsv")
print("BLAST done. Now run: python orthologs.py")
