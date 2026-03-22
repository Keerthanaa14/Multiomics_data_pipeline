import pandas as pd
import logging
from pathlib import Path
import time

def save_outputs(df, path, name, formats, compression):

    if df is None or len(df) == 0:
        return
    
    if "parquet" in formats:
        df.to_parquet(path / f"{name}.parquet", compression=compression)

    if "csv" in formats:
        df.to_csv(path / f"{name}.csv", index=False)

def gold_export(data, qc_results, batch_results, feature_results, config):
    logging.info("Exporting Gold layer...")
    start = time.time()

    base = Path("data/gold")
    base.mkdir(parents=True, exist_ok=True)

    formats = config.get("output.formats", ["parquet"])
    compression = config.get("output.compression", "snappy")

    # Qc
    qc_df = pd.DataFrame(qc_results).T
    save_outputs(qc_df, base, "qc_summary", formats, compression)

    #batch results: PCA/PVCA before and after
    for group_name, result in batch_results.items():
        group_path = base / group_name
        group_path.mkdir(exist_ok=True)

        #before batch correction
        if "pca_before" in result:
            save_outputs(
                result["pca_before"] ["pca_table"],
                group_path,
                f"pca_before_{group_name}",
                formats,
                compression
            )
        
        if "pvca_before" in result:
            save_outputs(
                pd.DataFrame([result["pvca_before"]]),
                group_path,
                f"pvca_before_{group_name}",
                formats,
                compression
            )
        
        #after batch correction
        if "pca_after" in result:
            save_outputs(
                result["pca_after"] ["pca_table"],
                group_path,
                f"pca_after_{group_name}",
                formats,
                compression
            )
        
        if "pvca_after" in result:
            save_outputs(
                pd.DataFrame([result["pvca_after"]]),
                group_path,
                f"pvca_after_{group_name}",
                formats,
                compression
            )

        # flag
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
    # fetaure importance
    for group_name, df in feature_results.items():
        group_path = base / group_name
        group_path.mkdir(exist_ok=True)

        if df is not None:
            save_outputs(
                df,
                group_path,
                f"feature_importance_{group_name}",
                formats,
                compression
            )

    #pipeline stats

    stats = {
        "datasets": len(data),
        "omics_groups": len(batch_results),
        "runtime_sec": round(time.time() - start, 2),
    }

    for group_name, result in batch_results.items():
        if "pca_after" in result:
            stats[f"{group_name}_pc1_variance_after"] = result["pca_after"]["variance"][0]

    stats_df = pd.DataFrame([stats])
    save_outputs(stats_df, base,"pipeline_statistics", formats, compression)

    logging.info("Gold Export completed")