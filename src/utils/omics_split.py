import logging


def split_by_omics(data):

    logging.info("Splitting datasets by omics type...")

    groups = {}

    for name, dataset in data.items():

        meta = dataset.get("metadata")

        if meta is None or len(meta) == 0:
            logging.warning(f"{name}: missing metadata → skipping")
            continue

        # Detect omics type
        if "data_type" in meta.columns:
            omics = str(meta["data_type"].iloc[0]).lower()
        elif "repository" in meta.columns:
            repo = str(meta["repository"].iloc[0]).lower()
            omics = "rna" if repo == "geo" else "proteomics"
        else:
            omics = "rna"

        # Normalize naming
        if omics in ["transcriptomics"]:
            omics = "rna"

        if omics in ["protein"]:
            omics = "proteomics"

        groups.setdefault(omics, {})
        groups[omics][name] = dataset

        logging.info(f"{name} → assigned to {omics}")

    for g, d in groups.items():
        logging.info(f"{g}: {len(d)} datasets → {list(d.keys())}")

    return groups