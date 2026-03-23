import logging
import pandas as pd


def align_features(data, min_feature_overlap=0.5):

    logging.info("Aligning features across datasets...")

    if len(data) == 0:
        logging.warning("No datasets to align")
        return data

    # -----------------------------
    # Collect feature sets
    # -----------------------------
    feature_sets = {}
    for name, dataset in data.items():

        expr = dataset["expression"]

        if expr is None or expr.shape[0] == 0:
            logging.warning(f"{name}: empty expression → skipping")
            continue

        feature_sets[name] = set(expr.columns)

    if len(feature_sets) < 2:
        logging.warning("Only one dataset → skipping alignment")
        return data

    # -----------------------------
    # Compute global feature pool
    # -----------------------------
    all_features = list(set.union(*feature_sets.values()))

    logging.info(f"Total unique features across datasets: {len(all_features)}")

    aligned = {}

    # -----------------------------
    # Align each dataset
    # -----------------------------
    for name, dataset in data.items():

        expr = dataset["expression"]
        meta = dataset["metadata"]

        current_features = set(expr.columns)

        overlap = len(current_features.intersection(all_features)) / len(all_features)

        logging.info(f"{name}: feature overlap = {overlap:.2f}")

        # -----------------------------
        # Skip very poor datasets
        # -----------------------------
        if overlap < min_feature_overlap:
            logging.warning(f"{name}: too few overlapping features → dropped")
            continue

        # -----------------------------
        # Reindex features (IMPORTANT)
        # -----------------------------
        expr_aligned = expr.reindex(columns=all_features)

        # Fill missing values
        expr_aligned = expr_aligned.fillna(0)

        aligned[name] = {
            "metadata": meta,
            "expression": expr_aligned
        }

        logging.info(f"{name}: aligned → {expr_aligned.shape}")

    if len(aligned) == 0:
        raise ValueError("No datasets left after feature alignment")

    logging.info(f"Final datasets after alignment: {list(aligned.keys())}")

    return aligned