import numpy as np
import pandas as pd
from pathlib import Path
import gzip
import json
import logging
import shutil


# --------------------------------------------------
# CONFIG (match your pipeline filters)
# --------------------------------------------------
DISEASE_NAME = "alzheimer disease"
DISEASE_ID = "DOID:10652"
ORGANISM = "Homo sapiens"
TISSUE = "hippocampus"
CELL = "microglia"


# --------------------------------------------------
# Expression generator
# --------------------------------------------------
def generate_expression(n_samples, n_features):

    np.random.seed(42)

    condition = np.random.choice(["control", "disease"], size=n_samples)
    batch = np.random.choice(["batch_1", "batch_2"], size=n_samples)

    expr = np.random.normal(0, 1, (n_samples, n_features))

    # biological signal
    expr[condition == "disease", :50] += 2

    # batch effect
    expr[batch == "batch_2", 50:100] += 1.5

    return expr, condition, batch


# --------------------------------------------------
# Study-level metadata (for discovery)
# --------------------------------------------------
def create_study_metadata(study_id, repo, n_samples):

    return {
        "study_id": study_id,
        "repository": repo,

        "disease_name": DISEASE_NAME,
        "disease_ontology_id": DISEASE_ID,

        "publication_year": 2024,

        "tissue_type": TISSUE,
        "cell_type": CELL,

        "organism": ORGANISM,

        "sample_size": n_samples
    }


# --------------------------------------------------
# GEO generator (geneCounts format)
# --------------------------------------------------
def generate_geo_study(study_id, base):

    logging.info(f"📊 Generating GEO study: {study_id}")

    n_samples = 20
    n_features = 500

    expr, condition, batch = generate_expression(n_samples, n_features)

    study_path = base / "geo" / study_id
    study_path.mkdir(parents=True, exist_ok=True)

    genes = [f"ENSG{i:06d}" for i in range(n_features)]

    sample_meta = []

    for i in range(n_samples):

        sample_id = f"GSM_{study_id}_{i}"

        df = pd.DataFrame({
            "GeneID": genes,
            "Counts": expr[i]
        })

        file_path = study_path / f"{sample_id}_geneCounts.txt.gz"

        with gzip.open(file_path, "wt") as f:
            df.to_csv(f, sep="\t", index=False)

        sample_meta.append({
            "sample_id": sample_id,
            "condition": condition[i],
            "batch": batch[i],
            "study_id": study_id,
            "repository": "geo",
            "omics": "rna"
        })

    # save sample metadata
    pd.DataFrame(sample_meta).to_csv(study_path / "metadata.csv", index=False)

    # save study metadata
    with open(study_path / "metadata.json", "w") as f:
        json.dump(create_study_metadata(study_id, "geo", n_samples), f, indent=2)


# --------------------------------------------------
# PRIDE generator (matrix format)
# --------------------------------------------------
def generate_pride_study(study_id, base):

    logging.info(f"🧪 Generating PRIDE study: {study_id}")

    n_samples = 20
    n_features = 300

    expr, condition, batch = generate_expression(n_samples, n_features)

    study_path = base / "pride" / study_id
    study_path.mkdir(parents=True, exist_ok=True)

    proteins = [f"P{i:05d}" for i in range(n_features)]
    samples = [f"{study_id}_S{i}" for i in range(n_samples)]

    expression = pd.DataFrame(expr, index=samples, columns=proteins)

    metadata = pd.DataFrame({
        "sample_id": samples,
        "condition": condition,
        "batch": batch,
        "study_id": study_id,
        "repository": "pride",
        "omics": "proteomics"
    })

    metadata.to_csv(study_path / "metadata.csv", index=False)
    expression.to_csv(study_path / "expression.csv")

    with open(study_path / "metadata.json", "w") as f:
        json.dump(create_study_metadata(study_id, "pride", n_samples), f, indent=2)


# --------------------------------------------------
# MASTER GENERATOR
# --------------------------------------------------
def generate_all():

    base = Path(__file__).resolve().parents[1] / "data" / "bronze"

    logging.info("🚀 Generating full synthetic dataset...")

    # clean old data
    if base.exists():
        shutil.rmtree(base)

    base.mkdir(parents=True, exist_ok=True)

    # GEO (3 studies)
    for i in range(3):
        generate_geo_study(f"GSE_SYNTH_{i}", base)

    # PRIDE (1 study)
    generate_pride_study("PRIDE_SYNTH_0", base)

    logging.info("✅ Synthetic data generation complete")


# --------------------------------------------------
# RUNNER
# --------------------------------------------------
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    print("🚀 Generating synthetic GEO + PRIDE datasets...")

    generate_all()

    print("✅ Done! Check data/bronze/")