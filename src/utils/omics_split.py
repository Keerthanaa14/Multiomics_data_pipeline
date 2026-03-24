import logging


def normalize_omics(value):

    if value is None:
        return "unknown"

    value = str(value).lower()

    # -----------------------------
    # RNA mapping
    # -----------------------------
    if any(k in value for k in [
        "rna", "transcript", "gene", "expression"
    ]):
        return "rna"

    # -----------------------------
    # Proteomics mapping
    # -----------------------------
    if any(k in value for k in [
        "protein", "proteome", "pride"
    ]):
        return "proteomics"

    return "unknown"


def split_by_omics(data):

    logging.info("Splitting datasets by omics type...")

    groups = {
        "rna": {},
        "proteomics": {}
    }

    for name, dataset in data.items():

        meta = dataset.get("metadata")

        if meta is None or len(meta) == 0:
            logging.warning(f"{name}: missing metadata → skipping")
            continue

        # -----------------------------
        # Detect omics
        # -----------------------------
        omics = None

        if "data_type" in meta.columns:
            omics = normalize_omics(meta["data_type"].iloc[0])

        elif "omics" in meta.columns:
            omics = normalize_omics(meta["omics"].iloc[0])

        elif "repository" in meta.columns:
            repo = str(meta["repository"].iloc[0]).lower()
            omics = "rna" if repo == "geo" else "proteomics"

        else:
            omics = "unknown"

        # -----------------------------
        # Assign safely
        # -----------------------------
        if omics not in groups:
            logging.warning(f"{name}: unknown omics ({omics}) → skipping")
            continue

        groups[omics][name] = dataset

        logging.info(f"{name} → assigned to {omics}")

    # -----------------------------
    # Final summary
    # -----------------------------
    for g, d in groups.items():
        logging.info(f"{g}: {len(d)} datasets → {list(d.keys())}")

    return groups