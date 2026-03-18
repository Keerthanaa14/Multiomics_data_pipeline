import yaml
import logging
from rapidfuzz import process

# Helpers

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)
    
def normalize(value):
    if value is None:
        return ""
    return str(value).strip().lower()

def standardize_column(df, column_map):
    new_columns = {}
    for standard, variants in column_map.items():
        for col in df.columns:
            if col.lower() in [v.lower() for v in variants]:
                new_columns[col] = standard

    return df.rename(columns=new_columns)

def enforce_schema(df, required_columns):
    for field in required_columns:
        if field not in df.columns:
            df[field] = "unknown"
    return df

# Main Harmonizer Class
class MetadataHarmonizer:
    def __init__(self, config):
        # store provided config dict (can be empty)
        self.config = config or {}

        # load mappings
        self.disease_map = load_yaml("config/disease_map.yaml")
        self.tissue_map = load_yaml("config/tissue_map.yaml")
        self.cell_map = load_yaml("config/cell_map.yaml")
        self.organism_map = load_yaml("config/organism_map.yaml")
        self.sex_map = load_yaml("config/sex_map.yaml")
        self.column_map = load_yaml("config/column_map.yaml")
        self.platform_map = load_yaml("config/platform_map.yaml")

        # Load schema dynamically from pipeline_config.yaml (provided via config)
        self.required_fields = self.config.get(
            "validation.required_metadata_fields", []
        )
        logging.info(f"Schema fields loaded: {self.required_fields}")

    # Harmonization functions
    def map_with_synonyms(self, value, mapping):
        value = normalize(value)

        for standard, synonyms in mapping.items():
            if value == standard.lower():
                return standard
            if value in [s.lower() for s in synonyms]:
                return standard
        return None

    def fuzzy_match(self, value, mapping, threshold=80):
        value = normalize(value)
        choices = list(mapping.keys())
        result = process.extractOne(value, choices)
        if not result:
            return None
        match, score, _ = result
        if score >= threshold:
            return match
        return None

    def harmonize_value(self, value, mapping):
        mapped = self.map_with_synonyms(value, mapping)
        if mapped:
            return mapped
        mapped = self.fuzzy_match(value, mapping)
        if mapped:
            return mapped

        logging.warning(f"Unmapped value: {value}")
        return "unknown"

    # Main Harmonization function
    def harmonize_metadata(self, df):
        logging.info("Harmonizing metadata...")

        # Standardize column names first
        df = standardize_column(df, self.column_map)

        # detailed tissue information retained
        if "tissue_type" in df.columns:
            df["tissue_detail"] = df["tissue_type"]

        # Value harmonization
        if "disease_status" in df.columns:
            df["disease_status"] = df["disease_status"].apply(
                lambda x: self.harmonize_value(x, self.disease_map)
            )

        if "sex" in df.columns:
            df["sex"] = df["sex"].apply(lambda x: self.harmonize_value(x, self.sex_map))

        if "tissue_type" in df.columns:
            df["tissue_type"] = df["tissue_type"].apply(
                lambda x: self.harmonize_value(x, self.tissue_map)
            )

        # enforce schema
        df = enforce_schema(df, self.required_fields)
        logging.info("Metadata harmonization complete.")
        return df

def run_harmonization(pipeline_config, data):
    harmonizer = MetadataHarmonizer(pipeline_config)
    harmonized_data = {}

    for dataset_name, dataset in data.items():
        metadata = dataset["metadata"].copy()
        expression = dataset.get("expression")

        metadata_clean = harmonizer.harmonize_metadata(metadata)
        harmonized_data[dataset_name] = {"metadata": metadata_clean, "expression": expression}

        logging.info(f"Harmonized {dataset_name}")
    return harmonized_data