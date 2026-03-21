from sklearn.decomposition import PCA
import pandas as pd

def run_pca(data, params):

    all_expr = []
    batch_labels = []
    condition_labels = []
    study_labels = []
    sample_ids = []

    for name, dataset in data.items():

        expr = dataset["expression"]
        meta = dataset["metadata"]

        assert len(expr) == len(meta), f"mismatch in {name}"

        all_expr.append(expr)

        batch_labels.extend(meta["batch"].tolist())
        condition_labels.extend(meta["condition"].tolist())
        study_labels.extend(meta["sample_id"].tolist())

    combined = pd.concat(all_expr, axis=0)

    n = params.get("n_components", 10)

    pca = PCA(n_components=n)
    coords = pca.fit_transform(combined)

    variance = pca.explained_variance_ratio_

    pca_df = pd.DataFrame(coords, columns=[f"PC{i+1}" for i in range(coords.shape[1])])

    pca_df["batch"] = batch_labels
    pca_df["condition"] = condition_labels
    pca_df["study"] = study_labels
    pca_df["sample_id"] = sample_ids

    return {
        "pca_table" : pca_df,
        "variance" : variance.tolist()
    }