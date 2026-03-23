from .r_methods import (
    run_deseq2_vst, run_deseq2_rlog, run_vsn, run_tmm
)
from .py_methods import (
    run_zscore, run_quantile, run_median, run_tpm, run_fpkm
)

import logging
import numpy as np
import pandas as pd


def apply_method(method, df, metadata, params):
    """
    Apply normalization method.
    Always returns DataFrame with preserved index and columns.
    """

    # Preserve structure
    index = df.index
    columns = df.columns

    # --------------------------------------------------
    # Apply method
    # --------------------------------------------------
    if method == "deseq2_vst":
        if not np.issubdtype(df.values.dtype, np.integer):
            raise ValueError("DESeq2 requires integer counts")
        result = run_deseq2_vst(df, metadata, params.get("deseq2_vst", {}))

    elif method == "deseq2_rlog":
        if not np.issubdtype(df.values.dtype, np.integer):
            raise ValueError("DESeq2 requires integer counts")
        result = run_deseq2_rlog(df, metadata)

    elif method == "vsn":
        result = run_vsn(df, metadata)

    elif method == "tmm":
        result = run_tmm(df, metadata)

    elif method == "quantile":
        result = run_quantile(df)

    elif method == "zscore":
        result = run_zscore(df)

    elif method == "median":
        result = run_median(df)

    elif method == "tpm":
        result = run_tpm(df)

    elif method == "fpkm":
        result = run_fpkm(df)

    else:
        raise ValueError(f"Unknown normalization method: {method}")

    # --------------------------------------------------
    # enforce DataFrame with index/columns
    # --------------------------------------------------
    if isinstance(result, np.ndarray):
        result = pd.DataFrame(result, index=index, columns=columns)

    elif isinstance(result, pd.DataFrame):
        result.index = index
        result.columns = columns

    else:
        raise ValueError(f"{method}: unsupported return type {type(result)}")

    return result