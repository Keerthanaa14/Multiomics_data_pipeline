import logging

def compute_qc(data, config):
    logging.info("Computing QC metrics...")

    qc = {}

    for name, dataset in data.items():
        meta = dataset["metadata"]
        expr = dataset["expression"]

        qc[name] = {
            "samples" : len(meta),
            "features": expr.shape[1],
            "missing_metadata": meta.isnull().mean().mean(),
            "missing_expression": expr.isnull().mean().mean(),
            "unique_batches": meta["batch"].nunique() if "batch" in meta else 0,
            "unique_conditions": meta["condition"].nunique() if "condition" in meta else 0
        }

    return qc