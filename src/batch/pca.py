from sklearn.decomposition import PCA
import pandas as pd
import logging


def run_pca(data, params):

    all_expr = []
    batch_labels = []
    condition_labels = []
    study_labels = []
    sample_ids = []

    for name, dataset in data.items():

        expr = dataset["expression"].copy()
        meta = dataset["metadata"].copy()

        if "sample_id" not in meta.columns:
            meta["sample_id"] = expr.index.astype(str)

        if "study" not in meta.columns:
            meta["study"] = name

        meta = meta.set_index("sample_id")
        expr.index = expr.index.astype(str)

        common = meta.index.intersection(expr.index)

        if len(common) == 0:
            logging.warning(f"{name}: no matching samples → skipping")
            continue

        expr = expr.loc[common]
        meta = meta.loc[common]

        all_expr.append(expr)

        batch_labels.extend(meta.get("batch", ["unknown"] * len(meta)))
        condition_labels.extend(meta.get("condition", ["unknown"] * len(meta)))
        study_labels.extend(meta.get("study", [name] * len(meta)))
        sample_ids.extend(meta.index.tolist())

    if len(all_expr) == 0:
        raise ValueError("No valid datasets for PCA")

    combined = pd.concat(all_expr, axis=0).fillna(0)

    logging.info(f"Combined shape before PCA: {combined.shape}")

    n = params.get("n_components", 10)

    pca = PCA(n_components=n)
    coords = pca.fit_transform(combined)

    variance = pca.explained_variance_ratio_

    df = pd.DataFrame(coords, columns=[f"PC{i+1}" for i in range(coords.shape[1])])

    df["batch"] = batch_labels
    df["condition"] = condition_labels
    df["study"] = study_labels
    df["sample_id"] = sample_ids

    return {
        "pca_table": df,
        "variance": variance.tolist()
    }