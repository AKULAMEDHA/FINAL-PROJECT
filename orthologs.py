# Ortholog Finder using Reciprocal BLAST
# Finds reciprocal best hits (RBH) between species A and species B


def parse_blast(path, max_evalue=1e-5):
    # Reads BLAST tabular output (-outfmt 6) and keeps the best hit per query
    best = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue
            fields = line.strip().split("\t")
            query = fields[0]
            subject = fields[1]
            identity = float(fields[2])
            evalue = float(fields[10])
            bitscore = float(fields[11])

            if evalue > max_evalue:
                continue
            if query not in best or bitscore > best[query]["bitscore"]:
                best[query] = {"hit": subject, "identity": identity,
                               "evalue": evalue, "bitscore": bitscore}
    return best


def find_orthologs(a_vs_b, b_vs_a):
    # A gene pair is an ortholog if each is the other's best hit
    orthologs = []
    for gene_a, info in a_vs_b.items():
        gene_b = info["hit"]
        if gene_b in b_vs_a and b_vs_a[gene_b]["hit"] == gene_a:
            orthologs.append((gene_a, gene_b, info["identity"], info["evalue"]))
    return orthologs


def save_results(orthologs, path):
    with open(path, "w") as f:
        f.write("gene_A,gene_B,identity,evalue\n")
        for gene_a, gene_b, identity, evalue in orthologs:
            f.write(f"{gene_a},{gene_b},{identity},{evalue}\n")


if __name__ == "__main__":
    a_vs_b = parse_blast("data/A_vs_B.tsv")
    b_vs_a = parse_blast("data/B_vs_A.tsv")
    orthologs = find_orthologs(a_vs_b, b_vs_a)

    print("Orthologs found:", len(orthologs))
    for gene_a, gene_b, identity, evalue in orthologs:
        print(gene_a, "<->", gene_b, "| identity:", identity, "| evalue:", evalue)

    save_results(orthologs, "orthologs.csv")
    print("Saved to orthologs.csv")
