import logging
from pathlib import Path
import pandas as pd

from utils.build_expression_matrix import build_expression_matrix


# --------------------------------------------------
# HELPER: ALIGN METADATA + EXPRESSION
# --------------------------------------------------
def align_expression_metadata(expression, metadata, study_id):
    """
    Ensure expression.index == metadata.sample_id

    Strategy:
    1. If lengths match → force alignment (safe for row-wise aligned data)
    2. Else → try intersection
    3. Fail loudly if still no match
    """

    # Ensure string types
    metadata["sample_id"] = metadata["sample_id"].astype(str)
    expression.index = expression.index.astype(str)

    # --------------------------------------------------
    # CASE 1: Perfect row-wise alignment (most common)
    # --------------------------------------------------
    if len(metadata) == len(expression):
        logging.info(f"{study_id}: Forcing index alignment (row-wise match)")
        expression.index = metadata["sample_id"].values

        # Validate
        if not all(expression.index == metadata["sample_id"].values):
            raise ValueError(f"{study_id}: Alignment failed after assignment")

        return expression, metadata

    # --------------------------------------------------
    # CASE 2: Try intersection (real-world datasets)
    # --------------------------------------------------
    logging.warning(f"{study_id}:  Length mismatch → attempting intersection")

    metadata = metadata.set_index("sample_id")

    common = metadata.index.intersection(expression.index)

    if len(common) == 0:
        raise ValueError(
            f"{study_id}: ❌ No matching samples between metadata and expression\n"
            f"expr example: {list(expression.index[:5])}\n"
            f"meta example: {list(metadata.index[:5])}"
        )

    logging.info(f"{study_id}:  Matched {len(common)} samples via intersection")

    metadata = metadata.loc[common]
    expression = expression.loc[common]

    metadata = metadata.reset_index()

    return expression, metadata


# --------------------------------------------------
# GEO LOADER (geneCounts → matrix)
# --------------------------------------------------
def load_geo_dataset(study_id, base_path):

    logging.info(f"Loading GEO dataset: {study_id}")

    study_path = base_path / "geo" / study_id

    # -----------------------------
    # Expression (build from geneCounts)
    # -----------------------------
    expression = build_expression_matrix(study_path)

    # -----------------------------
    # Metadata (sample-level)
    # -----------------------------
    metadata = pd.read_csv(study_path / "metadata.csv")

    if "sample_id" not in metadata.columns:
        raise ValueError(f"{study_id}: metadata missing 'sample_id' column")

    # -----------------------------
    # Align
    # -----------------------------
    expression, metadata = align_expression_metadata(
        expression, metadata, study_id
    )

    logging.info(
        f"{study_id}: Final aligned shape → {expression.shape[0]} samples, {expression.shape[1]} features"
    )

    return {
        "metadata": metadata,
        "expression": expression
    }


# --------------------------------------------------
# PRIDE LOADER (matrix already exists)
# --------------------------------------------------
def load_pride_dataset(study_id, base_path):

    logging.info(f"Loading PRIDE dataset: {study_id}")

    study_path = base_path / "pride" / study_id

    # -----------------------------
    # Expression
    # -----------------------------
    expression = pd.read_csv(study_path / "expression.csv", index_col=0)

    # -----------------------------
    # Metadata
    # -----------------------------
    metadata = pd.read_csv(study_path / "metadata.csv")

    if "sample_id" not in metadata.columns:
        raise ValueError(f"{study_id}: metadata missing 'sample_id' column")

    # -----------------------------
    # Align
    # -----------------------------
    expression, metadata = align_expression_metadata(
        expression, metadata, study_id
    )

    logging.info(
        f"{study_id}: Final aligned shape → {expression.shape[0]} samples, {expression.shape[1]} features"
    )

    return {
        "metadata": metadata,
        "expression": expression
    }


# --------------------------------------------------
# MAIN INGESTION
# --------------------------------------------------
def run_ingestion(selected):

    logging.info("🚀 Running ingestion...")

    base_path = Path("data/bronze")

    data = {}

    for repo, studies in selected.items():

        for study in studies:

            study_id = study["study_id"]

            try:
                if repo == "geo":
                    dataset = load_geo_dataset(study_id, base_path)

                elif repo == "pride":
                    dataset = load_pride_dataset(study_id, base_path)

                else:
                    logging.warning(f"Unknown repository: {repo}")
                    continue

                data[study_id] = dataset

                logging.info(
                    f"✅ Loaded {study_id}: {dataset['expression'].shape}"
                )

            except Exception as e:
                logging.error(f"Failed {study_id}: {e}")

    if len(data) == 0:
        raise ValueError("No datasets successfully ingested")

    return data