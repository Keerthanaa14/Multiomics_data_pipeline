import logging
from batch.pca import run_pca
from batch.pvca import run_pvca
from batch.combat import run_combat


def detect_batch_effect(data, config):

    results = {}

    params = config.get("methods.batch_detection.parameters", {})

    # PCA BEFORE
    pca_before = run_pca(data, params.get("pca", {}))
    pvca_before = run_pvca(data, params.get("pvca", {}))

    results["pca_before"] = pca_before["pca_table"]
    results["pca_variance_before"] = pca_before["variance"]
    results["pvca_before"] = pvca_before

    batch_var = pvca_before.get("mean_batch_variance", 0)
    cond_var = pvca_before.get("mean_condition_variance", 0)

    logging.info(f"Batch variance: {batch_var:.3f}, Condition variance: {cond_var:.3f}")

    apply_combat = batch_var > cond_var
    results["combat_applied"] = apply_combat

    # APPLY COMBAT SAFELY
    if apply_combat:
        logging.info("Batch effect detected → applying ComBat")

        for name, dataset in data.items():

            meta = dataset["metadata"]

            if meta["batch"].nunique() < 2:
                logging.warning(f"{name}: only 1 batch → skipping")
                continue

            if meta["condition"].nunique() < 2:
                logging.warning(f"{name}: only 1 condition → skipping")
                continue

            try:
                dataset["expression"] = run_combat(
                    dataset["expression"],
                    meta
                )
                logging.info(f"{name}: ✅ ComBat applied")

            except Exception as e:
                logging.warning(f"{name}: ComBat failed → {e}")

    else:
        logging.info("No strong batch effect → skipping ComBat")

    # PCA AFTER
    pca_after = run_pca(data, params.get("pca", {}))
    pvca_after = run_pvca(data, params.get("pvca", {}))

    results["pca_after"] = pca_after["pca_table"]
    results["pca_variance_after"] = pca_after["variance"]
    results["pvca_after"] = pvca_after

    return results