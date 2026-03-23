import yaml
import logging
import pandas as pd
from rapidfuzz import process


# -----------------------------
# Helpers
# -----------------------------
def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def normalize(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def standardize_column(df, column_map):
    new_columns = {}

    for standard, variants in column_map.items():
        for col in df.columns:
            if normalize(col) in [normalize(v) for v in variants]:
                new_columns[col] = standard

    return df.rename(columns=new_columns)


def enforce_schema(df, required_columns):
    for col in required_columns:
        if col not in df.columns:
            df[col] = "unknown"
    return df


# -----------------------------
# Alignment
# -----------------------------
def align_metadata_expression(metadata, expression):

    if expression is None:
        return metadata, expression

    if "sample_id" not in metadata.columns:
        raise ValueError("Metadata missing 'sample_id'")

    metadata = metadata.set_index("sample_id")

    # CASE 1: already aligned
    if len(metadata) == expression.shape[0]:
        logging.info(" Metadata and expression aligned (row-wise)")
        return metadata.reset_index(), expression.reset_index(drop=True)

    # CASE 2: transpose needed
    if len(metadata) == expression.shape[1]:
        logging.info("Transposing expression")
        expression = expression.T
        return metadata.reset_index(), expression.reset_index(drop=True)

    # CASE 3: match by ID
    common = metadata.index.intersection(expression.index)

    if len(common) > 0:
        logging.info(f"Aligning using {len(common)} shared samples")
        return metadata.loc[common].reset_index(), expression.loc[common]

    raise ValueError("Could not align metadata and expression")


def validate_metadata(df):

    if "sample_id" not in df.columns:
        raise ValueError("Missing sample_id")

    if df["sample_id"].isnull().any():
        raise ValueError("Null sample_id detected")

    if "batch" not in df.columns:
        raise ValueError("Missing batch column")

    if df["batch"].nunique() < 1:
        raise ValueError("Invalid batch column")


# -----------------------------
# Harmonizer
# -----------------------------
class MetadataHarmonizer:

    def __init__(self, config):

        self.config = config or {}

        self.disease_map = load_yaml("config/disease_map.yaml")
        self.tissue_map = load_yaml("config/tissue_map.yaml")
        self.sex_map = load_yaml("config/sex_map.yaml")
        self.column_map = load_yaml("config/column_map.yaml")

        self.required_fields = self.config.get(
            "validation.required_metadata_fields", []
        )

        logging.info(f"Schema fields loaded: {self.required_fields}")

    # -----------------------------
    # Mapping functions
    # -----------------------------
    def map_value(self, value, mapping):

        value_norm = normalize(value)

        for standard, synonyms in mapping.items():
            if value_norm == normalize(standard):
                return standard
            if value_norm in [normalize(s) for s in synonyms]:
                return standard

        # fuzzy match
        match = process.extractOne(value_norm, mapping.keys())
        if match and match[1] > 80:
            return match[0]

        # IMPORTANT: keep meaningful values
        if value_norm in ["control", "case", "disease", "healthy"]:
            return value_norm

        return value_norm

    # -----------------------------
    # Core fields (CRITICAL)
    # -----------------------------
    def ensure_core_fields(self, df, dataset_name):

        # sample_id
        if "sample_id" not in df.columns:
            df["sample_id"] = [f"{dataset_name}_{i}" for i in range(len(df))]

        df["sample_id"] = df["sample_id"].astype(str)

        # batch
        if "batch" not in df.columns:
            if "study_id" in df.columns:
                df["batch"] = df["study_id"]
            else:
                df["batch"] = dataset_name

        df["batch"] = df["batch"].astype(str)

        # condition (CRITICAL FIX)
        if "condition" not in df.columns:

            if "disease_status" in df.columns:
                df["condition"] = df["disease_status"]
            else:
                df["condition"] = "unknown"

        df["condition"] = df["condition"].astype(str).str.lower()

        # normalize condition values
        df["condition"] = df["condition"].replace({
            "healthy": "control",
            "normal": "control",
            "case": "disease"
        })

        df.loc[~df["condition"].isin(["control", "disease"]), "condition"] = "unknown"

        # dataset identity
        df["study"] = dataset_name
        
    
        if "data_type" not in df.columns:

            # infer from dataset name
            if "geo" in dataset_name.lower():
                df["data_type"] = "rna"
            elif "pride" in dataset_name.lower():
                df["data_type"] = "proteomics"
            else:
                df["data_type"] = "rna"
        
        return df

    # -----------------------------
    # Main harmonization
    # -----------------------------
    def harmonize_metadata(self, df, dataset_name):

        logging.info("Harmonizing metadata...")

        df = standardize_column(df, self.column_map)

        # value harmonization
        if "disease_status" in df.columns:
            df["disease_status"] = df["disease_status"].apply(
                lambda x: self.map_value(x, self.disease_map)
            )

        if "sex" in df.columns:
            df["sex"] = df["sex"].apply(
                lambda x: self.map_value(x, self.sex_map)
            )

        if "tissue_type" in df.columns:
            df["tissue_type"] = df["tissue_type"].apply(
                lambda x: self.map_value(x, self.tissue_map)
            )

        # enforce core fields
        df = self.ensure_core_fields(df, dataset_name)

        # enforce schema
        df = enforce_schema(df, self.required_fields)

        # Debug logging
        logging.info(
            f"{dataset_name}: condition → {df['condition'].value_counts().to_dict()}"
        )
        logging.info(
            f"{dataset_name}: batches → {df['batch'].nunique()}"
        )

        logging.info("Metadata harmonization complete.")

        return df


# -----------------------------
# Pipeline entry
# -----------------------------
def run_harmonization(config, data):

    harmonizer = MetadataHarmonizer(config)
    harmonized = {}

    for name, dataset in data.items():

        metadata = dataset["metadata"].copy()
        expression = dataset.get("expression")

        metadata = harmonizer.harmonize_metadata(metadata, name)
        metadata, expression = align_metadata_expression(metadata, expression)

        validate_metadata(metadata)

        harmonized[name] = {
            "metadata": metadata,
            "expression": expression
        }

        logging.info(f"Harmonized {name}")

    return harmonized