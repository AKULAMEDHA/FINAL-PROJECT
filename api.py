from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from orthologs import find_orthologs, parse_blast, save_results

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_A_VS_B = DATA_DIR / "A_vs_B.tsv"
DEFAULT_B_VS_A = DATA_DIR / "B_vs_A.tsv"
DEFAULT_OUTPUT = BASE_DIR / "orthologs.csv"

app = FastAPI(
    title="Ortholog Finder API",
    description="API for finding reciprocal-best-hit orthologs from BLAST results.",
    version="1.0.0",
)

# Allows a browser frontend running on another port (for example localhost:3000)
# to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrthologRequest(BaseModel):
    a_vs_b: str = Field(default="data/A_vs_B.tsv")
    b_vs_a: str = Field(default="data/B_vs_A.tsv")
    max_evalue: float = Field(default=1e-5, gt=0)


def resolve_project_path(path: str) -> Path:
    """Resolve a path while keeping API file access inside the project."""
    candidate = (BASE_DIR / path).resolve()
    if BASE_DIR not in candidate.parents and candidate != BASE_DIR:
        raise HTTPException(status_code=400, detail="File path must be inside the project directory")
    return candidate


def calculate_orthologs(a_path: Path, b_path: Path, max_evalue: float):
    if not a_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {a_path.name}")
    if not b_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {b_path.name}")

    a_vs_b = parse_blast(str(a_path), max_evalue=max_evalue)
    b_vs_a = parse_blast(str(b_path), max_evalue=max_evalue)
    return find_orthologs(a_vs_b, b_vs_a)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ortholog-finder-api"}


@app.get("/api/orthologs")
def get_orthologs(max_evalue: float = 1e-5):
    """Find orthologs using the bundled sample BLAST results."""
    orthologs = calculate_orthologs(DEFAULT_A_VS_B, DEFAULT_B_VS_A, max_evalue)
    return {
        "count": len(orthologs),
        "orthologs": [
            {
                "gene_A": gene_a,
                "gene_B": gene_b,
                "identity": identity,
                "evalue": evalue,
            }
            for gene_a, gene_b, identity, evalue in orthologs
        ],
    }


@app.post("/api/find-orthologs")
def find_orthologs_api(request: OrthologRequest):
    """Run the ortholog finder on two BLAST tabular result files."""
    a_path = resolve_project_path(request.a_vs_b)
    b_path = resolve_project_path(request.b_vs_a)

    orthologs = calculate_orthologs(a_path, b_path, request.max_evalue)
    save_results(orthologs, str(DEFAULT_OUTPUT))

    return {
        "count": len(orthologs),
        "output_file": "orthologs.csv",
        "orthologs": [
            {
                "gene_A": gene_a,
                "gene_B": gene_b,
                "identity": identity,
                "evalue": evalue,
            }
            for gene_a, gene_b, identity, evalue in orthologs
        ],
    }
