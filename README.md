# Multiomics_data_pipeline
AI usage disclosure
    This project utilized AI tools for:
        - Debuggging pipeline error
        - architechtural brainstorming
        -code optimization suggestion
All implementation, validation and final integration were performed by the auhtor

#Team
Name: Keerthanaa Balasubramanian Shanthi
Contribution:
    - Pipeline design and implementation
    -multiomics integration
    - ML modeling
    - Testing and debugging


# Tasks implemented

# Documents and Presentation
    - Pipeline architecutre description
    -data schema documentation
    - end to end workflow explanation
    - dashboard for results

# Data Ingestion
    - Structed data( now works with synthetic data)
    - multi-source injestion (API+syntehtic fallback)
    - Automated batch injestion pipeline

# Data Processing and cleaning
    - ETL pipeline(cleaning, normalization, transformation)
    - medallion architecture
    - metadata harmonization(ontology +fuzzy matching)
    - Feature ID harmonization (Ensembl/Uniprot)
    - missing value imputation (proteomics)
    -schema validation

# Advanced features
    - Data lieage tracking 
    - ML model (Random Forest feature selection)
    - Batch effect detection(PCA, PVCA)
    - Batch correction (ComBat)

# Visualization and Monitoring
    - PCA (before and after batch correction)
    - pipeline statistics tracking
    - QC reports

# Data Sharing
    - Data product exported(Gold layer)
    - API- ready structure
    - can be deployed in cloud platforms like databricks with minimal chnages retaining the architecture

# Logging
    - Structured logging across all stages
    - Error handling and fallbacks

# Project Overview
This project implemets a config driven multi-omics pipeline that integrates RNA-seq and proteomics datasets from multiple repositories (GEO and PRIDE)

The pipeline is designed for:
    - resuability
    - scalability
    - biological validity

It performs:
    - Data ingestion
    - Harmonization
    - Normalization
    - Batch effect detection and correction
    - Feature selection using machine learning

# Pipeline Architecture
data/
│
├── bronze/      ← raw ingested data
├── gold/        ← final analytics-ready data

# Pipeline Flow
Ingestion
   ↓
Metadata Harmonization
   ↓
Normalization (config-driven)
   ↓
Feature Harmonization (Gene/Protein IDs)
   ↓
Missing Value Imputation
   ↓
Split by Omics (RNA / Proteomics)
   ↓
Feature Alignment
   ↓
Batch Effect Detection (PCA, PVCA)
   ↓
ComBat Correction (if needed)
   ↓
Machine Learning (Random Forest)
   ↓
Gold Export + QC + Stats

# Data Sources
1. GEO (RNA seq)
    - Gene expresison counts
    - Multiple studies combined
    - Ensembl gene IDs

2. PRIDE (Proteomics)
    - Protein abundance data
    - Missing values handled
    - Uniprot IDs

3. Synthetic Dataset
    - Generated to validate:
        - Batch effects
        - Biological signal
        - ML feature recovery

# data schema
Metadata
Column              Description
sample_id           Unique sample
condition           Biological condition
batch               tehcnical batch
study_id            study source
repository          GEO/PRIDE
omics               RNA/Proteomics

# Expression Matrix
Row                 Column
Sample              Feature (gene/protein)

# Key Features

1. Config driven normalization
    supports
        - DESeq2(VST, rlog)
        - TPM/FPKM
        - Quantile
        - z-score
        - median normalization

2. Feature ID harmonization
    - Ensembl conversion to gene symbols using BioMart
    - Uniprot normalization
    - this ensures cross study compatability for feature selection

3. Batch effect handling
    Detection
        -PCA
        -PVCA
    Correction
        - ComBat(applied only if atch effect detected)

4. Machine learning
    - random forest classifier
    - feature importance extraction
    - per omics analysis

5. PCA analysis
    - before and after batch correction
    - Used ot validate:
        - Batch removal
        - biological clustering

# Quality control
Computed metriics:
    - Missing value rate
    - Sample count
    - Feature count
    - PCA variance explained

# How to Run
#activate environment
venv\Scripts\activate
#run pipeline
python src/run_pipeline.py

# Innovativeness
- Multiomics data integration (intiated)
- COnfig driven achitecture
- Automated batch detection and correction
- ML integrated into ETL pipeline
- synthetic validation framework

# Limitations
- The real world omics data needs standardization before this pipeline which will take rigorous robust standardization before ingestion
- BioMart dependency may fail (fallback implemented)
- Synthetic data used for testing (not full biological complexity)
- No real-time streaming (batch-based pipeline)

# Future improvements being done
- Real-time ingestion (streaming)
- Deep learning models
- Cross-omics integration (joint embedding)
- Web dashboard / API deployment

# Conclusion
This pipeline demonstrates a fully automated, reusable and iologically meaningful data engineering solution for multi-omics data analysis and intergation:
- Data engineering
- Bioinformatics
- Machine Leanring