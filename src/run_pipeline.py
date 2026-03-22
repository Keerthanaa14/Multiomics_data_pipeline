import logging

from Config_loader import ConfigLoader

# for ingestion and study discovery

from injestion import run_ingestion
from study_loader import load_available_studies
from study_disocvery import StudyDiscovery

#Delta table layer or parquet file compression

from delta_writer import write_delta_table
from delta_reader import read_delta_tables

# Processing 

from metadata_harmonizer import run_harmonization
from normalization.manager import normalize_expression

from utils.feature_harmonizer import harmonize_feature_ids
from utils.imputation import impute_missing_values
from utils.omics_split import split_by_omics
from utils.feature_alignment import align_features

# Batch effect detection, correction and QC
from batch.manager import detect_batch_effect
from qc import compute_qc

#machine learning for feature selection
from ml.feature_selection import run_feature_selection, aggregate_feature_importance

#Final out or gold layer export
from gold_export import gold_export
from catalog import build_catalog

def run_pipeline():
    logging.basicConfig(level=logging.INFO)
    logging.info("starting multi-omics pipeline...")

    # load configuration

    config = ConfigLoader(
        "config/pipeline_config.yaml",
        environment="development"
    )

    # study discovery and injestion

    available = load_available_studies()
    selected = StudyDiscovery(config).discover(available)

    raw = run_ingestion(selected)

    # bronze layer converted to parquet or delta table
    write_delta_table(raw,config)
    data = read_delta_tables(selected)

    #metadata harmonization
    data = run_harmonization(config, data)

    #catalog
    build_catalog(data)

    #normalization based on config
    data = normalize_expression(data, config)

    #feature ID harmonization for cross study comparison
    data = harmonize_feature_ids(data, config)

    #missing value handling of proteomics data
    data = impute_missing_values(data, config)

    #split by omics 
    groups = split_by_omics(data)

    batch_results = {}
    feature_results = {}

    # per omics processing
    for group_name, group_data in groups.items():

        if len(group_data) == 0:
            continue
        logging.info(f"Processing omics group:{group_name}")

        #Feature alignment
        group_data = align_features(group_data)

        #batch detection, followed by ComBat; PCA before and after correction
        batch_results = detect_batch_effect(group_data, config)
        batch_results[group_name] = batch_results

        # Featuure selection using ML after batch correction
        logging.info(f"Running random forest for {group_name}")

        fs = run_feature_selection(group_data)
        agg = aggregate_feature_importance(fs)

        feature_results[group_name] = agg

    #Quality control global
    qc_results = compute_qc(data, config)

    #Export gold layer
    export_gold(
        data=data,
        qc_results=qc_results,
        batch_results=batch_results,
        feature_results=feature_results,
        config=config
    )

    logging.info("pipeline completed!")

if __name__ == "__main__":
    run_pipeline()

