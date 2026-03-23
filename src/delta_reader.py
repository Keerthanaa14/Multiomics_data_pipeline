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

            # -----------------------------
            # Read files
            # -----------------------------
            metadata = pd.read_parquet(path / "metadata.parquet")
            expression = pd.read_parquet(path / "expression.parquet")

            # -----------------------------
            # Validate metadata
            # -----------------------------
            if "sample_id" not in metadata.columns:
                raise ValueError(f"{study_id}: metadata missing 'sample_id' column")

            metadata["sample_id"] = metadata["sample_id"].astype(str)

            # -----------------------------
            #  ALWAYS enforce alignment
            # -----------------------------
            if len(expression) != len(metadata):
                raise ValueError(
                    f"{study_id}:  length mismatch "
                    f"(expression={len(expression)}, metadata={len(metadata)})"
                )

            # Force correct sample IDs
            expression.index = metadata["sample_id"].values

            # -----------------------------
            # Final validation
            # -----------------------------
            if not all(expression.index == metadata["sample_id"].values):
                raise ValueError(f"{study_id}:  index alignment failed")

            # -----------------------------
            # Store
            # -----------------------------
            key = f"{repo}_{study_id}"

            data[key] = {
                "metadata": metadata,
                "expression": expression
            }

            logging.info(
                f"Read {key} → {len(metadata)} samples, {expression.shape[1]} features"
            )

    if len(data) == 0:
        raise ValueError("No datasets loaded from delta tables")

    return data