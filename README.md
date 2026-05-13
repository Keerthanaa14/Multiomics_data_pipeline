# Multiomics Data Pipeline for Cross-Study Integration and Feature Selection

### Config-Driven Multiomics Data Engineering Pipeline with Batch Correction, Metadata Harmonization, and ML-Based Feature Selection

---

## Overview

This project implements a config-driven multiomics data pipeline for integrating RNA-seq and proteomics datasets from multiple public repositories including GEO and PRIDE. The pipeline is designed to support scalable, reusable, and biologically meaningful data integration workflows for downstream analytics and machine learning.

The system combines modern data engineering principles with bioinformatics workflows to automate:

* Data ingestion
* Metadata harmonization
* Feature ID harmonization
* Data normalization
* Batch effect detection and correction
* Multiomics feature alignment
* Machine learning-based feature selection
* Quality control reporting
* Dashboard generation

The pipeline follows a medallion architecture (Bronze → Gold) and supports structured and semi-structured biomedical datasets.

---

# Motivation

Multiomics datasets generated across independent studies are often heterogeneous, inconsistently annotated, and affected by technical batch effects. Integrating these datasets reproducibly while preserving biological signal remains a major challenge in computational biology.

This project was developed to demonstrate how modern data engineering workflows can support scalable and reproducible multiomics integration using configurable ETL pipelines, metadata harmonization, automated validation, and machine learning.

The project focuses on:

* Cross-study RNA-seq and proteomics integration
* Metadata standardization
* Feature harmonization across repositories
* Automated batch effect handling
* ML-ready data generation
* Reproducible analytical workflows

---

# Key Features

## Data Ingestion

* Structured data ingestion using synthetic datasets
* Semi-structured parsing of gene count files
* Automated batch ingestion workflows
* Support for GEO and PRIDE datasets

## Data Processing & Cleaning

* ETL pipeline for cleaning, normalization, and transformation
* Metadata harmonization using ontology mapping and fuzzy matching
* Feature ID harmonization across Ensembl and UniProt identifiers
* Missing value imputation for proteomics datasets
* Schema validation and metadata verification

## Batch Effect Detection & Correction

* PCA-based batch effect detection
* PVCA-based variance assessment
* Conditional ComBat batch correction
* Pre- and post-correction PCA visualization

## Machine Learning Integration

* Random Forest feature selection
* Feature importance extraction
* Per-omics analysis workflows
* ML-ready feature matrix generation

## Monitoring & Visualization

* HTML dashboard generation
* QC report generation
* Pipeline statistics tracking
* Logging and error handling across all stages

## Data Product & Sharing

* Structured analytics-ready outputs
* API-ready data structures
* Gold layer exports
* Cloud-deployment-compatible architecture

---

# Pipeline Architecture

The pipeline follows a medallion-style architecture:

```text
Raw Data Sources (GEO / PRIDE / Synthetic Data)
                     │
                     ▼
┌──────────────────────────────────┐
│ Bronze Layer                    │
│ Raw ingested datasets           │
└──────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────┐
│ Harmonization & Processing       │
│ - Metadata harmonization         │
│ - Feature ID alignment           │
│ - Normalization                  │
│ - Missing value imputation       │
└──────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────┐
│ Batch Effect Analysis            │
│ - PCA                            │
│ - PVCA                           │
│ - Conditional ComBat correction  │
└──────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────┐
│ Machine Learning                 │
│ Random Forest feature selection  │
└──────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────┐
│ Gold Layer                       │
│ Analytics-ready integrated data  │
└──────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      ▼                             ▼
Dashboard Outputs            API-ready Outputs
```

---

# Pipeline Flow

```text
Data Ingestion
      ↓
Metadata Harmonization
      ↓
Normalization (Config-Driven)
      ↓
Feature Harmonization (Gene/Protein IDs)
      ↓
Missing Value Imputation
      ↓
Split by Omics Type
      ↓
Feature Alignment
      ↓
Batch Effect Detection (PCA, PVCA)
      ↓
Conditional ComBat Correction
      ↓
Machine Learning (Random Forest)
      ↓
Gold Export + QC + Statistics
```

