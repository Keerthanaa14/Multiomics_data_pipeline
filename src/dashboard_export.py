import os
import json
import logging


def export_dashboard(data, qc_results, feature_results, batch_results):

    os.makedirs("dashboard", exist_ok=True)

    dashboard = {
        "datasets": list(data.keys()),
        "qc": qc_results or {},
        "features": {},
        "batch": {}
    }

    # -----------------------------
    # FEATURE IMPORTANCE (safe)
    # -----------------------------
    for group, df in (feature_results or {}).items():

        if df is not None and hasattr(df, "to_dict"):
            dashboard["features"][group] = df.to_dict(orient="records")
        else:
            dashboard["features"][group] = []

    # -----------------------------
    # BATCH RESULTS (dynamic)
    # -----------------------------
    for group, result in (batch_results or {}).items():

        dashboard["batch"][group] = {
            "combat_applied": result.get("combat_applied", False),
            "variance_before": result.get("pca_variance_before", []),
            "variance_after": result.get("pca_variance_after", [])
        }

        pca = result.get("pca_before")

        if hasattr(pca, "to_dict"):
            dashboard["batch"][group]["pca"] = pca.to_dict(orient="records")
        else:
            dashboard["batch"][group]["pca"] = []

    # -----------------------------
    # SAVE
    # -----------------------------
    with open("dashboard/data.json", "w") as f:
        json.dump(dashboard, f, indent=2)

    logging.info(" Dashboard JSON exported")