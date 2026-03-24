import logging
from pathlib import Path
from Config_loader import ConfigLoader

# ingestion and study discovery
from injestion import run_ingestion
from study_loader import load_available_studies
from study_disocvery import StudyDiscovery

# Delta layer
from delta_writer import write_delta_table
from delta_reader import read_delta_tables

# Processing
from metadata_harmonizer import run_harmonization
from normalization.manager import normalize_expression

from utils.feature_harmonizer import harmonize_feature_ids
from utils.imputation import impute_missing_values
from utils.omics_split import split_by_omics
from utils.feature_alignment import align_features

# Batch + QC
from batch.manager import detect_batch_effect
from qc import compute_qc

# ML
from ml.feature_selection import run_feature_selection, aggregate_feature_importance

# Output
from gold_export import gold_export
from catalog import build_catalog

# R environment
import os

os.environ["R_HOME"] = r"C:\Program Files\R\R-4.5.2"
os.environ["R_USER"] = r"C:\Program Files\R\R-4.5.2" 
os.environ["PATH"] += r";C:\Program Files\R\R-4.5.2\bin\x64"

#dashboard
from dashboard_export import export_dashboard



def run_pipeline():

    logging.basicConfig(level=logging.INFO)
    logging.info("starting multi-omics pipeline...")

    # --------------------------------------------------
    # Load config
    # --------------------------------------------------
    config = ConfigLoader(
        "config/pipeline_config.yaml",
        environment="development"
    )

    # --------------------------------------------------
    # Study discovery
    # --------------------------------------------------
    available = load_available_studies()

    if isinstance(available, list):
        grouped = {"geo": [], "pride": []}
        for study in available:
            repo = study.get("repository", "geo")
            grouped.setdefault(repo, []).append(study)
        available = grouped

    selected = StudyDiscovery(config).discover(available)

    # --------------------------------------------------
    # Ingestion
    # --------------------------------------------------
    raw = run_ingestion(selected)

    write_delta_table(raw, config)
    data = read_delta_tables(selected)

    # --------------------------------------------------
    # Harmonization
    # --------------------------------------------------
    data = run_harmonization(config, data)

    build_catalog(data)

    # --------------------------------------------------
    # Normalization
    # --------------------------------------------------
    data = normalize_expression(data, config)

    # --------------------------------------------------
    # Feature harmonization + imputation
    # --------------------------------------------------
    data = harmonize_feature_ids(data, config)
    data = impute_missing_values(data, config)

    # --------------------------------------------------
    # Split by omics
    # --------------------------------------------------
    groups = split_by_omics(data)

    batch_results = {}
    feature_results = {}

    # --------------------------------------------------
    # Per-omics processing
    # --------------------------------------------------
    for group_name, group_data in groups.items():

        if len(group_data) == 0:
            continue

        logging.info(f"Processing omics group: {group_name}")

        # --------------------------
        # Feature alignment
        # --------------------------
        group_data = align_features(group_data)

        # Safety check (prevents PCA crash)
        for name, ds in group_data.items():
            expr = ds["expression"]
            meta = ds["metadata"]

            if len(expr) != len(meta):
                raise ValueError(f"{name}: mismatch before PCA")

            # enforce alignment (final safety)
            expr.index = meta["sample_id"].values

        # --------------------------
        # Batch detection
        # --------------------------
        result = detect_batch_effect(group_data, config)
        batch_results[group_name] = result

        # --------------------------
        # Feature selection
        # --------------------------
        logging.info(f"Running random forest for {group_name}")

        fs = run_feature_selection(group_data)
        agg = aggregate_feature_importance(fs)

        feature_results[group_name] = agg

    # --------------------------------------------------
    # QC
    # --------------------------------------------------
    qc_results = compute_qc(data, config)

    # --------------------------------------------------
    # Export
    # --------------------------------------------------
    gold_export(
        data=data,
        qc_results=qc_results,
        batch_results=batch_results,
        feature_results=feature_results,
        config=config
    )

    logging.info("pipeline completed!")
    print("DEBUG DASHBOARD INPUT")
    print("Data keys:", list(data.keys()))
    print("Batch results keys:", batch_results.keys())
    print("Feature results keys:", feature_results.keys())
    export_dashboard(data=data, qc_results=qc_results, feature_results=feature_results, batch_results=batch_results)
    


if __name__ == "__main__":
    run_pipeline()
