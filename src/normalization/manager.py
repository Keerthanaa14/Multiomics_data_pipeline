import numpy as np
import logging

def normalize_expression(data, config):

    logging.info("Normalizing expression data...")
    processed = {}

    for name, dataset in data.items():

        df= dataset["expression"].copy()
        metadata = dataset["metadata"]
        repo = metadata["repository"].iloc[0]

        if repo == "geo":
            cfg = config["methods"]["rna_normalization"]
            data_type = "RNA"
        elif repo == "pride":
            cfg = config["methods"]["proteomics_normalization"]
            data_type = "PROTEOMICS"
        else:
            logging.warning(f"{name}: Unknown repo choosing fallback options")
            cfg = {"primary_method":"zscore", "fallback_method":"zscore", "parameters":{}}

        primary = cfg["primary_method"]
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

        processed[name] = {"metadata": metadata, "expression": df_norm, "normalized_with": used}

        return processed