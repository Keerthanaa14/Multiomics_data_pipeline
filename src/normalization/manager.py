import numpy as np
import pandas as pd
from .methods import apply_method
from .validators import validate_input
import logging

def normalize_expression(data, config):

    logging.info("Normalizing expression data...")
    processed = {}

    for name, dataset in data.items():

        df= dataset["expression"].copy()
        metadata = dataset["metadata"]

        original_index = df.index
        original_columns = df.columns

        repo = metadata["repository"].iloc[0]

        if repo == "geo":
            cfg = config.get("methods.rna_normalization", {})
            data_type = "RNA"
        elif repo == "pride":
            ccfg = config.get("methods.proteomics_normalization", {})
            data_type = "PROTEOMICS"
        else:
            logging.warning(f"{name}: Unknown repo choosing fallback options")
            cfg = {"primary_method":"zscore", "fallback_method":"zscore", "parameters":{}}
            data_type = "UNKNOWN"

        primary = cfg.get("primary_method", "zscore")
        fallback = cfg.get("fallback_method")
        params = cfg.get("parameters", {})

        try:
            validate_input(df, data_type, primary)
            df_norm = apply_method(primary,df,metadata, params)
            used = primary
        
        except Exception as e:
            logging.warning(f"{name}: Primary normalization {primary} failed with error: {e}")
            if fallback:
                df_norm = apply_method(fallback,df,metadata, params)
                used = fallback
            else:
                raise e
            
        if isinstance(df_norm, np.ndarray):
            df_norm = pd.DataFrame(
                df_norm,
                index=original_index,
                columns=original_columns
            )

        elif isinstance(df_norm, pd.DataFrame):
            df_norm.index = original_index
            df_norm.columns = original_columns

        else:
            raise ValueError(f"{name}: normalization returned unsupported type {type(df_norm)}")

        # Final validation
        if len(df_norm) != len(metadata):
            raise ValueError(f"{name}: mismatch after normalization")

        processed[name] = {"metadata": metadata, "expression": df_norm, "normalized_with": used}
        logging.info(f"{name}: ✅ normalized using {used}")
        return processed