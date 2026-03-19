import pandas as pd
import logging
from pathlib import Path

def read_delta_tables(selected_studies):

    logging.info("Reading delta tables...")
    base_path = Path("data/bronze/delta_table")

    data = {}
    for repo, studies in selected_studies.items():
        for study in studies:
            study_id = study["study_id"]
            path = base_path / repo / study_id

            metadata = pd.read_parquet(path / "metadata.parquet")
            expression = pd.read_parquet(path / "expression.parquet")

            key = f"{repo}_{study_id}"
            data[key] = {"metadata": metadata, "expression": expression}
            logging.info(f"Read {key} with {len(metadata)} metadata records and expression data of shape {expression.shape}.")

    return data