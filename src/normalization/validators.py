import numpy as np
import logging

def validate_input(df, data_type, method):

    #DESeq2 requires raw counts, so we check for non-negative integers
    if method.startswith("deseq2"):
        if not np.issubdtype(df.values.dtype, np.integer):
            raise ValueError(f"{method} requires integer count data.")
        if (df.values < 0).any():
            raise ValueError(f"{method} requires non-negative count data.")
        
    # For proteomics data, we check for missing input
    if data_type == "PROTEOMICS":
        if df.isnull(). sum().sum() > 0:
            raise ValueError(f"{method} cannot handle missing values in proteomics data.")