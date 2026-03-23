import pandas as pd
import logging
from pathlib import Path
import time


# --------------------------------------------------
# Helper: save dataframe in multiple formats
# --------------------------------------------------
def save_outputs(df, path, name, formats, compression):

    if df is None or len(df) == 0:
        return

    path.mkdir(parents=True, exist_ok=True)

    if "parquet" in formats:
        df.to_parquet(path / f"{name}.parquet", compression=compression)

    if "csv" in formats:
        df.to_csv(path / f"{name}.csv", index=False)


# --------------------------------------------------
# Main Gold Export
# --------------------------------------------------
def gold_export(data, qc_results, batch_results, feature_results, config):

    logging.info("Exporting Gold layer...")
    start = time.time()

    base = Path("data/gold")
    base.mkdir(parents=True, exist_ok=True)

    formats = config.get("output.formats", ["parquet"])
    compression = config.get("output.compression", "snappy")

    # ==================================================
    # 1. SAVE PER DATASET (metadata + expression)
    # ==================================================
    for dataset_name, dataset in data.items():

        metadata = dataset.get("metadata")
        expression = dataset.get("expression")

        # infer omics type
        metadata = dataset.get("metadata")

        if metadata is not None and "data_type" in metadata.columns:
            omics = metadata["data_type"].iloc[0]
        else:
            omics = "unknown"

        dataset_path = base / omics / dataset_name

        # -------- Metadata --------
        if metadata is not None:
            save_outputs(metadata, dataset_path, "metadata", formats, compression)

        # -------- Expression (gene counts) --------
        if expression is not None:

            expr_df = expression.copy()

            # ensure sample_id column exists
            if expr_df.index.name is None or expr_df.index.name != "sample_id":
                expr_df.index.name = "sample_id"

            expr_df = expr_df.reset_index()

            save_outputs(expr_df, dataset_path, "expression", formats, compression)

    # ==================================================
    # 2. QC SUMMARY
    # ==================================================
    if qc_results:
        qc_df = pd.DataFrame(qc_results).T
        save_outputs(qc_df, base, "qc_summary", formats, compression)

    # ==================================================
    # 3. BATCH RESULTS (PCA + PVCA)
    # ==================================================
    for group_name, result in (batch_results or {}).items():

        group_path = base / group_name
        group_path.mkdir(parents=True, exist_ok=True)

        # PCA before
        if "pca_before" in result:
            save_outputs(
                result["pca_before"],
                group_path,
                f"pca_before_{group_name}",
                formats,
                compression
            )

        # PCA after
        if "pca_after" in result:
            save_outputs(
                result["pca_after"],
                group_path,
                f"pca_after_{group_name}",
                formats,
                compression
            )

        # PVCA before
        if "pvca_before" in result:
            save_outputs(
                pd.DataFrame([result["pvca_before"]]),
                group_path,
                f"pvca_before_{group_name}",
                formats,
                compression
            )

        # PVCA after
        if "pvca_after" in result:
            save_outputs(
                pd.DataFrame([result["pvca_after"]]),
                group_path,
                f"pvca_after_{group_name}",
                formats,
                compression
            )

        # ComBat flag
        flag_df = pd.DataFrame([{
            "combat_applied": result.get("combat_applied", False)
        }])

        save_outputs(
            flag_df,
            group_path,
            f"combat_flag_{group_name}",
            formats,
            compression
        )

    # ==================================================
    # 4. FEATURE IMPORTANCE
    # ==================================================
    for group_name, df in (feature_results or {}).items():

        if df is None or len(df) == 0:
            continue

        group_path = base / group_name
        group_path.mkdir(parents=True, exist_ok=True)

        save_outputs(
            df,
            group_path,
            f"feature_importance_{group_name}",
            formats,
            compression
        )

    # ==================================================
    # 5. PIPELINE STATISTICS
    # ==================================================
    stats = {
        "datasets": len(data),
        "omics_groups": len(batch_results or {}),
        "runtime_sec": round(time.time() - start, 2),
    }

    for group_name, result in (batch_results or {}).items():

        variance = result.get("pca_variance_after")

        if variance and len(variance) > 0:
            stats[f"{group_name}_pc1_variance_after"] = variance[0]

    stats_df = pd.DataFrame([stats])
    save_outputs(stats_df, base, "pipeline_statistics", formats, compression)

    logging.info("Gold Export completed")