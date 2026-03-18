from importlib import metadata
import pandas as pd
from pathlib import Path
import logging

def load_geo_dataset(name,base_path):
    """
    Load GEO dataset metadata from a TSV file.
    """
    metadata_path = Path(base_path / f"{name}_metadata.txt", sep="\t")
    expression = pd.read_csv (base_path / f"{name}_raw.csv", sep="\t")

    metadata["study_id"] = name
    metadata["data_type"] = "RNA"
    metadata["repository"] = "GEO"

    return {"metadata": metadata, "expression": expression}

def load_pride_dataset(name,base_path):
    """
    Load PRIDE dataset metadata from a TSV file.
    """
    metadata_path = Path(base_path / f"{name}_metadata.json")
    expression = pd.read_csv (base_path / f"{name}_raw.csv")
    metadata["study_id"] = name
    metadata["data_type"] = "Proteomics"
    metadata["repository"] = "PRIDE"

    return {"metadata": metadata, "expression": expression}

def run_ingestion(selected_studies):
    base_path = Path("data/raw")
    data = {}

    for repo, studies in selected_studies.items():
        for study in studies:
            study_id = study["study_id"]

            logging.info(f"Loading {study_id} from {repo}...")

            if repo == "geo":
                data[study_id] = load_geo_dataset(study_id, base_path)
            elif repo == "pride":
                data[study_id] = load_pride_dataset(study_id, base_path)

        logging.info(f"Completed loading {len(studies)} studies from {repo}.")
        return data