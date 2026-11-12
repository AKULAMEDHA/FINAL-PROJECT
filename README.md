# Ortholog Finder using Reciprocal BLAST (Backend)

Anushree Sharma (SE25UBIT044)
My part: Ortholog finder logic, reciprocal BLAST workflow, BLAST parsing, backend Python code

## Run
1. (Optional, needs BLAST+) `python run_blast.py`
2. `python orthologs.py`  -> prints orthologs and saves `orthologs.csv`

Sample BLAST results are already in `data/`, so step 2 works without BLAST.

## API

The project now includes a FastAPI backend in `api.py`.

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the API

From the `ortholog_finder` folder:

```bash
uvicorn api:app --reload
```

The API will run at `http://127.0.0.1:8000`.

### Endpoints

- `GET /api/health` — checks that the API is running.
- `GET /api/orthologs` — runs the ortholog finder using the bundled BLAST result files.
- `POST /api/find-orthologs` — runs the ortholog finder using the BLAST files specified in the request body and saves `orthologs.csv`.
- `GET /docs` — interactive Swagger API documentation.

Example request:

```json
{
  "a_vs_b": "data/A_vs_B.tsv",
  "b_vs_a": "data/B_vs_A.tsv",
  "max_evalue": 0.00001
}
```
