import logging
from batch.pca import run_pca
from batch.pvca import run_pvca
from batch.combat import run_combat

def detect_batch_effect(data,config):

    results = {}

    params = config.get("methods.batch_detection.parameters", {})

    #PCA before batch correction

    pca_before = run_pca(data, params.get("pca", {}))
    pvca_before = run_pvca(data, params.get("pvca", {}))

    results["pca_before"] = pca_before
    results["pvca_before"] = pvca_before

    batch_var = pvca_before.get("mean_batch_variance",0)
    cond_var = pvca_before.get("mean_condition_variance",0)

    logging.info(f"Batch variance: {batch_var:.3f}, Condition variance: {cond_var:.3f}")
    apply_combat = batch_var > cond_var

    results["combat_applied"] = apply_combat

    # apply combat if needed

    if apply_combat:
        logging.info("Batch effect detected; applying ComBat")
        for name, dataset in data.items():
            expr = dataset["expression"]
            meta = dataset["metadata"]

            corrected = run_combat(expr, meta)
            dataset["expression"] = corrected

    else:
        logging.info("No strong batch effect detected; skipping combat")

    #PCA after Batch effect correction

    pca_after = run_pca(data, params.get("pca",{}))
    pvca_after = run_pvca(data, params.get("pvca", {}))

    results["pca_after"] = pca_after
    results["pvca_after"] = pvca_after

    return results
