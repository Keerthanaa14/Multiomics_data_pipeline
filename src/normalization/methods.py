from .r_methods import (run_deseq2_vst, run_deseq2_rlog, run_vsn, run_tmm)
from .py_methods import (run_zscore, run_quantile, run_median, run_tpm, run_fpkm)

def apply_method(method, df, metadata, params):
    if method == "deseq2_vst":
        return run_deseq2_vst(df, metadata, params.get("deseq2_vst", {}))
    elif method == "deseq2_rlog":
        return run_deseq2_rlog(df, metadata)
    elif method == "vsn":
        return run_vsn(df, metadata)
    elif method == "tmm":
        return run_tmm(df, metadata)
    elif method == "quantile":
        return run_quantile(df)
    elif method == "zscore":
        return run_zscore(df)
    elif method == "median":
        return run_median(df)
    elif method == "tpm":
        return run_tpm(df)
    elif method == "fpkm":
        return run_fpkm(df)
    else:
        raise ValueError(f"Unknown normalization method: {method}")