---

# Data Sources

## GEO (RNA-seq)

* Gene expression count datasets
* Multiple studies combined
* Ensembl gene identifiers

## PRIDE (Proteomics)

* Protein abundance datasets
* Missing value handling implemented
* UniProt protein identifiers

## Synthetic Dataset

Synthetic datasets were generated to validate:

* Batch effects
* Biological signal preservation
* ML feature recovery
* Pipeline robustness

---

# Data Schema

## Metadata Schema

| Column     | Description              |
| ---------- | ------------------------ |
| sample_id  | Unique sample identifier |
| condition  | Biological condition     |
| batch      | Technical batch          |
| study_id   | Study source             |
| repository | GEO or PRIDE             |
| omics      | RNA-seq or Proteomics    |

## Expression Matrix

| Row    | Column                 |
| ------ | ---------------------- |
| Sample | Feature (gene/protein) |

---

# Technology Stack

| Component                | Technology                     |
| ------------------------ | ------------------------------ |
| Workflow orchestration   | Python-based workflow          |
| Data architecture        | Medallion architecture         |
| Machine learning         | Random Forest                  |
| Batch correction         | ComBat                         |
| PCA analysis             | PCA / PVCA                     |
| Identifier harmonization | BioMart / UniProt              |
| Visualization            | HTML dashboard                 |
| Logging                  | Structured logging             |
| HPC compatibility        | CSC Puhti-compatible workflows |

---

# Repository Structure

```text
Multiomics_data_pipeline/
│
├── Data/              # Raw and processed datasets
├── config/            # Configuration files
├── dashboard/         # Dashboard outputs
├── logs/              # Structured logs
├── src/               # Core pipeline source code
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Quality Control

Computed metrics include:

* Missing value rate
* Sample count
* Feature count
* PCA variance explained
* Batch effect assessment

The pipeline generates QC reports and visualization outputs to validate biological signal preservation after preprocessing and batch correction.

---

# Scalability & Engineering Design

The pipeline is designed to support:

* Config-driven execution
* Reusable ETL workflows
* Automated metadata harmonization
* Scalable multi-study integration
* Cloud deployment compatibility
* HPC execution environments

The architecture can be adapted to cloud platforms such as Databricks with minimal modifications.

---

# Running the Pipeline

## Activate Environment

```bash
venv\\Scripts\\activate
```

## Run Pipeline

```bash
python src/run_pipeline.py
```

---

# Current Limitations

* Real-world omics datasets require extensive standardization before ingestion
* BioMart dependency may occasionally fail (fallback implemented)
* Synthetic data is used for testing and validation
* No real-time streaming support yet (batch-based pipeline)

---

# Future Improvements

Planned enhancements include:

* Real-time streaming ingestion
* Deep learning integration
* Cross-omics joint embedding
* Web dashboard deployment
* API deployment
* Expanded lineage tracking
* Advanced cloud-native orchestration

---

# Innovativeness

This project demonstrates:

* Multiomics data integration workflows
* Automated metadata harmonization
* Config-driven architecture
* Automated batch effect detection and correction
* Machine learning integrated directly into ETL workflows
* Synthetic validation framework for reproducibility testing

---

# AI Usage Declaration

AI tools were used for:

* Debugging pipeline issues
* Architectural brainstorming
* Improving code robustness and structure

AI tools were not used for:

* Direct copy-paste implementation of complete solutions
* Unmodified report generation

All implementation, validation, integration, and final review were independently completed by the author.

---

# Conclusion

This project demonstrates a reusable and scalable multiomics data engineering workflow integrating:

* Data engineering
* Bioinformatics
* Machine learning

The pipeline combines automated ETL workflows, metadata harmonization, batch effect correction, and ML-based feature selection into a unified reproducible framework for cross-study biomedical data integration.

---

# License

MIT License

![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
