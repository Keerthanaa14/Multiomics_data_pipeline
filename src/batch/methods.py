from .pca import run_pca
from .pvca import run_pvca
from .rle import run_rle

def apply_batch_correction(method, data, metadata, params):
    if method == "pca":
        return run_pca(data, params.get("pca", {}))
    elif method == "pvca":
        return run_pvca(data, params.get("pvca", {}))
    elif method == "rle":
        return run_rle(data)
    elif method == "combat_detection":
        return {"info": "Combat batch effect detection results placeholder"}
    else:
        raise ValueError(f"Unknown batch correction method: {method}")